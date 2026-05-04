import React, { useCallback, useState } from 'react';
import ScanForm from '../components/ScanForm';
import ScanResults from '../components/ScanResults';

function getScanHistoryKey() {
  return 'aws-cost-optimizer/scan-results';
}

export default function DashboardPage({ apiBaseUrl }) {
  const [result, setResult] = useState(null);

  const handleResult = useCallback(
    (scanResult) => {
      setResult(scanResult);

      if (!scanResult) {
        return;
      }

      const key = getScanHistoryKey();
      const saved = window.sessionStorage.getItem(key);
      let history = [];
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          history = Array.isArray(parsed) ? parsed : [];
        } catch {
          history = [];
        }
      }

      const dashboardPayload = scanResult.mode === 'dashboard' ? scanResult.payload?.analysis || {} : {};
      const entry = {
        timestamp: new Date().toISOString(),
        mode: scanResult.mode,
        region: scanResult.region || dashboardPayload.region || scanResult.payload?.region || 'us-east-1',
        total_instances: dashboardPayload?.summary?.total_instances || scanResult.payload?.summary?.total_instances || 0,
        potential_monthly_savings_inr:
          dashboardPayload?.summary?.potential_monthly_savings_inr ||
          scanResult.payload?.summary?.potential_monthly_savings_inr ||
          0,
        payload: scanResult.payload || null,
      };

      history.unshift(entry);
      window.sessionStorage.setItem(key, JSON.stringify(history.slice(0, 25)));
    },
    []
  );

  return (
    <div className="dashboard-container">
      <section className="dashboard-hero panel">
        <div>
          <p className="eyebrow">Scan & Analyze</p>
          <h2>Cloud Cost Analysis Dashboard</h2>
        </div>
        <p className="hero-text">
          Run scans to analyze your EC2 instances, identify savings opportunities, and get actionable recommendations.
        </p>
      </section>

      <section className="panel form-panel">
        <ScanForm apiBaseUrl={apiBaseUrl} onResult={handleResult} />
      </section>

      {result && <ScanResults result={result} />}

      {!result && (
        <section className="empty-state panel">
          <div className="empty-state-content">
            <p className="empty-state-icon">📊</p>
            <h3>No scan results yet</h3>
            <p>Run a scan above to see your cost analysis and savings recommendations.</p>
          </div>
        </section>
      )}
    </div>
  );
}
