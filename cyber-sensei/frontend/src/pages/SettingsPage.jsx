import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Switch, FormControlLabel,
  Button, TextField, Divider, Alert, CircularProgress, Grid,
  Tabs, Tab, FormHelperText, InputAdornment, IconButton
} from '@mui/material';
import {
  Visibility, VisibilityOff, Lock, Settings as SettingsIcon,
  Bell, Privacy, Person
} from '@mui/icons-material';
import { useUser } from '../context/UserContext';

function SettingsPage({ showNotification }) {
  const { user } = useUser();
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [showPassword, setShowPassword] = useState(false);

  // Profile settings
  const [profile, setProfile] = useState({
    fullName: user?.full_name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // Application settings
  const [settings, setSettings] = useState({
    darkMode: localStorage.getItem('theme') === 'dark',
    notifications: true,
    emailNotifications: true,
    emailUpdates: true,
    emailMarketingEmails: false,
    privateProfile: false,
    showOnlineStatus: true,
  });

  const handleProfileChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleSettingChange = (key) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const saveSettings = async () => {
    setLoading(true);
    try {
      // Simulate API call
      localStorage.setItem('theme', settings.darkMode ? 'dark' : 'light');
      showNotification?.('Settings saved successfully', 'success');
    } catch (error) {
      showNotification?.(error.message || 'Error saving settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async () => {
    if (!profile.fullName.trim()) {
      showNotification?.('Full name is required', 'warning');
      return;
    }

    if (profile.newPassword || profile.currentPassword) {
      if (!profile.currentPassword) {
        showNotification?.('Please enter current password', 'warning');
        return;
      }
      if (!profile.newPassword || profile.newPassword.length < 8) {
        showNotification?.('New password must be at least 8 characters', 'warning');
        return;
      }
      if (profile.newPassword !== profile.confirmPassword) {
        showNotification?.('Passwords do not match', 'warning');
        return;
      }
    }

    setLoading(true);
    try {
      // Simulate API call
      showNotification?.('Profile updated successfully', 'success');
      setProfile(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));
    } catch (error) {
      showNotification?.(error.message || 'Error updating profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Settings & Preferences
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Profile" icon={<Person />} iconPosition="start" />
          <Tab label="Application" icon={<SettingsIcon />} iconPosition="start" />
          <Tab label="Notifications" icon={<Bell />} iconPosition="start" />
          <Tab label="Privacy" icon={<Privacy />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* Profile Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                  <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Profile Information
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <TextField
                  fullWidth
                  label="Full Name"
                  value={profile.fullName}
                  onChange={(e) => handleProfileChange('fullName', e.target.value)}
                  margin="normal"
                  variant="outlined"
                />

                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={profile.email}
                  margin="normal"
                  disabled
                  helperText="Email cannot be changed"
                  variant="outlined"
                />

                <Typography variant="subtitle2" sx={{ mt: 3, mb: 2, fontWeight: 'bold' }}>
                  <Lock sx={{ mr: 1, verticalAlign: 'middle', fontSize: '1rem' }} />
                  Change Password (Optional)
                </Typography>

                <TextField
                  fullWidth
                  label="Current Password"
                  type={showPassword ? 'text' : 'password'}
                  value={profile.currentPassword}
                  onChange={(e) => handleProfileChange('currentPassword', e.target.value)}
                  margin="normal"
                  variant="outlined"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />

                <TextField
                  fullWidth
                  label="New Password"
                  type={showPassword ? 'text' : 'password'}
                  value={profile.newPassword}
                  onChange={(e) => handleProfileChange('newPassword', e.target.value)}
                  margin="normal"
                  variant="outlined"
                  helperText="Minimum 8 characters"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />

                <TextField
                  fullWidth
                  label="Confirm Password"
                  type={showPassword ? 'text' : 'password'}
                  value={profile.confirmPassword}
                  onChange={(e) => handleProfileChange('confirmPassword', e.target.value)}
                  margin="normal"
                  variant="outlined"
                  sx={{ mb: 2 }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />

                <Button
                  variant="contained"
                  onClick={updateProfile}
                  disabled={loading}
                  sx={{ mr: 1 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Save Profile'}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: 'rgba(0, 172, 193, 0.05)' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Account Status
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Your account is active and verified.
                </Typography>
                <Typography variant="caption" display="block">
                  Joined: January 7, 2026
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Application Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
              <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Application Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.darkMode}
                    onChange={() => handleSettingChange('darkMode')}
                  />
                }
                label="Dark Mode"
              />
              <FormHelperText>
                Toggle between dark and light themes
              </FormHelperText>

              <Divider sx={{ my: 1 }} />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.showOnlineStatus}
                    onChange={() => handleSettingChange('showOnlineStatus')}
                  />
                }
                label="Show Online Status"
              />
              <FormHelperText>
                Let other users know when you're online
              </FormHelperText>

              <Button
                variant="contained"
                onClick={saveSettings}
                disabled={loading}
                sx={{ mt: 2, alignSelf: 'flex-start' }}
              >
                {loading ? <CircularProgress size={24} /> : 'Save Settings'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Notifications Tab */}
      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
              <Bell sx={{ mr: 1, verticalAlign: 'middle' }} />
              Notification Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications}
                    onChange={() => handleSettingChange('notifications')}
                  />
                }
                label="In-App Notifications"
              />
              <FormHelperText>
                Receive notifications within the application
              </FormHelperText>

              <Divider sx={{ my: 1 }} />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.emailNotifications}
                    onChange={() => handleSettingChange('emailNotifications')}
                  />
                }
                label="Email Notifications"
              />
              <FormHelperText>
                Receive important updates via email
              </FormHelperText>

              <Divider sx={{ my: 1 }} />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.emailUpdates}
                    onChange={() => handleSettingChange('emailUpdates')}
                  />
                }
                label="Learning Updates"
              />
              <FormHelperText>
                Get notified about new courses and learning paths
              </FormHelperText>

              <Divider sx={{ my: 1 }} />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.emailMarketingEmails}
                    onChange={() => handleSettingChange('emailMarketingEmails')}
                  />
                }
                label="Marketing Emails"
              />
              <FormHelperText>
                Receive promotional offers and announcements
              </FormHelperText>

              <Button
                variant="contained"
                onClick={saveSettings}
                disabled={loading}
                sx={{ mt: 2, alignSelf: 'flex-start' }}
              >
                {loading ? <CircularProgress size={24} /> : 'Save Settings'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Privacy Tab */}
      {tabValue === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
              <Privacy sx={{ mr: 1, verticalAlign: 'middle' }} />
              Privacy & Security
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Alert severity="info" sx={{ mb: 3 }}>
              Your data is encrypted and secure. We follow industry-standard practices to protect your privacy.
            </Alert>

            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Profile Visibility
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={settings.privateProfile}
                  onChange={() => handleSettingChange('privateProfile')}
                />
              }
              label="Private Profile"
            />
            <FormHelperText sx={{ mb: 3 }}>
              Hide your progress and achievements from other users
            </FormHelperText>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
              Data & Account Management
            </Typography>

            <Button variant="outlined" sx={{ mr: 1, mb: 1 }}>
              ?? Download My Data
            </Button>
            <Button variant="outlined" color="warning" sx={{ mb: 1 }}>
              ?? Export Learning History
            </Button>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2, color: '#f44336' }}>
              Danger Zone
            </Typography>

            <Typography variant="body2" color="textSecondary" paragraph>
              Deleting your account is permanent and cannot be undone.
            </Typography>

            <Button variant="outlined" color="error">
              ??? Delete Account
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default SettingsPage;
