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
import DashboardPageEnhanced from './pages/DashboardPageEnhanced.jsx';
import ChatPage from './pages/ChatPage.jsx';
import KnowledgeBasePage from './pages/KnowledgeBasePage.jsx';
import CyberRangePage from './pages/CyberRangePage.jsx';
import FileUploadComponent from './components/FileUploadComponent.jsx';
import DeadLetterQueueDashboard from './pages/DeadLetterQueueDashboard.jsx';
import LoginPage from './pages/LoginPage.jsx';
import { UserContext } from './context/UserContext';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00acc1' },
    background: { default: '#121212', paper: '#1e1e1e' },
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
    { text: 'Enhanced Dashboard', icon: <AnalyticsIcon />, id: 'dashboard-enhanced' },
    { text: 'Learning Path', icon: <SchoolIcon />, id: 'chat' },
    { text: 'Knowledge Base', icon: <BookIcon />, id: 'knowledge' },
    { text: 'File Upload', icon: <UploadIcon />, id: 'upload' },
    { text: 'Task Queue', icon: <ErrorIcon />, id: 'dlq' },
    { text: 'Cyber Range', icon: <TerminalIcon />, id: 'lab' },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <DashboardPage username={user.username} />;
      case 'dashboard-enhanced': return <DashboardPageEnhanced username={user.username} />;
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
      <UserContext.Provider value={{ user, setUser }}>
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
      </UserContext.Provider>
    </ThemeProvider>
  );
}

export default App;