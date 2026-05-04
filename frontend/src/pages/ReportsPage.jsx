import React, { useEffect, useMemo, useRef, useState } from 'react';
import ScanResults from '../components/ScanResults';

function getScanHistoryKey() {
  return 'aws-cost-optimizer/scan-results';
}

function normalizeViewMode(mode) {
  if (mode === 'json') {
    return 'json';
  }

  if (mode === 'dashboard') {
    return 'dashboard';
  }

  return 'summary';
}

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedViewMode, setSelectedViewMode] = useState('dashboard');
  const [confirmDeleteIndex, setConfirmDeleteIndex] = useState(null);

  useEffect(() => {
    const historyKey = getScanHistoryKey();
    const stored = window.sessionStorage.getItem(historyKey);

    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        const normalized = Array.isArray(parsed) ? parsed : [parsed];
        setReports(normalized);
        setSelectedReport(normalized.length > 0 ? 0 : null);
        setSelectedViewMode(normalizeViewMode(normalized[0]?.mode || 'dashboard'));
      } catch {
        window.sessionStorage.removeItem(historyKey);
      }
    }
  }, []);

  useEffect(() => {
    if (selectedReport === null || !reports[selectedReport]) {
      return;
    }

    setSelectedViewMode(normalizeViewMode(reports[selectedReport].mode || 'dashboard'));
  }, [reports, selectedReport]);

  function formatDate(timestamp) {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp).toLocaleString();
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      maximumFractionDigits: 0,
      minimumFractionDigits: 0,
    }).format(value ?? 0);
  }

  const selectedReportData = useMemo(() => {
    if (selectedReport === null) {
      return null;
    }

    const report = reports[selectedReport];
    if (!report) {
      return null;
    }

    const payload = report.payload || {};

    if (selectedViewMode === 'dashboard') {
      return {
        mode: 'dashboard',
        region: report.region,
        payload,
      };
    }

    if (selectedViewMode === 'json') {
      return {
        mode: 'json',
        region: report.region,
        rendered: JSON.stringify(
          payload.analysis || payload,
          null,
          2
        ),
      };
    }

    return {
      mode: 'summary',
      region: report.region,
      rendered: payload.summary_card || payload.report_text || 'No summary available.',
    };
  }, [reports, selectedReport, selectedViewMode]);

  function selectReport(index) {
    setSelectedReport(index);
    setSelectedViewMode(normalizeViewMode(reports[index]?.mode || 'dashboard'));
  }

  // refs to report items so we can scroll the selected one into view
  const itemRefs = useRef([]);

  useEffect(() => {
    if (selectedReport === null) return;
    const el = itemRefs.current[selectedReport];
    if (el && el.scrollIntoView) {
      el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [selectedReport]);

  function getPreview(report) {
    const payload = report.payload || {};
    const src = payload.summary_card || payload.report_text || (payload.analysis && JSON.stringify(payload.analysis.summary)) || '';
    if (!src) return '';
    const text = typeof src === 'string' ? src : String(src);

    // Prefer a short human line: skip decorative box-drawing lines and pick the first meaningful line
    const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
    for (const line of lines) {
      // compute ratio of alphanumeric chars to detect decorative lines
      const alphaCount = (line.match(/[A-Za-z0-9]/g) || []).length;
      const ratio = line.length > 0 ? alphaCount / line.length : 0;
      if (ratio > 0.3 && line.length > 3) {
        const cleaned = line.replace(/[\u2500-\u257F\|\*\#\=\-\+<>\[\]\\\/]/g, ' ').replace(/\s+/g, ' ').trim();
        return cleaned.slice(0, 100) + (cleaned.length > 100 ? '…' : '');
      }
    }

    // Fallback: collapse whitespace and truncate
    const collapsed = text.replace(/\s+/g, ' ').trim();
    return collapsed.slice(0, 100) + (collapsed.length > 100 ? '…' : '');
  }

  function handleDownload(index, e) {
    e.stopPropagation();
    const report = reports[index];
    if (!report) return;
    const data = JSON.stringify(report.payload || report, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${index + 1}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function handleDelete(index) {
    const next = reports.slice();
    next.splice(index, 1);
    setReports(next);
    const historyKey = getScanHistoryKey();
    window.sessionStorage.setItem(historyKey, JSON.stringify(next));
    // adjust selected index if needed
    if (selectedReport !== null) {
      if (next.length === 0) setSelectedReport(null);
      else if (index === selectedReport) setSelectedReport(Math.max(0, selectedReport - 1));
      else if (index < selectedReport) setSelectedReport(selectedReport - 1);
    }
    setConfirmDeleteIndex(null);
  }

  function requestDelete(index, e) {
    e.stopPropagation();
    setConfirmDeleteIndex(index);
  }

  function cancelDelete(e) {
    if (e && e.stopPropagation) e.stopPropagation();
    setConfirmDeleteIndex(null);
  }

  return (
    <div className="reports-container">
      <section className="panel reports-header">
        <div className="section-header">
          <p className="eyebrow">Scan History</p>
          <h2>Previous Analysis Reports</h2>
        </div>
        <p className="header-text">
          View and compare your previous cost analysis scans. Reports are saved for the current browser session.
        </p>
      </section>

      {reports.length === 0 ? (
        <section className="empty-state panel">
          <div className="empty-state-content">
            <p className="empty-state-icon">📋</p>
            <h3>No reports yet</h3>
            <p>Run a scan from the Dashboard to generate your first cost analysis report.</p>
          </div>
        </section>
      ) : (
        <div className="reports-layout">
          <section className="panel reports-list">
            <h3 className="list-title">Reports ({reports.length})</h3>
            <div className="report-items">
              {reports.map((report, index) => (
                <button
                  key={index}
                  ref={(el) => (itemRefs.current[index] = el)}
                  type="button"
                  className={`report-item ${selectedReport === index ? 'active' : ''}`}
                  onClick={() => selectReport(index)}
                >
                  <div className="report-card-header">
                    <div className="report-title-block">
                      <div className="report-number">Report #{reports.length - index}</div>
                      <div className="report-mini-date">{formatDate(report.timestamp || report.analysis_timestamp)}</div>
                    </div>
                    <div className="report-actions" role="group" aria-label="Report actions">
                      <button type="button" className="action-button" onClick={(e) => handleDownload(index, e)}>Download</button>
                      <button type="button" className="action-button danger" onClick={(e) => requestDelete(index, e)}>Delete</button>
                    </div>
                  </div>
                  <div className="report-card-region">{report.region || 'N/A'}</div>
                  <div className="report-card-snippet">{getPreview(report)}</div>
                  <div className="report-card-meta">
                    <div className="meta-item">
                      <div className="meta-value">{report.total_instances || 0}</div>
                      <div className="meta-label">Instances</div>
                    </div>
                    <div className="meta-item">
                      <div className="meta-value">₹{formatCurrency(report.potential_monthly_savings_inr || report.savings || 0)}</div>
                      <div className="meta-label">Monthly</div>
                    </div>
                    <div className="meta-item">
                      <div className="meta-value">{(report.mode || 'dashboard').toUpperCase()}</div>
                      <div className="meta-label">View</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </section>

          {selectedReport !== null && reports[selectedReport] && selectedReportData && (
            <section className="panel report-details">
              <div className="report-detail-header">
                <h3>Report #{reports.length - selectedReport}</h3>
                <p className="report-timestamp">
                  {formatDate(
                    reports[selectedReport].timestamp || reports[selectedReport].analysis_timestamp
                  )}
                </p>
              </div>

              <div className="operation-strip report-view-strip" role="tablist" aria-label="Report view format">
                {['dashboard', 'summary', 'json'].map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    className={`operation-button ${selectedViewMode === mode ? 'active' : ''}`}
                    onClick={() => setSelectedViewMode(mode)}
                  >
                    {mode.charAt(0).toUpperCase() + mode.slice(1)}
                  </button>
                ))}
              </div>

              <div className="report-view-scroll">
                <ScanResults result={selectedReportData} />
              </div>

              <div className="report-stats">
                <div className="stat-item">
                  <span className="stat-label">Region</span>
                  <strong className="stat-value">{reports[selectedReport].region || 'N/A'}</strong>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Instances Scanned</span>
                  <strong className="stat-value">
                    {reports[selectedReport].total_instances || 0}
                  </strong>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Monthly Savings Potential</span>
                  <strong className="stat-value">
                    ₹{formatCurrency(reports[selectedReport].potential_monthly_savings_inr)}
                  </strong>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Annual Savings Potential</span>
                  <strong className="stat-value">
                    ₹{formatCurrency(
                      (reports[selectedReport].potential_monthly_savings_inr || 0) * 12
                    )}
                  </strong>
                </div>
              </div>
            </section>
          )}
        </div>
      )}
      {confirmDeleteIndex !== null && (
        <div className="confirm-modal" onClick={cancelDelete}>
          <div className="confirm-dialog" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
            <h4>Delete report?</h4>
            <p>Are you sure you want to delete Report #{reports.length - confirmDeleteIndex}? This action cannot be undone.</p>
            <div className="confirm-actions">
              <button type="button" className="action-button" onClick={(e) => cancelDelete(e)}>Cancel</button>
              <button type="button" className="action-button danger" onClick={() => handleDelete(confirmDeleteIndex)}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Note: Confirmation modal styles are in styles.css
