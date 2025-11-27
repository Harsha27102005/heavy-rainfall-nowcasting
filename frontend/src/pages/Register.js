import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/RegisterPage.css';

const Register = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    isAdmin: false
  });
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const { register, verifyOtp } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    // Always send is_admin in payload, regardless of form state key
    const userData = {
      email: formData.email,
      username: formData.username,
      password: formData.password,
      is_admin: !!formData.isAdmin // ensure boolean
    };

    const result = await register(userData);

    if (result.success) {
      setOtpSent(true);
      setMessage(result.message || 'OTP sent to your email address.');
    } else {
      // If error is an array (validation error), join messages
      if (Array.isArray(result.error)) {
        setError(result.error.map(e => e.msg || JSON.stringify(e)).join(' '));
      } else {
        setError(result.error);
      }
    }

    setLoading(false);
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await verifyOtp(formData.email, otp);
    if (result.success) {
      // If backend returns a token, store it and redirect
      // verifyOtp now returns { success: true, data: response.data }
      if (result.data && result.data.access_token) {
        // Token is already stored in context, but we can double check or just redirect
        setError('');
        setMessage('Registration complete! Redirecting...');
        setTimeout(() => navigate('/dashboard'), 1000);
      } else {
        // Fallback if token missing but success true (unlikely with current backend)
        setError('Registration successful but auto-login failed. Please login manually.');
        setTimeout(() => navigate('/login'), 2000);
      }
    } else {
      // If error is an array (validation error), join messages
      if (Array.isArray(result.error)) {
        setError(result.error.map(e => e.msg || JSON.stringify(e)).join(' '));
      } else {
        setError(result.error);
      }
    }

    setLoading(false);
  };

  return (
    <div className="register-page">
      <div className="register-form-container">
        <div className="register-form">
          <h2>Register</h2>
          {error && (
            <p className="error-message">
              {Array.isArray(error)
                ? error.map((e, i) =>
                  typeof e === 'object' && e.msg
                    ? <span key={i}>{e.msg}<br /></span>
                    : <span key={i}>{String(e)}<br /></span>
                )
                : typeof error === 'object' && error.msg
                  ? error.msg
                  : String(error)}
            </p>
          )}
          {message && <p className="message">{typeof message === 'object' ? JSON.stringify(message) : message}</p>}

          {!otpSent ? (
            <form onSubmit={handleRegisterSubmit}>
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                required
              />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirmPassword"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />

              <div className="checkbox-container">
                <input
                  type="checkbox"
                  name="isAdmin"
                  checked={formData.isAdmin}
                  onChange={handleChange}
                />
                <label>Register as Admin</label>
              </div>

              <button type="submit" className="register-button" disabled={loading}>
                {loading ? 'Registering...' : 'Register'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifySubmit}>
              <p>An OTP has been sent to {formData.email}. Please enter it below.</p>
              <input
                type="text"
                name="otp"
                placeholder="Enter OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
              />
              <button type="submit" className="register-button" disabled={loading}>
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>
            </form>
          )}

          <div className="extra-links">
            <Link to="/login">Already have an account? Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
