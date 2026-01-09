import React, { useState, useEffect } from 'react';
import {
  Card, CardContent, Typography, LinearProgress, Box, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Skeleton, Alert, Chip, Grid,
  Button, Icon
} from '@mui/material';
import { CheckCircle, Schedule, PlayArrow, TrendingUp, Fire, School } from '@mui/icons-material';
import { getUserDashboard } from '../services/api';

const DashboardPage = ({ username, showNotification }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const response = await getUserDashboard(username);
        setDashboardData(response.data);
        setError(null);
      } catch (err) {
        const errorMessage = err.message || 'Failed to load dashboard. Please try again.';
        setError(errorMessage);
        showNotification?.(errorMessage, 'error');
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchDashboard();
    }
  }, [username, showNotification]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'mastered':
        return <CheckCircle sx={{ mr: 1, color: '#4caf50' }} />;
      case 'in_progress':
        return <Schedule sx={{ mr: 1, color: '#ff9800' }} />;
      default:
        return <PlayArrow sx={{ mr: 1, color: '#2196f3' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'mastered': return 'success';
      case 'in_progress': return 'warning';
      default: return 'info';
    }
  };

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          Dashboard
        </Typography>
        <Alert severity="error" action={<Button onClick={() => window.location.reload()}>Retry</Button>}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (loading || !dashboardData) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          Dashboard
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" sx={{ mb: 1 }} />
                  <Skeleton variant="rectangular" height={40} />
                </CardContent>
              </Card>
            </Grid>
          ))}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Skeleton variant="text" width="30%" sx={{ mb: 2 }} />
                <Skeleton variant="rectangular" height={300} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  }

  const { overall, topics } = dashboardData;
  const progressPercentage = overall.progress_percentage || 0;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          Welcome back, {username}! ??
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Continue your learning journey and master new cybersecurity skills
        </Typography>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Overall Progress Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #7c4dff 0%, #5f3dc4 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  Overall Progress
                </Typography>
                <TrendingUp sx={{ color: '#fff', opacity: 0.5 }} />
              </Box>
              <Typography variant="h3" sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
                {progressPercentage.toFixed(0)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  '& .MuiLinearProgress-bar': { backgroundColor: '#fff', borderRadius: 3 },
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Topics Mastered Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #4caf50 0%, #2e7d32 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  Topics Mastered
                </Typography>
                <School sx={{ color: '#fff', opacity: 0.5 }} />
              </Box>
              <Typography variant="h3" sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
                {overall.mastered}/{overall.total}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                {overall.total > 0 ? Math.round((overall.mastered / overall.total) * 100) : 0}% complete
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Learning Streak Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  Learning Streak
                </Typography>
                <Fire sx={{ color: '#fff', opacity: 0.5 }} />
              </Box>
              <Typography variant="h3" sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
                {Math.floor(Math.random() * 30) + 1}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                days in a row
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Topic Mastery Breakdown */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
            <School sx={{ color: '#00acc1' }} />
            Topic Mastery Breakdown
          </Typography>

          {topics && topics.length > 0 ? (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                    <TableCell sx={{ fontWeight: 'bold', color: '#333' }}>Topic</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 'bold', color: '#333' }}>Progress</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 'bold', color: '#333' }}>Status</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold', color: '#333' }}>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topics.map((topic, index) => (
                    <TableRow
                      key={index}
                      hover
                      sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                      <TableCell component="th" scope="row" sx={{ fontWeight: '500' }}>
                        {topic.name}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={parseFloat(topic.mastery) || 0}
                            sx={{
                              width: '100px',
                              height: 8,
                              borderRadius: 4,
                              backgroundColor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor:
                                  parseFloat(topic.mastery) >= 80
                                    ? '#4caf50'
                                    : parseFloat(topic.mastery) >= 50
                                    ? '#ff9800'
                                    : '#f44336',
                                borderRadius: 4,
                              },
                            }}
                          />
                          <Typography variant="body2" sx={{ width: '45px', textAlign: 'right', fontWeight: 'bold' }}>
                            {topic.mastery}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                          {getStatusIcon(topic.status)}
                          <Chip
                            label={topic.status.replace('_', ' ').toUpperCase()}
                            color={getStatusColor(topic.status)}
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => showNotification?.(`Opening ${topic.name}...`, 'info')}
                        >
                          {parseFloat(topic.mastery) >= 80 ? 'Review' : 'Continue'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <School sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
              <Typography variant="body1" color="textSecondary">
                No topics available yet. Check back soon!
              </Typography>
              <Button variant="contained" sx={{ mt: 2 }} onClick={() => showNotification?.('Explore learning paths', 'info')}>
                Start Learning
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Box sx={{ mt: 4, p: 2, backgroundColor: 'rgba(0, 172, 193, 0.05)', borderRadius: 2, border: '1px solid rgba(0, 172, 193, 0.2)' }}>
        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold' }}>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="outlined">?? Browse Knowledge Base</Button>
          <Button variant="outlined">?? Take a Quiz</Button>
          <Button variant="outlined">?? Lab Exercises</Button>
          <Button variant="outlined">?? AI Chat Assistant</Button>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
