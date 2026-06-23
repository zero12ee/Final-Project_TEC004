import { useState } from 'react';

const Login = ({ onSignIn, onSignUp, authError }) => {
  const [mode, setMode] = useState('sign-in');
  const [form, setForm] = useState({ id: '', email: '', password: '' });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (mode === 'sign-in') {
      if (!form.id || !form.password) return;
      onSignIn({ id: form.id, password: form.password });
    } else {
      if (!form.id || !form.email || !form.password) return;
      onSignUp({ id: form.id, email: form.email, password: form.password });
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="page-header">
          <div>
            <h1>{mode === 'sign-in' ? 'Grade Tracker' : 'Create account'}</h1>
            <p>{mode === 'sign-in' ? 'Sign in to manage your performance.' : 'Start tracking your academic performance.'}</p>
          </div>
        </div>

        <div className="auth-toggle">
          <button type="button" className={mode === 'sign-in' ? 'primary' : 'secondary'} onClick={() => setMode('sign-in')}>
            Sign In
          </button>
          <button type="button" className={mode === 'sign-up' ? 'primary' : 'secondary'} onClick={() => setMode('sign-up')}>
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {authError && <div className="error-msg">{authError}</div>}
          <div className="form-group">
            <label>ID</label>
            <input type="text" name="id" value={form.id} onChange={handleChange} placeholder="Enter user ID" />
          </div>

          {mode === 'sign-up' && (
            <div className="form-group">
              <label>Email</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} placeholder="Enter email" />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <input type="password" name="password" value={form.password} onChange={handleChange} placeholder="Enter password" />
          </div>

          <button type="submit" className="btn-primary">
            {mode === 'sign-in' ? 'Sign In' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
