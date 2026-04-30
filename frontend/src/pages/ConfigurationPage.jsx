import React, { useEffect, useState } from 'react';

function getStorageKey() {
  return 'aws-cost-optimizer/aws-credentials';
}

export default function ConfigurationPage() {
  const [credentials, setCredentials] = useState({
    accessKeyId: '',
    secretAccessKey: '',
    sessionToken: '',
  });
  const [rememberCredentials, setRememberCredentials] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const storageKey = getStorageKey();
    const stored = window.sessionStorage.getItem(storageKey);

    if (!stored) {
      return;
    }

    try {
      const parsed = JSON.parse(stored);
      setCredentials({
        accessKeyId: parsed.accessKeyId || '',
        secretAccessKey: parsed.secretAccessKey || '',
        sessionToken: parsed.sessionToken || '',
      });
      setRememberCredentials(true);
    } catch {
      window.sessionStorage.removeItem(storageKey);
    }
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setCredentials((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSave() {
    const storageKey = getStorageKey();

    if (rememberCredentials && credentials.accessKeyId) {
      window.sessionStorage.setItem(storageKey, JSON.stringify(credentials));
      setMessage('Credentials saved in your session');
      setTimeout(() => setMessage(''), 3000);
    }
  }

  function handleClear() {
    const storageKey = getStorageKey();
    window.sessionStorage.removeItem(storageKey);
    setCredentials({
      accessKeyId: '',
      secretAccessKey: '',
      sessionToken: '',
    });
    setMessage('Credentials cleared');
    setTimeout(() => setMessage(''), 3000);
  }

  return (
    <div className="configuration-container">
      <section className="panel config-section">
        <div className="section-header">
          <p className="eyebrow">AWS Credentials</p>
          <h2>Session Configuration</h2>
        </div>

        <div className="config-intro">
          <p>Provide your AWS credentials in your session to scan your infrastructure.</p>
          <ul className="config-checklist">
            <li>✓ Never stored on our servers</li>
            <li>✓ Stored in your session only</li>
            <li>✓ Sent directly to AWS for scanning</li>
            <li>✓ Deleted after each scan completes</li>
          </ul>
        </div>

        <form className="config-form">
          <div className="form-group">
            <label>
              <span className="label-text">AWS Access Key ID</span>
              <span className="label-hint">Starts with AKIA</span>
            </label>
            <input
              type="text"
              name="accessKeyId"
              value={credentials.accessKeyId}
              onChange={handleChange}
              placeholder="AKIA..."
              className="config-input"
            />
          </div>

          <div className="form-group">
            <label>
              <span className="label-text">AWS Secret Access Key</span>
              <span className="label-hint">Keep this confidential</span>
            </label>
            <input
              type="password"
              name="secretAccessKey"
              value={credentials.secretAccessKey}
              onChange={handleChange}
              placeholder="••••••••••••"
              className="config-input"
            />
          </div>

          <div className="form-group">
            <label>
              <span className="label-text">Session Token (Optional)</span>
              <span className="label-hint">For temporary credentials only</span>
            </label>
            <input
              type="password"
              name="sessionToken"
              value={credentials.sessionToken}
              onChange={handleChange}
              placeholder="Leave empty for permanent keys"
              className="config-input"
            />
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={rememberCredentials}
                onChange={(event) => setRememberCredentials(event.target.checked)}
              />
              <span>Remember credentials in this session</span>
            </label>
          </div>

          <div className="form-actions">
            <button type="button" className="primary-button" onClick={handleSave}>
              Save Credentials
            </button>
            <button type="button" className="secondary-button" onClick={handleClear}>
              Clear All
            </button>
          </div>

          {message && <div className="config-message">{message}</div>}
        </form>
      </section>

      <section className="panel config-section security-info">
        <div className="section-header">
          <p className="eyebrow">Security & Privacy</p>
          <h2>How We Protect Your Data</h2>
        </div>

        <div className="info-grid">
          <article className="info-card">
            <h4>🔒 Session Storage</h4>
            <p>Credentials are stored only for the current browser session and are cleared when the session ends.</p>
          </article>

          <article className="info-card">
            <h4>🛡️ Open Access</h4>
            <p>The API is open and accepts AWS credentials directly with each scan request.</p>
          </article>

          <article className="info-card">
            <h4>📊 Per-Request Usage</h4>
            <p>Credentials are used only for the active scan request and are never retained in logs or databases.</p>
          </article>

          <article className="info-card">
            <h4>🔑 Temporary Credentials</h4>
            <p>We recommend using temporary AWS credentials with session tokens for enhanced security.</p>
          </article>
        </div>
      </section>

      <section className="panel config-section aws-setup">
        <div className="section-header">
          <p className="eyebrow">AWS Setup Guide</p>
          <h2>Creating Access Keys</h2>
        </div>

        <div className="setup-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>Go to AWS IAM</h4>
              <p>Sign in to your AWS Console and navigate to IAM → Users</p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>Create or Select a User</h4>
              <p>Select the IAM user account you'll use for this tool</p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>Create Access Keys</h4>
              <p>Go to Security credentials and create a new access key for application use</p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h4>Copy Keys Here</h4>
              <p>Paste your Access Key ID and Secret Access Key into the fields above</p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">5</div>
            <div className="step-content">
              <h4>Set IAM Permissions</h4>
              <p>Ensure the user has EC2 read permissions. Minimum: <code>ec2:DescribeInstances</code></p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
