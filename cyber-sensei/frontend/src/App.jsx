import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemText,
  ListItemIcon, Box, CssBaseline, ThemeProvider, createTheme, Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  MenuBook as BookIcon,
  Terminal as TerminalIcon,
  CloudUpload as UploadIcon,
  BarChart as AnalyticsIcon,
  ErrorOutline as ErrorIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import LabPage from './pages/LabPage';
import ErrorBoundary from './components/ErrorBoundary.jsx';

// Import our page components
import DashboardPage from './pages/DashboardPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import KnowledgeBasePage from './pages/KnowledgeBasePage.jsx';
import CyberRangePage from './pages/CyberRangePage.jsx';
import FileUploadComponent from './components/FileUploadComponent.jsx';
import DeadLetterQueueDashboard from './pages/DeadLetterQueueDashboard.jsx';
import LoginPage from './pages/LoginPage.jsx';
import { UserContext, UserProvider } from './context/UserContext.jsx';

const drawerWidth = 260;

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00acc1',
      light: '#5ddef4',
      dark: '#007c91',
    },
    secondary: {
      main: '#7c4dff',
      light: '#b47cff',
      dark: '#3f1dcb',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#0a0e27',
      paper: '#1a1f3a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b7c3',
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, rgba(122, 76, 255, 0.05) 0%, rgba(0, 172, 193, 0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 24px rgba(0, 172, 193, 0.2)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '0.95rem',
        },
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
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #1a1f3a 0%, #252b4a 100%)',
          borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          transition: 'all 0.3s ease',
          '&:hover': {
            background: 'rgba(0, 172, 193, 0.15)',
            transform: 'translateX(4px)',
          },
          '&.Mui-selected': {
            background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.2) 0%, rgba(0, 172, 193, 0.2) 100%)',
            borderLeft: '3px solid #00acc1',
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

  // Check if user is already authenticated on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
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
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  if (!user) {
    return <LoginPage onLoginSuccess={(userData) => {
      setUser(userData);
      setCurrentPage('dashboard');
    }} />;
  }

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, id: 'dashboard' },
    { text: 'Learning Path', icon: <SchoolIcon />, id: 'chat' },
    { text: 'Knowledge Base', icon: <BookIcon />, id: 'knowledge' },
    { text: 'File Upload', icon: <UploadIcon />, id: 'upload' },
    { text: 'Task Queue', icon: <ErrorIcon />, id: 'dlq' },
    { text: 'Cyber Range', icon: <TerminalIcon />, id: 'lab' },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <DashboardPage username={user.username} />;
      case 'chat': return <ChatPage username={user.username} />;
      case 'knowledge': return <KnowledgeBasePage />;
      case 'upload': return <FileUploadComponent />;
      case 'dlq': return <DeadLetterQueueDashboard />;
      case 'lab': return <CyberRangePage />;
      default: return <DashboardPage username={user.username} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <UserProvider value={{ user, setUser }}>
        <ErrorBoundary>
          <Box sx={{ display: 'flex' }}>
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
              <Toolbar sx={{ justifyContent: 'space-between' }}>
                <Typography variant="h6" noWrap component="div">
                  Cyber-Sensei AI - {user.full_name || user.username}
                </Typography>
                <Button color="inherit" startIcon={<LogoutIcon />} onClick={handleLogout}>
                  Logout
                </Button>
              </Toolbar>
            </AppBar>
            <Drawer
              variant="permanent"
              sx={{
                width: drawerWidth,
                flexShrink: 0,
                [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
              }}
            >
              <Toolbar />
              <Box sx={{ overflow: 'auto' }}>
                <List>
                  {menuItems.map((item) => (
                    <ListItem button key={item.id} onClick={() => setCurrentPage(item.id)}>
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Drawer>
            <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
              <Toolbar />
              {renderPage()}
            </Box>
          </Box>
        </ErrorBoundary>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;