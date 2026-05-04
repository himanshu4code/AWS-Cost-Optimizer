import React, { useEffect, useState } from 'react';

const OPERATIONS = [
  { id: 'dashboard', label: 'Dashboard', endpoint: '/scan', mode: 'dashboard' },
  { id: 'text', label: 'Text', endpoint: '/scan/text', mode: 'text' },
  { id: 'summary', label: 'Summary', endpoint: '/scan/summary', mode: 'summary' },
  { id: 'json', label: 'JSON', endpoint: '/scan/json', mode: 'json' },
];

function getStorageKey() {
  return 'aws-cost-optimizer/aws-credentials';
}

export default function ScanForm({ apiBaseUrl, onResult }) {
  const [formState, setFormState] = useState({
    region: 'us-east-1',
    days: 7,
    cpuThreshold: 5,
    useMockData: false,
    accessKeyId: '',
    secretAccessKey: '',
    sessionToken: '',
  });
  const [selectedOperation, setSelectedOperation] = useState('dashboard');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const storageKey = getStorageKey();
    const storedValue = window.sessionStorage.getItem(storageKey);

    if (!storedValue) {
      return;
    }

    try {
      const parsed = JSON.parse(storedValue);
      setFormState((current) => ({
        ...current,
        accessKeyId: parsed.accessKeyId || '',
        secretAccessKey: parsed.secretAccessKey || '',
        sessionToken: parsed.sessionToken || '',
        useMockData: false,
      }));
    } catch {
      window.sessionStorage.removeItem(storageKey);
    }
  }, []);

  function persistCredentials(credentials) {
    const storageKey = getStorageKey();

    window.sessionStorage.setItem(storageKey, JSON.stringify(credentials));
  }

  function clearSavedCredentials() {
    const storageKey = getStorageKey();
    window.sessionStorage.removeItem(storageKey);
    setFormState((current) => ({
      ...current,
      accessKeyId: '',
      secretAccessKey: '',
      sessionToken: '',
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      if (!formState.useMockData && (!formState.accessKeyId || !formState.secretAccessKey)) {
        throw new Error('AWS access key ID and secret access key are required for a real scan.');
      }

      const selectedOp = OPERATIONS.find((op) => op.id === selectedOperation) || OPERATIONS[0];
      const endpoint = selectedOp.endpoint;
      const payload = {
        region: formState.region,
        cpu_threshold: Number(formState.cpuThreshold),
        days: Number(formState.days),
        use_mock_data: formState.useMockData,
        aws_credentials: formState.useMockData
          ? null
          : {
              access_key_id: formState.accessKeyId,
              secret_access_key: formState.secretAccessKey,
              session_token: formState.sessionToken || null,
            },
      };

      if (!formState.useMockData) {
        persistCredentials({
          accessKeyId: formState.accessKeyId,
          secretAccessKey: formState.secretAccessKey,
          sessionToken: formState.sessionToken,
        });
      }

      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || 'Unable to generate insights.');
      }

      let result;
      if (selectedOp.mode === 'json') {
        const data = await response.json();
        result = {
          mode: 'json',
          region: formState.region,
          payload: data,
          rendered: JSON.stringify(data, null, 2),
        };
      } else if (selectedOp.mode === 'dashboard') {
        const data = await response.json();
        result = { mode: 'dashboard', region: formState.region, payload: data };
      } else {
        const text = await response.text();
        result = { mode: selectedOp.mode, region: formState.region, rendered: text };
      }

      onResult(result);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function updateField(name, value) {
    setFormState((current) => ({
      ...current,
      [name]: value,
    }));
  }

  const selectedOperationConfig = OPERATIONS.find((op) => op.id === selectedOperation) || OPERATIONS[0];

  return (
    <form onSubmit={handleSubmit} className="scan-form">
      <div className="form-header">
        <h2>Run Scan</h2>
        <p>Configure scan parameters and AWS access to analyze your instances</p>
      </div>

      <div className="operation-strip" role="tablist" aria-label="Scan operations">
        {OPERATIONS.map((operation) => (
          <button
            key={operation.id}
            type="button"
            className={`operation-button ${selectedOperation === operation.id ? 'active' : ''}`}
            onClick={() => setSelectedOperation(operation.id)}
          >
            {operation.label}
          </button>
        ))}
      </div>

      <div className="form-grid">
        <label>
          <span>Region</span>
          <input
            value={formState.region}
            onChange={(event) => updateField('region', event.target.value)}
            placeholder="us-east-1"
          />
        </label>

        <label>
          <span>Days</span>
          <input
            type="number"
            min="1"
            max="30"
            value={formState.days}
            onChange={(event) => updateField('days', event.target.value)}
          />
        </label>

        <label>
          <span>CPU threshold %</span>
          <input
            type="number"
            min="1"
            step="0.1"
            value={formState.cpuThreshold}
            onChange={(event) => updateField('cpuThreshold', event.target.value)}
          />
        </label>

        <label className="toggle">
          <input
            type="checkbox"
            checked={formState.useMockData}
            onChange={(event) => updateField('useMockData', event.target.checked)}
          />
          <span>Use mock data for a demo scan</span>
        </label>
      </div>

      <div className={`credential-grid ${formState.useMockData ? 'disabled' : ''}`}>
        <label>
          <span>AWS access key ID</span>
          <input
            value={formState.accessKeyId}
            onChange={(event) => updateField('accessKeyId', event.target.value)}
            placeholder="AKIA..."
            disabled={formState.useMockData}
          />
        </label>

        <label>
          <span>AWS secret access key</span>
          <input
            value={formState.secretAccessKey}
            onChange={(event) => updateField('secretAccessKey', event.target.value)}
            placeholder="••••••••••••"
            disabled={formState.useMockData}
            type="password"
          />
        </label>

        <label>
          <span>Session token</span>
          <input
            value={formState.sessionToken}
            onChange={(event) => updateField('sessionToken', event.target.value)}
            placeholder="Optional for temporary credentials"
            disabled={formState.useMockData}
          />
        </label>
      </div>

      <div className="credential-actions">
        <button type="button" className="secondary-button" onClick={clearSavedCredentials}>
          Clear saved credentials
        </button>
      </div>

      <div className="form-actions">
        <button type="submit" className="primary-button" disabled={isSubmitting}>
          {isSubmitting ? 'Generating insights...' : `Run ${selectedOperationConfig.label}`}
        </button>
        <span className="form-note">
          Credentials are sent only to the backend for the active request.
        </span>
      </div>

      {error ? <p className="error-banner">{error}</p> : null}
    </form>
  );
}
