import { useState, useEffect, useCallback, useRef } from 'react';
import { api, AgentWebSocket } from './api';
import './index.css';

// ═══════════════════════════════════════════════════
// ONBOARDING WIZARD
// ═══════════════════════════════════════════════════

function OnboardingWizard({ onComplete }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    first_name: '', last_name: '', dob: '', ssn_last4: '',
    phone: '', email: '', zip_code: '76201', location_preference: 'Denton',
    max_distance_miles: 25, slot_priority: 'any',
    has_texas_license: false, has_out_of_state_license: false,
    license_expired: false, license_lost_stolen: false,
    is_commercial: false, id_only: false, needs_permit: false,
    smtp_user: '', smtp_password: '',
  });

  const set = (field) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [field]: val }));
  };

  const analyzeProfile = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await api.analyze({
        has_texas_license: form.has_texas_license,
        has_out_of_state_license: form.has_out_of_state_license,
        license_expired: form.license_expired,
        license_lost_stolen: form.license_lost_stolen,
        is_commercial: form.is_commercial,
        id_only: form.id_only,
        needs_permit: form.needs_permit,
      });
      setAnalysis(result);
      setStep(4);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  const submitProfile = async () => {
    setLoading(true);
    setError('');

    // Format DOB to MM/DD/YYYY if possible
    let cleanDob = form.dob.trim();
    if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(cleanDob)) {
      const portions = cleanDob.split('/');
      cleanDob = portions.map((p, i) => i < 2 ? p.padStart(2, '0') : p).join('/');
    }

    // Clean up data before sending
    const payload = {
      ...form,
      dob: cleanDob,
      max_distance_miles: parseInt(form.max_distance_miles, 10) || 25,
      age: form.age ? parseInt(form.age, 10) : null,
      notify_email: form.email,
      smtp_user: form.smtp_user || form.email,
    };

    try {
      console.log('Submitting profile:', payload);
      const user = await api.createUser(payload);
      console.log('Profile created successfully:', user);
      onComplete(user);
    } catch (e) {
      console.error('Profile creation failed:', e);
      if (e.status === 422) {
        const details = e.data?.detail;
        let msg = 'Validation Error: ';
        if (Array.isArray(details)) {
          msg += details.map(d => {
            const field = d.loc[d.loc.length - 1];
            return `${field}: ${d.msg}`;
          }).join(', ');
        } else {
          msg += 'Please check that all fields (DOB, Zip, SSN) match the required format.';
        }
        setError(msg);
      } else {
        setError(e.message || 'An unexpected error occurred during profile creation.');
      }
    }
    setLoading(false);
  };

  const totalSteps = 4;

  return (
    <div className="wizard-container">
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8 }}>
          🚗 Set Up Your DPS Agent
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Let's get you booked for a DPS appointment automatically
        </p>
      </div>

      {/* Step Progress */}
      <div className="step-progress">
        {[1, 2, 3, 4].map((s, i) => (
          <span key={s}>
            <span className={`step-dot ${step === s ? 'active' : step > s ? 'completed' : ''}`} />
            {i < 3 && <span className={`step-line ${step > s ? 'completed' : ''}`} />}
          </span>
        ))}
      </div>

      {error && (
        <div style={{
          background: 'rgba(255,107,107,0.12)', border: '1px solid rgba(255,107,107,0.3)',
          borderRadius: 8, padding: '10px 16px', marginBottom: 20, color: 'var(--accent-red)',
          fontSize: '0.85rem'
        }}>
          {error}
        </div>
      )}

      {/* Step 1: Personal Info */}
      {step === 1 && (
        <div className="wizard-step card">
          <h3 className="card-title"><span className="emoji">👤</span> Personal Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input className="form-input" placeholder="John" value={form.first_name} onChange={set('first_name')} />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input className="form-input" placeholder="Doe" value={form.last_name} onChange={set('last_name')} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Date of Birth</label>
              <input className="form-input" placeholder="MM/DD/YYYY" value={form.dob} onChange={set('dob')} />
            </div>
            <div className="form-group">
              <label className="form-label">SSN Last 4</label>
              <input className="form-input" placeholder="1234" maxLength={4} value={form.ssn_last4} onChange={set('ssn_last4')} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Phone</label>
              <input className="form-input" placeholder="(555) 123-4567" value={form.phone} onChange={set('phone')} />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input className="form-input" type="email" placeholder="john@gmail.com" value={form.email} onChange={set('email')} />
            </div>
          </div>
          <div className="wizard-actions">
            <div />
            <button className="btn btn-primary" onClick={() => setStep(2)}
              disabled={!form.first_name || !form.last_name || !form.dob || !form.email || !form.ssn_last4 || !form.phone}>
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Location & Preferences */}
      {step === 2 && (
        <div className="wizard-step card">
          <h3 className="card-title"><span className="emoji">📍</span> Location & Preferences</h3>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">ZIP Code</label>
              <input className="form-input" placeholder="76201" value={form.zip_code} onChange={set('zip_code')} />
            </div>
            <div className="form-group">
              <label className="form-label">Preferred Location</label>
              <input className="form-input" placeholder="Denton" value={form.location_preference} onChange={set('location_preference')} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Max Distance (miles)</label>
              <input className="form-input" type="number" min="5" max="100" value={form.max_distance_miles}
                onChange={set('max_distance_miles')} />
            </div>
            <div className="form-group">
              <label className="form-label">Slot Priority</label>
              <select className="form-select" value={form.slot_priority} onChange={set('slot_priority')}>
                <option value="any">Any Available</option>
                <option value="same_day">Same Day Only</option>
                <option value="next_day">Next Day Preferred</option>
                <option value="this_week">This Week</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Email Credentials (for OTP & Notifications)</label>
            <div className="form-row">
              <input className="form-input" placeholder="SMTP Username (Gmail address)" value={form.smtp_user} onChange={set('smtp_user')} />
              <input className="form-input" type="password" placeholder="App Password" value={form.smtp_password} onChange={set('smtp_password')} />
            </div>
          </div>
          <div className="wizard-actions">
            <button className="btn btn-secondary" onClick={() => setStep(1)}>← Back</button>
            <button className="btn btn-primary" onClick={() => setStep(3)}>Next →</button>
          </div>
        </div>
      )}

      {/* Step 3: License Situation */}
      {step === 3 && (
        <div className="wizard-step card">
          <h3 className="card-title"><span className="emoji">🪪</span> Your License Situation</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 20 }}>
            Tell us about your current situation so our AI can recommend the right DPS service.
          </p>
          <div style={{ display: 'grid', gap: 4 }}>
            <div className="form-checkbox">
              <input type="checkbox" id="has_tx" checked={form.has_texas_license} onChange={set('has_texas_license')} />
              <label htmlFor="has_tx">I have an existing Texas driver license</label>
            </div>
            <div className="form-checkbox">
              <input type="checkbox" id="has_oos" checked={form.has_out_of_state_license} onChange={set('has_out_of_state_license')} />
              <label htmlFor="has_oos">I have an out-of-state license</label>
            </div>
            <div className="form-checkbox">
              <input type="checkbox" id="expired" checked={form.license_expired} onChange={set('license_expired')} />
              <label htmlFor="expired">My license is expired or near expiry</label>
            </div>
            <div className="form-checkbox">
              <input type="checkbox" id="lost" checked={form.license_lost_stolen} onChange={set('license_lost_stolen')} />
              <label htmlFor="lost">My license was lost or stolen</label>
            </div>
            <div className="form-checkbox">
              <input type="checkbox" id="commercial" checked={form.is_commercial} onChange={set('is_commercial')} />
              <label htmlFor="commercial">I need a Commercial Driver License (CDL)</label>
            </div>
            <div className="form-checkbox">
              <input type="checkbox" id="id_only" checked={form.id_only} onChange={set('id_only')} />
              <label htmlFor="id_only">I only need a Texas ID card (no driving)</label>
            </div>
            <div className="form-checkbox">
              <input type="checkbox" id="permit" checked={form.needs_permit} onChange={set('needs_permit')} />
              <label htmlFor="permit">I need a Learner Permit (under 18)</label>
            </div>
          </div>
          <div className="wizard-actions">
            <button className="btn btn-secondary" onClick={() => setStep(2)}>← Back</button>
            <button className="btn btn-primary" onClick={analyzeProfile} disabled={loading}>
              {loading ? <><span className="spinner" /> Analyzing...</> : '🧠 Analyze & Recommend'}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: AI Recommendation */}
      {step === 4 && analysis && (
        <div className="wizard-step">
          <div className="ai-card">
            <div className="ai-title">🧠 AI Recommendation</div>
            <div className="ai-service">{analysis.recommended_service}</div>
            <div className="ai-confidence">
              Confidence: {Math.round(analysis.confidence * 100)}% — {analysis.reasoning}
            </div>
            <ul className="ai-tips">
              {analysis.booking_tips?.map((tip, i) => <li key={i}>{tip}</li>)}
            </ul>
          </div>
          <div className="wizard-actions">
            <button className="btn btn-secondary" onClick={() => setStep(3)}>← Change Answers</button>
            <button className="btn btn-primary btn-lg" onClick={submitProfile} disabled={loading}>
              {loading ? <><span className="spinner" /> Creating Profile...</> : '✅ Create Profile & Start'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════

function Dashboard({ user, wsConnected, wsMessages }) {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const loadJobs = useCallback(async () => {
    try {
      const data = await api.getJobs();
      setJobs(data);
      if (data.length > 0 && !selectedJob) {
        setSelectedJob(data[0]);
      }
    } catch { }
  }, [selectedJob]);

  const loadLogs = useCallback(async (jobId) => {
    try {
      const data = await api.getJobLogs(jobId);
      setLogs(data);
    } catch { }
  }, []);

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 10000);
    return () => clearInterval(interval);
  }, [loadJobs]);

  useEffect(() => {
    if (selectedJob) {
      loadLogs(selectedJob.id);
      const interval = setInterval(() => loadLogs(selectedJob.id), 5000);
      return () => clearInterval(interval);
    }
  }, [selectedJob, loadLogs]);

  // Update from WebSocket
  useEffect(() => {
    if (wsMessages.length > 0) {
      const latest = wsMessages[wsMessages.length - 1];
      if (latest.type === 'job_status') {
        loadJobs();
        if (selectedJob?.id === latest.job_id) {
          loadLogs(latest.job_id);
        }
      }
    }
  }, [wsMessages, loadJobs, loadLogs, selectedJob]);

  const startJob = async () => {
    setCreating(true);
    try {
      const job = await api.createJob({
        user_id: user.id,
        check_interval_minutes: 5,
        auto_book: true,
        max_attempts: 100,
      });
      setSelectedJob(job);
      await loadJobs();
    } catch (e) {
      alert('Error: ' + e.message);
    }
    setCreating(false);
  };

  const stopJob = async (jobId) => {
    try {
      await api.stopJob(jobId);
      await loadJobs();
    } catch { }
  };

  const activeJobs = jobs.filter(j => ['running', 'monitoring', 'appointment_found', 'booking', 'otp_waiting'].includes(j.status));
  const totalChecks = jobs.reduce((sum, j) => sum + (j.attempts || 0), 0);
  const bookedCount = jobs.filter(j => j.status === 'booked').length;

  return (
    <div>
      {/* Stats */}
      <div className="stat-cards">
        <div className="stat-card">
          <div className="stat-value">{jobs.length}</div>
          <div className="stat-label">Total Jobs</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{activeJobs.length}</div>
          <div className="stat-label">Active</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totalChecks}</div>
          <div className="stat-label">Checks</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{bookedCount}</div>
          <div className="stat-label">Booked</div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Job Control */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title"><span className="emoji">🤖</span> Agent Control</h3>
            <button className="btn btn-primary btn-sm" onClick={startJob} disabled={creating}>
              {creating ? <><span className="spinner" /> Starting...</> : '▶ Start New Job'}
            </button>
          </div>

          {jobs.length === 0 ? (
            <div className="empty-state">
              <div className="emoji">🤖</div>
              <p>No monitoring jobs yet. Click "Start New Job" to begin automated appointment checking.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {jobs.slice(0, 10).map(job => (
                <div key={job.id} onClick={() => setSelectedJob(job)}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '12px 16px', borderRadius: 8,
                    background: selectedJob?.id === job.id ? 'var(--bg-secondary)' : 'transparent',
                    border: selectedJob?.id === job.id ? '1px solid var(--border-active)' : '1px solid transparent',
                    cursor: 'pointer', transition: 'all 0.15s ease'
                  }}>
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                      {job.service_type?.substring(0, 30)}...
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      Check #{job.attempts || 0} · {job.appointment_location || 'Monitoring...'}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className={`status-badge ${job.status}`}>
                      <span className={`status-dot ${['running', 'monitoring'].includes(job.status) ? 'pulse' : ''}`} />
                      {job.status}
                    </span>
                    {['running', 'monitoring', 'pending'].includes(job.status) && (
                      <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); stopJob(job.id); }}>
                        ■
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Agent Logs */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title"><span className="emoji">📋</span> Agent Activity Log</h3>
            {selectedJob && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Job {selectedJob.id.substring(0, 8)}...
              </span>
            )}
          </div>

          {logs.length === 0 ? (
            <div className="empty-state">
              <div className="emoji">📋</div>
              <p>No logs yet. Start a job to see real-time activity.</p>
            </div>
          ) : (
            <div className="log-list">
              {logs.map((log) => (
                <div key={log.id} className="log-entry">
                  <span className="log-time">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`log-level ${log.level}`}>{log.level}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* User Profile Summary */}
      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <h3 className="card-title"><span className="emoji">👤</span> Your Profile</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, fontSize: '0.85rem' }}>
          <div><span style={{ color: 'var(--text-muted)' }}>Name</span><br />{user.first_name} {user.last_name}</div>
          <div><span style={{ color: 'var(--text-muted)' }}>Email</span><br />{user.email}</div>
          <div><span style={{ color: 'var(--text-muted)' }}>Location</span><br />{user.location_preference} ({user.zip_code})</div>
          <div><span style={{ color: 'var(--text-muted)' }}>Service</span><br />{user.recommended_service || 'Not set'}</div>
        </div>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════
// HISTORY
// ═══════════════════════════════════════════════════

function History() {
  const [bookings, setBookings] = useState([]);
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    api.getBookings().then(setBookings).catch(() => { });
    api.getJobs().then(setJobs).catch(() => { });
  }, []);

  return (
    <div>
      {/* Booking Results */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h3 className="card-title"><span className="emoji">📅</span> Booking Results</h3>
        </div>

        {bookings.length === 0 ? (
          <div className="empty-state">
            <div className="emoji">📅</div>
            <p>No booking results yet. They will appear here once the agent finds appointments.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Date</th>
                <th>Slots</th>
                <th>Status</th>
                <th>Found At</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map(b => (
                <tr key={b.id}>
                  <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{b.location}</td>
                  <td>{b.appointment_date}</td>
                  <td>{b.total_slots}</td>
                  <td>
                    <span className={`status-badge ${b.booking_confirmed ? 'booked' : 'pending'}`}>
                      <span className="status-dot" />
                      {b.booking_confirmed ? 'Confirmed' : 'Found'}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>
                    {new Date(b.checked_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Job History */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title"><span className="emoji">📊</span> Job History</h3>
        </div>

        {jobs.length === 0 ? (
          <div className="empty-state">
            <div className="emoji">📊</div>
            <p>No jobs yet.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Status</th>
                <th>Checks</th>
                <th>Location</th>
                <th>Appointment</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(j => (
                <tr key={j.id}>
                  <td style={{ fontWeight: 500, color: 'var(--text-primary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {j.service_type}
                  </td>
                  <td>
                    <span className={`status-badge ${j.status}`}>
                      <span className={`status-dot ${['running', 'monitoring'].includes(j.status) ? 'pulse' : ''}`} />
                      {j.status}
                    </span>
                  </td>
                  <td>{j.attempts}/{j.max_attempts}</td>
                  <td>{j.appointment_location || '—'}</td>
                  <td>{j.appointment_date || '—'}</td>
                  <td style={{ color: 'var(--text-muted)' }}>
                    {new Date(j.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════

export default function App() {
  const [page, setPage] = useState('onboarding');
  const [user, setUser] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsMessages, setWsMessages] = useState([]);
  const wsRef = useRef(null);

  // Try to load existing user on mount
  useEffect(() => {
    api.getUsers()
      .then(users => {
        if (users.length > 0) {
          setUser(users[0]);
          setPage('dashboard');
        }
      })
      .catch(() => { });
  }, []);

  // WebSocket connection
  useEffect(() => {
    const ws = new AgentWebSocket(
      (data) => setWsMessages((prev) => [...prev.slice(-99), data]),
      () => setWsConnected(true),
      () => setWsConnected(false),
    );
    ws.connect();
    wsRef.current = ws;
    return () => ws.disconnect();
  }, []);

  const handleOnboardingComplete = (newUser) => {
    setUser(newUser);
    setPage('dashboard');
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-logo">
          <div className="icon">🤖</div>
          <div>
            <h1>DPS Agent</h1>
            <div className="subtitle">Intelligent Appointment Booking</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          {user && (
            <nav className="nav-tabs">
              <button className={`nav-tab ${page === 'dashboard' ? 'active' : ''}`}
                onClick={() => setPage('dashboard')}>
                Dashboard
              </button>
              <button className={`nav-tab ${page === 'history' ? 'active' : ''}`}
                onClick={() => setPage('history')}>
                History
              </button>
              <button className={`nav-tab ${page === 'onboarding' ? 'active' : ''}`}
                onClick={() => setPage('onboarding')}>
                Setup
              </button>
            </nav>
          )}

          <div className={`connection-status ${wsConnected ? 'connected' : ''}`}>
            <span className={`connection-dot ${wsConnected ? 'connected' : ''}`} />
            {wsConnected ? 'Live' : 'Offline'}
          </div>
        </div>
      </header>

      {/* Pages */}
      {page === 'onboarding' && (
        <OnboardingWizard onComplete={handleOnboardingComplete} />
      )}
      {page === 'dashboard' && user && (
        <Dashboard user={user} wsConnected={wsConnected} wsMessages={wsMessages} />
      )}
      {page === 'history' && (
        <History />
      )}
    </div>
  );
}
