import React, { useState, useEffect } from 'react';

function getScanHistoryKey() {
  return 'aws-cost-optimizer/scan-results';
}

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    const historyKey = getScanHistoryKey();
    const stored = window.sessionStorage.getItem(historyKey);

    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setReports(Array.isArray(parsed) ? parsed : [parsed]);
      } catch {
        window.sessionStorage.removeItem(historyKey);
      }
    }
  }, []);

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
                  className={`report-item ${selectedReport === index ? 'active' : ''}`}
                  onClick={() => setSelectedReport(index)}
                >
                  <div className="report-item-header">
                    <span className="report-number">Report #{reports.length - index}</span>
                    <span className="report-date">
                      {formatDate(report.timestamp || report.analysis_timestamp)}
                    </span>
                  </div>
                  <div className="report-item-preview">
                    <p className="preview-region">
                      Region: <strong>{report.region || 'N/A'}</strong>
                    </p>
                    <p className="preview-savings">
                      Savings: <strong>₹{formatCurrency(report.savings || report.potential_monthly_savings_inr)}</strong>
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </section>

          {selectedReport !== null && reports[selectedReport] && (
            <section className="panel report-details">
              <div className="report-detail-header">
                <h3>Report #{reports.length - selectedReport}</h3>
                <p className="report-timestamp">
                  {formatDate(
                    reports[selectedReport].timestamp || reports[selectedReport].analysis_timestamp
                  )}
                </p>
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

              <div className="report-details-text">
                <h4>Full Report</h4>
                <pre className="report-json">
                  {JSON.stringify(reports[selectedReport], null, 2)}
                </pre>
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
