import React from 'react';
import { useNavigate } from 'react-router-dom';

function StatCard({ label, value, hint }) {
  return (
    <div className="stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <span className="stat-hint">{hint}</span>
    </div>
  );
}

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <section className="hero panel">
        <div className="hero-copy">
          <p className="eyebrow">Enterprise AWS Cost Optimization</p>
          <h1>Reduce EC2 spend by up to 70%</h1>
          <p className="hero-text">
            Identify idle instances, find rightsizing opportunities, and get actionable recommendations to optimize your AWS infrastructure. Manage credentials securely in your session.
          </p>

          <button
            type="button"
            className="primary-button hero-cta"
            onClick={() => navigate('/dashboard')}
          >
            Open Dashboard
          </button>
        </div>

        <div className="hero-metrics">
          <StatCard
            label="Session Management"
            value="Client-Side"
            hint="Credentials managed securely in your session"
          />
          <StatCard
            label="Privacy"
            value="Session Credentials"
            hint="Temporary credentials, never persisted to server"
          />
          <StatCard
            label="Insights"
            value="Real-time Analysis"
            hint="Get savings recommendations instantly"
          />
        </div>
      </section>

      <section className="features-grid">
        <article className="feature-card panel">
          <div className="feature-icon">🔍</div>
          <h3>Instance Discovery</h3>
          <p>Automatically scan and catalog all EC2 instances across your regions with detailed utilization metrics.</p>
        </article>

        <article className="feature-card panel">
          <div className="feature-icon">📊</div>
          <h3>Idle Detection</h3>
          <p>Identify instances with low CPU usage, minimal network traffic, or stopped status for days.</p>
        </article>

        <article className="feature-card panel">
          <div className="feature-icon">💰</div>
          <h3>Savings Calculator</h3>
          <p>Get precise monthly and annual savings estimates based on your specific AWS pricing.</p>
        </article>

        <article className="feature-card panel">
          <div className="feature-icon">⚡</div>
          <h3>Right-sizing</h3>
          <p>Receive recommendations to downsize overprovisioned instances without impacting performance.</p>
        </article>

        <article className="feature-card panel">
          <div className="feature-icon">📈</div>
          <h3>Detailed Reports</h3>
          <p>Export comprehensive reports in text, JSON, or interactive dashboard formats.</p>
        </article>

        <article className="feature-card panel">
          <div className="feature-icon">🔐</div>
          <h3>Secure & Private</h3>
          <p>Your AWS credentials are managed in your session only. Nothing is persisted to the server.</p>
        </article>
      </section>

      <section className="cta-section panel">
        <div className="cta-content">
          <h2>Ready to optimize your AWS costs?</h2>
          <p>Provide your AWS credentials to start identifying savings opportunities across your infrastructure.</p>
        </div>
        <button
          type="button"
          className="primary-button large-button"
          onClick={() => navigate('/dashboard')}
        >
          Go to Dashboard
        </button>
      </section>
    </div>
  );
}
