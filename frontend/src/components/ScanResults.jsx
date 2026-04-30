import React from 'react';

const money = new Intl.NumberFormat('en-IN', {
  maximumFractionDigits: 2,
  minimumFractionDigits: 0,
});

function formatInr(value) {
  return `₹${money.format(value ?? 0)}`;
}

function StatCard({ label, value, hint }) {
  return (
    <div className="stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <span className="stat-hint">{hint}</span>
    </div>
  );
}

function getActionClass(action) {
  if (!action) {
    return 'keep';
  }
  if (action.includes('TERMINATE')) {
    return 'terminate';
  }
  if (action.includes('RIGHTSIZE')) {
    return 'rightsize';
  }
  return action.toLowerCase();
}

export default function ScanResults({ result }) {
  if (!result) {
    return null;
  }

  const payload = result.payload || {};
  const summary = payload.summary || {};
  const details = payload.details || {};
  const idleInstances = Array.isArray(details.idle_instances) ? details.idle_instances : [];
  const stoppedAbandoned = Array.isArray(details.stopped_abandoned) ? details.stopped_abandoned : [];
  const rightsizeRecommendations = Array.isArray(details.rightsize_recommendations)
    ? details.rightsize_recommendations
    : [];

  return (
    <section className="results-grid">
      {result.mode === 'dashboard' ? (
        <>
          <article className="panel results-panel">
            <div className="section-header">
              <div>
                <p className="eyebrow">Savings snapshot</p>
                <h3>{payload.message || 'Scan completed'}</h3>
              </div>
              <span className="pill">{payload.user?.email || payload.user?.name || 'Session user'}</span>
            </div>

            <div className="stats-grid">
              <StatCard 
                label="Instances" 
                value={summary.total_instances ?? 0} 
                hint="Total EC2 instances scanned" 
              />
              <StatCard 
                label="Current monthly cost" 
                value={formatInr(summary.total_current_monthly_cost_inr)} 
                hint="Approximate on-demand spend" 
              />
              <StatCard 
                label="Potential monthly savings" 
                value={formatInr(summary.potential_monthly_savings_inr)} 
                hint="Terminate or right-size candidates" 
              />
              <StatCard 
                label="Reduction" 
                value={`${summary.savings_percentage ?? 0}%`} 
                hint="Share of current monthly spend" 
              />
            </div>

            <div className="summary-card">
              <pre>{payload.summary_card || 'No summary available.'}</pre>
            </div>
          </article>

          <article className="panel report-panel">
            <div className="section-header">
              <div>
                <p className="eyebrow">Recommendations</p>
                <h3>Action items</h3>
              </div>
            </div>

            <div className="recommendations">
              {idleInstances.length > 0 && (
                <div className="recommendation-group">
                  <h4>Idle Instances ({idleInstances.length})</h4>
                  <table className="recommendation-table">
                    <thead>
                      <tr>
                        <th>Instance ID</th>
                        <th>Type</th>
                        <th>Monthly Savings</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {idleInstances.map((instance) => (
                        <tr key={instance.InstanceId}>
                          <td className="monospace">{instance.InstanceId}</td>
                          <td>{instance.InstanceType}</td>
                          <td>{formatInr(instance.monthly_savings_inr)}</td>
                          <td>
                            <span className={`action-badge ${getActionClass(instance.action)}`}>
                              {instance.action}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {stoppedAbandoned.length > 0 && (
                <div className="recommendation-group">
                  <h4>Stopped/Abandoned ({stoppedAbandoned.length})</h4>
                  <table className="recommendation-table">
                    <thead>
                      <tr>
                        <th>Instance ID</th>
                        <th>Type</th>
                        <th>Monthly Savings</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stoppedAbandoned.map((instance) => (
                        <tr key={instance.InstanceId}>
                          <td className="monospace">{instance.InstanceId}</td>
                          <td>{instance.InstanceType}</td>
                          <td>{formatInr(instance.monthly_savings_inr)}</td>
                          <td>
                            <span className={`action-badge ${getActionClass(instance.action)}`}>
                              {instance.action}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {rightsizeRecommendations.length > 0 && (
                <div className="recommendation-group">
                  <h4>Right-sizing Opportunities ({rightsizeRecommendations.length})</h4>
                  <table className="recommendation-table">
                    <thead>
                      <tr>
                        <th>Instance ID</th>
                        <th>Current → Recommended</th>
                        <th>Monthly Savings</th>
                        <th>Potential %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rightsizeRecommendations.map((instance) => (
                        <tr key={instance.InstanceId}>
                          <td className="monospace">{instance.InstanceId}</td>
                          <td>{instance.current_type} → {instance.recommended_type}</td>
                          <td>{formatInr(instance.monthly_savings_inr)}</td>
                          <td>{instance.savings_percentage}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {idleInstances.length === 0 && stoppedAbandoned.length === 0 && rightsizeRecommendations.length === 0 && (
                <div className="empty-state panel">
                  <div className="empty-state-content">
                    <p className="empty-state-icon">📭</p>
                    <h3>No recommendations available</h3>
                    <p>The scan completed successfully, but there were no idle or rightsizing candidates in the response.</p>
                  </div>
                </div>
              )}
            </div>
          </article>
        </>
      ) : result.mode === 'json' ? (
        <article className="panel results-panel full-width">
          <div className="section-header">
            <p className="eyebrow">JSON Output</p>
            <h3>Raw Data</h3>
          </div>
          <pre className="json-output">{result.rendered}</pre>
        </article>
      ) : (
        <article className="panel results-panel full-width">
          <div className="section-header">
            <p className="eyebrow">{result.mode.charAt(0).toUpperCase() + result.mode.slice(1)} Report</p>
            <h3>Analysis Results</h3>
          </div>
          <pre className="text-output">{result.rendered}</pre>
        </article>
      )}
    </section>
  );
}
