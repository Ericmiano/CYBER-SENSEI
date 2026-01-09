import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SettingsPage from '../pages/SettingsPage';

const theme = createTheme();

const mockUserContext = {
  user: {
    full_name: 'Test User',
    email: 'test@example.com'
  },
  setUser: vi.fn()
};

const mockShowNotification = vi.fn();

describe('SettingsPage Component', () => {
  beforeEach(() => {
    mockShowNotification.mockClear();
    mockUserContext.setUser.mockClear();
  });

  const renderWithTheme = (component) => {
    return render(
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    );
  };

  it('should render settings page', () => {
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    expect(screen.getByText('Settings & Preferences')).toBeInTheDocument();
  });

  it('should have all tabs', () => {
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Application')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Privacy')).toBeInTheDocument();
  });

  it('should render profile tab content', async () => {
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    // Profile tab should be active by default
    expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
    expect(screen.getByText('Change Password')).toBeInTheDocument();
  });

  it('should update full name', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    const fullNameInput = screen.getByLabelText('Full Name');
    await user.clear(fullNameInput);
    await user.type(fullNameInput, 'New Name');
    
    expect(fullNameInput.value).toBe('New Name');
  });

  it('should validate password fields', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    const newPasswordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    
    await user.type(newPasswordInput, 'password123');
    await user.type(confirmPasswordInput, 'password456');
    
    const saveButton = screen.getByText('Save Profile');
    await user.click(saveButton);
    
    // Should show error notification for mismatched passwords
    await waitFor(() => {
      expect(mockShowNotification).toHaveBeenCalledWith(
        expect.stringContaining('match'),
        'warning'
      );
    });
  });

  it('should validate password minimum length', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    const newPasswordInput = screen.getByLabelText('New Password');
    await user.type(newPasswordInput, 'short');
    
    const saveButton = screen.getByText('Save Profile');
    await user.click(saveButton);
    
    // Should show error notification for short password
    await waitFor(() => {
      expect(mockShowNotification).toHaveBeenCalledWith(
        expect.stringContaining('8 characters'),
        'warning'
      );
    });
  });

  it('should toggle dark mode', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    // Click Application tab
    const appTab = screen.getByText('Application');
    await user.click(appTab);
    
    // Find and toggle dark mode switch
    const darkModeSwitch = screen.getByRole('checkbox', { name: /dark mode/i });
    await user.click(darkModeSwitch);
    
    expect(darkModeSwitch).toBeChecked();
  });

  it('should toggle notification settings', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    // Click Notifications tab
    const notifTab = screen.getByText('Notifications');
    await user.click(notifTab);
    
    // Find notification switches
    const inAppNotif = screen.getByRole('checkbox', { name: /in-app notifications/i });
    await user.click(inAppNotif);
    
    expect(inAppNotif).not.toBeChecked();
  });

  it('should toggle privacy settings', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    // Click Privacy tab
    const privacyTab = screen.getByText('Privacy');
    await user.click(privacyTab);
    
    // Find private profile switch
    const privateProfile = screen.getByRole('checkbox', { name: /private profile/i });
    await user.click(privateProfile);
    
    expect(privateProfile).toBeChecked();
  });

  it('should show error message when saving profile fails', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    const fullNameInput = screen.getByLabelText('Full Name');
    await user.clear(fullNameInput);
    
    // Try to save without full name
    const saveButton = screen.getByText('Save Profile');
    await user.click(saveButton);
    
    // Should show validation error
    await waitFor(() => {
      expect(mockShowNotification).toHaveBeenCalled();
    });
  });

  it('should persist settings to localStorage', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    // Click Application tab
    const appTab = screen.getByText('Application');
    await user.click(appTab);
    
    // Toggle dark mode
    const darkModeSwitch = screen.getByRole('checkbox', { name: /dark mode/i });
    await user.click(darkModeSwitch);
    
    // Save settings
    const saveButton = screen.getByText('Save Settings');
    await user.click(saveButton);
    
    // Check localStorage
    expect(localStorage.getItem('theme')).toBe('dark');
  });

  it('should display account status info', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    expect(screen.getByText('Account Status')).toBeInTheDocument();
    expect(screen.getByText('Your account is active and verified.')).toBeInTheDocument();
  });

  it('should disable email field', () => {
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    const emailInput = screen.getByLabelText('Email');
    expect(emailInput).toBeDisabled();
  });

  it('should show password visibility toggle', async () => {
    const user = userEvent.setup();
    renderWithTheme(
      <SettingsPage showNotification={mockShowNotification} />
    );
    
    const visibilityButtons = screen.getAllByRole('button', { name: '' });
    // At least one should be visibility toggle
    expect(visibilityButtons.length).toBeGreaterThan(0);
  });
});
