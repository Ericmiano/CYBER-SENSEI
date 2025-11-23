import React, { useState } from 'react';
import {
  AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemText,
  ListItemIcon, Box, CssBaseline, ThemeProvider, createTheme
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  MenuBook as BookIcon,
  Terminal as TerminalIcon
} from '@mui/icons-material';
import LabPage from './pages/LabPage';
import ErrorBoundary from './components/ErrorBoundary.jsx';

// Import our page components
import DashboardPage from './pages/DashboardPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import KnowledgeBasePage from './pages/KnowledgeBasePage.jsx';
import CyberRangePage from './pages/CyberRangePage.jsx';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00acc1' },
    background: { default: '#121212', paper: '#1e1e1e' },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const username = "testuser"; // Hardcoded for now

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, id: 'dashboard' },
    { text: 'Learning Path', icon: <SchoolIcon />, id: 'chat' },
    { text: 'Knowledge Base', icon: <BookIcon />, id: 'knowledge' },
    { text: 'Cyber Range', icon: <TerminalIcon />, id: 'lab' },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <DashboardPage username={username} />;
      case 'chat': return <ChatPage username={username} />;
      case 'knowledge': return <KnowledgeBasePage />;
      case 'lab': return <CyberRangePage />;
      default: return <DashboardPage username={username} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>
        <Box sx={{ display: 'flex' }}>
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <Typography variant="h6" noWrap component="div">
                Cyber-Sensei AI
              </Typography>
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
    </ThemeProvider>
  );
}

export default App;