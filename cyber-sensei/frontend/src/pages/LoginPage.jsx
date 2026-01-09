import React, { useState } from 'react';
import {
  Container, Paper, TextField, Button, Typography, Box, Alert, Tabs, Tab,
  CircularProgress, InputAdornment, IconButton, Link, Card, CardContent
} from '@mui/material';
import { Visibility, VisibilityOff, Info } from '@mui/icons-material';
import { api } from '../services/api';

function LoginPage({ onLoginSuccess }) {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  
  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  
  // Register form
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerFullName, setRegisterFullName] = useState('');

  // Validation functions
  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validatePassword = (password) => password.length >= 8;
  const validateUsername = (username) => /^[a-zA-Z0-9_-]{3,50}$/.test(username);

  const getPasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    return strength;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const newFieldErrors = {};
    
    if (!loginEmail) newFieldErrors.loginEmail = 'Email is required';
    else if (!validateEmail(loginEmail)) newFieldErrors.loginEmail = 'Invalid email format';
    
    if (!loginPassword) newFieldErrors.loginPassword = 'Password is required';

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors);
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/users/login', {
        email: loginEmail,
        password: loginPassword,
      });
      
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      onLoginSuccess(response.data.user);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const newFieldErrors = {};

    if (!registerUsername) newFieldErrors.registerUsername = 'Username is required';
    else if (!validateUsername(registerUsername)) newFieldErrors.registerUsername = 'Username: 3-50 chars, alphanumeric, dash, underscore only';

    if (!registerEmail) newFieldErrors.registerEmail = 'Email is required';
    else if (!validateEmail(registerEmail)) newFieldErrors.registerEmail = 'Invalid email format';

    if (!registerPassword) newFieldErrors.registerPassword = 'Password is required';
    else if (!validatePassword(registerPassword)) newFieldErrors.registerPassword = 'Password must be at least 8 characters';

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors);
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/users/register', {
        username: registerUsername,
        email: registerEmail,
        password: registerPassword,
        full_name: registerFullName || registerUsername,
      });
      
      localStorage.setItem('access_token', response.data.access_token || response.data.token || '');
      localStorage.setItem('user', JSON.stringify(response.data));
      onLoginSuccess(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(registerPassword);
  const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
  const strengthColors = ['#f44336', '#ff9800', '#ffc107', '#8bc34a', '#4caf50'];

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #7c4dff 0%, #00acc1 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      p: 2,
    }}>
      <Container maxWidth="sm">
        <Paper elevation={10} sx={{ p: 4, borderRadius: 3 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, background: 'linear-gradient(135deg, #7c4dff 0%, #00acc1 100%)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Cyber-Sensei
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Master cybersecurity through AI-powered learning
            </Typography>
          </Box>

          {/* Error Alert */}
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {/* Tabs */}
          <Tabs value={tab} onChange={(e, newValue) => {
            setTab(newValue);
            setError('');
            setFieldErrors({});
          }} fullWidth sx={{ mb: 3 }}>
            <Tab label="Login" />
            <Tab label="Register" />
          </Tabs>

          {/* Login Form */}
          {tab === 0 ? (
            <Box component="form" onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={loginEmail}
                onChange={(e) => {
                  setLoginEmail(e.target.value);
                  if (fieldErrors.loginEmail) setFieldErrors({ ...fieldErrors, loginEmail: '' });
                }}
                margin="normal"
                error={!!fieldErrors.loginEmail}
                helperText={fieldErrors.loginEmail}
                disabled={loading}
                autoFocus
              />
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={loginPassword}
                onChange={(e) => {
                  setLoginPassword(e.target.value);
                  if (fieldErrors.loginPassword) setFieldErrors({ ...fieldErrors, loginPassword: '' });
                }}
                margin="normal"
                error={!!fieldErrors.loginPassword}
                helperText={fieldErrors.loginPassword}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" disabled={loading}>
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <Button
                fullWidth
                variant="contained"
                type="submit"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Login'}
              </Button>
              <Box sx={{ textAlign: 'center' }}>
                <Link href="#" underline="hover" sx={{ fontSize: '0.875rem' }}>
                  Forgot password?
                </Link>
              </Box>
            </Box>
          ) : (
            <Box component="form" onSubmit={handleRegister}>
              <TextField
                fullWidth
                label="Username"
                value={registerUsername}
                onChange={(e) => {
                  setRegisterUsername(e.target.value);
                  if (fieldErrors.registerUsername) setFieldErrors({ ...fieldErrors, registerUsername: '' });
                }}
                margin="normal"
                error={!!fieldErrors.registerUsername}
                helperText={fieldErrors.registerUsername || '3-50 characters'}
                disabled={loading}
                autoFocus
              />
              <TextField
                fullWidth
                label="Full Name (optional)"
                value={registerFullName}
                onChange={(e) => setRegisterFullName(e.target.value)}
                margin="normal"
                disabled={loading}
                helperText="Leave blank to use username"
              />
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={registerEmail}
                onChange={(e) => {
                  setRegisterEmail(e.target.value);
                  if (fieldErrors.registerEmail) setFieldErrors({ ...fieldErrors, registerEmail: '' });
                }}
                margin="normal"
                error={!!fieldErrors.registerEmail}
                helperText={fieldErrors.registerEmail}
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={registerPassword}
                onChange={(e) => {
                  setRegisterPassword(e.target.value);
                  if (fieldErrors.registerPassword) setFieldErrors({ ...fieldErrors, registerPassword: '' });
                }}
                margin="normal"
                error={!!fieldErrors.registerPassword}
                helperText={fieldErrors.registerPassword || 'Minimum 8 characters'}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" disabled={loading}>
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              
              {/* Password Strength Indicator */}
              {registerPassword && (
                <Box sx={{ mt: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Box sx={{
                      flex: 1,
                      height: 4,
                      borderRadius: 2,
                      background: `linear-gradient(to right, ${strengthColors.slice(0, passwordStrength + 1).join(', ')})`,
                    }} />
                    <Typography variant="caption" sx={{ color: strengthColors[passwordStrength], fontWeight: 'bold' }}>
                      {strengthLabels[passwordStrength] || 'Weak'}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="textSecondary">
                    Password requirements: Uppercase, lowercase, number, special character
                  </Typography>
                </Box>
              )}

              <Button
                fullWidth
                variant="contained"
                type="submit"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading || !registerPassword || passwordStrength < 2}
              >
                {loading ? <CircularProgress size={24} /> : 'Register'}
              </Button>
            </Box>
          )}

          {/* Help Card */}
          <Card sx={{ mt: 3, backgroundColor: 'rgba(0, 172, 193, 0.1)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                <Info sx={{ fontSize: '1.2rem', mt: 0.5, color: '#00acc1' }} />
                <Box>
                  <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Test Credentials</Typography>
                  <Typography variant="caption" display="block">
                    Email: test@example.com<br/>
                    Password: testpassword123
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Container>
    </Box>
  );
}

export default LoginPage;
