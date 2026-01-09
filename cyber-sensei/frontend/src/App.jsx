import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Box, CssBaseline, ThemeProvider, createTheme, Button, IconButton, useMediaQuery,
  Container, Snackbar, Alert
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  MenuBook as BookIcon,
  Terminal as TerminalIcon,
  CloudUpload as UploadIcon,
  BarChart as AnalyticsIcon,
  ErrorOutline as ErrorIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import KnowledgeBasePage from './pages/KnowledgeBasePage.jsx';
import CyberRangePage from './pages/CyberRangePage.jsx';
import FileUploadComponent from './components/FileUploadComponent.jsx';
import DeadLetterQueueDashboard from './pages/DeadLetterQueueDashboard.jsx';
import LoginPage from './pages/LoginPage.jsx';
import SettingsPage from './pages/SettingsPage.jsx';
import ErrorPage from './pages/ErrorPage.jsx';
import SearchBar from './components/SearchBar.jsx';
import { UserContext, UserProvider } from './context/UserContext.jsx';

const drawerWidth = 260;

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#00acc1', light: '#5ddef4', dark: '#007c91' },
    secondary: { main: '#7c4dff', light: '#b47cff', dark: '#3f1dcb' },
    success: { main: '#4caf50' },
    warning: { main: '#ff9800' },
    error: { main: '#f44336' },
    background: { default: '#f5f5f5', paper: '#ffffff' },
    text: { primary: '#212121', secondary: '#666666' },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, rgba(122, 76, 255, 0.05) 0%, rgba(0, 172, 193, 0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0, 0, 0, 0.1)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 12px 24px rgba(0, 172, 193, 0.2)' },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, padding: '10px 24px', fontSize: '0.95rem' },
        contained: {
          background: 'linear-gradient(135deg, #7c4dff 0%, #00acc1 100%)',
          boxShadow: '0 4px 12px rgba(124, 77, 255, 0.4)',
          '&:hover': {
            background: 'linear-gradient(135deg, #6a3eeb 0%, #0099ad 100%)',
            boxShadow: '0 6px 16px rgba(0, 172, 193, 0.5)',
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          transition: 'all 0.3s ease',
          '&:hover': { background: 'rgba(0, 172, 193, 0.15)', transform: 'translateX(4px)' },
          '&.Mui-selected': {
            background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.2) 0%, rgba(0, 172, 193, 0.2) 100%)',
            borderLeft: '3px solid #00acc1',
          },
        },
      },
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00acc1', light: '#5ddef4', dark: '#007c91' },
    secondary: { main: '#7c4dff', light: '#b47cff', dark: '#3f1dcb' },
    success: { main: '#4caf50' },
    warning: { main: '#ff9800' },
    error: { main: '#f44336' },
    background: { default: '#0a0e27', paper: '#1a1f3a' },
    text: { primary: '#ffffff', secondary: '#b0b7c3' },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, rgba(122, 76, 255, 0.05) 0%, rgba(0, 172, 193, 0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 12px 24px rgba(0, 172, 193, 0.2)' },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, padding: '10px 24px', fontSize: '0.95rem' },
        contained: {
          background: 'linear-gradient(135deg, #7c4dff 0%, #00acc1 100%)',
          boxShadow: '0 4px 12px rgba(124, 77, 255, 0.4)',
          '&:hover': {
            background: 'linear-gradient(135deg, #6a3eeb 0%, #0099ad 100%)',
            boxShadow: '0 6px 16px rgba(0, 172, 193, 0.5)',
          },
        },
      },
    },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const isMobile = useMediaQuery('(max-width:600px)');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) setDarkMode(savedTheme === 'dark');
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
      setCurrentPage('dashboard');
    }
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    setCurrentPage('login');
    showNotification('Logged out successfully', 'success');
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleThemeToggle = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  if (!user) {
    return (
      <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        <CssBaseline />
        <LoginPage onLoginSuccess={(userData) => {
          setUser(userData);
          setCurrentPage('dashboard');
          showNotification('Welcome! Logged in successfully', 'success');
        }} />
      </ThemeProvider>
    );
  }

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, id: 'dashboard' },
    { text: 'Learning Path', icon: <SchoolIcon />, id: 'chat' },
    { text: 'Knowledge Base', icon: <BookIcon />, id: 'knowledge' },
    { text: 'File Upload', icon: <UploadIcon />, id: 'upload' },
    { text: 'Analytics', icon: <AnalyticsIcon />, id: 'dlq' },
    { text: 'Cyber Range', icon: <TerminalIcon />, id: 'lab' },
    { text: 'Settings', icon: <SettingsIcon />, id: 'settings' },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <DashboardPage username={user.username} showNotification={showNotification} />;
      case 'chat': return <ChatPage username={user.username} showNotification={showNotification} />;
      case 'knowledge': return <KnowledgeBasePage showNotification={showNotification} />;
      case 'upload': return <FileUploadComponent showNotification={showNotification} />;
      case 'dlq': return <DeadLetterQueueDashboard />;
      case 'lab': return <CyberRangePage showNotification={showNotification} />;
      case 'settings': return <SettingsPage showNotification={showNotification} />;
      case 'error': return <ErrorPage code={404} />;
      default: return <DashboardPage username={user.username} showNotification={showNotification} />;
    }
  };

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <UserProvider value={{ user, setUser }}>
        <ErrorBoundary>
          <Box sx={{ display: 'flex' }}>
            {/* App Bar */}
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
              <Toolbar sx={{ justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {isMobile && (
                    <IconButton color="inherit" onClick={() => setMobileOpen(!mobileOpen)}>
                      <MenuIcon />
                    </IconButton>
                  )}
                  <Typography variant="h6" noWrap>
                    Cyber-Sensei
                  </Typography>
                </Box>
                
                {/* Search Bar - Desktop only */}
                {!isMobile && <SearchBar onSearch={() => {}} onNavigate={(path) => {}} />}
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {isMobile && (
                    <IconButton color="inherit" size="small">
                      <SearchIcon />
                    </IconButton>
                  )}
                  <Typography variant="body2">{user.full_name || user.username}</Typography>
                  <IconButton color="inherit" onClick={handleThemeToggle} size="small">
                    {darkMode ? '??' : '??'}
                  </IconButton>
                  <Button color="inherit" startIcon={<LogoutIcon />} onClick={handleLogout}>
                    {isMobile ? '' : 'Logout'}
                  </Button>
                </Box>
              </Toolbar>
            </AppBar>

            {/* Sidebar Navigation */}
            {!isMobile && (
              <Drawer variant="permanent" sx={{ width: drawerWidth, flexShrink: 0 }}>
                <Toolbar />
                <Box sx={{ overflow: 'auto' }}>
                  <List>
                    {menuItems.map((item) => (
                      <ListItemButton
                        key={item.id}
                        selected={currentPage === item.id}
                        onClick={() => setCurrentPage(item.id)}
                      >
                        <ListItemIcon>{item.icon}</ListItemIcon>
                        <ListItemText primary={item.text} />
                      </ListItemButton>
                    ))}
                  </List>
                </Box>
              </Drawer>
            )}

            {/* Mobile Drawer */}
            {isMobile && (
              <Drawer open={mobileOpen} onClose={() => setMobileOpen(false)}>
                <Box sx={{ width: 250 }}>
                  <Toolbar />
                  <List>
                    {menuItems.map((item) => (
                      <ListItemButton
                        key={item.id}
                        selected={currentPage === item.id}
                        onClick={() => {
                          setCurrentPage(item.id);
                          setMobileOpen(false);
                        }}
                      >
                        <ListItemIcon>{item.icon}</ListItemIcon>
                        <ListItemText primary={item.text} />
                      </ListItemButton>
                    ))}
                  </List>
                </Box>
              </Drawer>
            )}

            {/* Main Content */}
            <Box component="main" sx={{ flexGrow: 1, p: isMobile ? 2 : 3 }}>
              <Toolbar />
              <Container maxWidth="lg">
                {renderPage()}
              </Container>
            </Box>
          </Box>

          {/* Notifications */}
          <Snackbar
            open={notification.open}
            autoHideDuration={6000}
            onClose={() => setNotification({ ...notification, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert onClose={() => setNotification({ ...notification, open: false })} severity={notification.severity}>
              {notification.message}
            </Alert>
          </Snackbar>
        </ErrorBoundary>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;