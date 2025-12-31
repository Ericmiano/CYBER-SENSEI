import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Skeleton,
  Alert,
  Chip,
} from '@mui/material';
import { CheckCircle, Schedule, PlayArrow } from '@mui/icons-material';
import { getUserDashboard } from '../services/api';

const DashboardPage = ({ username }) => {
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
        const errorMessage = err.message || 'Failed to load dashboard data. Please try again.';
        if (import.meta.env.DEV) {
          console.error('Error fetching dashboard:', err);
        }
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchDashboard();
    }
  }, [username]);

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
      case 'mastered':
        return 'success';
      case 'in_progress':
        return 'warning';
      default:
        return 'info';
    }
  };

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (loading || !dashboardData) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Overall Progress
            </Typography>
            <Skeleton variant="rectangular" height={30} sx={{ mb: 1 }} />
            <Skeleton variant="rectangular" height={10} />
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Skeleton variant="text" width="30%" sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={300} />
          </CardContent>
        </Card>
      </Box>
    );
  }

  const { overall, topics } = dashboardData;
  const progressPercentage = overall.progress_percentage || 0;

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Your Learning Dashboard
      </Typography>

      {/* Overall Progress Card */}
      <Card sx={{ mb: 3, backgroundColor: '#1e3a5f' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ color: '#00acc1' }}>
              Overall Progress
            </Typography>
            <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
              {progressPercentage.toFixed(0)}%
            </Typography>
          </Box>

          <Box sx={{ mb: 1 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              {overall.mastered} of {overall.total} Topics Mastered
            </Typography>
            <LinearProgress
              variant="determinate"
              value={progressPercentage}
              sx={{
                height: 12,
                borderRadius: 1,
                backgroundColor: '#333',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: '#00acc1',
                  borderRadius: 1,
                },
              }}
            />
          </Box>

          <Typography variant="caption" sx={{ color: '#999' }}>
            Keep learning! You're making great progress.
          </Typography>
        </CardContent>
      </Card>

      {/* Topic Mastery Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Topic Mastery Breakdown
          </Typography>

          {topics && topics.length > 0 ? (
            <TableContainer component={Paper} sx={{ backgroundColor: '#0a0a0a' }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#1e1e1e' }}>
                    <TableCell sx={{ fontWeight: 'bold', color: '#00acc1' }}>Topic</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 'bold', color: '#00acc1' }}>
                      Mastery Level
                    </TableCell>
                    <TableCell align="center" sx={{ fontWeight: 'bold', color: '#00acc1' }}>
                      Status
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topics.map((topic, index) => (
                    <TableRow
                      key={index}
                      sx={{
                        '&:hover': { backgroundColor: '#1e1e1e' },
                        borderBottom: '1px solid #333',
                      }}
                    >
                      <TableCell sx={{ color: '#d4d4d4' }}>{topic.name}</TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={parseFloat(topic.mastery) || 0}
                            sx={{
                              width: '60%',
                              height: 8,
                              borderRadius: 1,
                              backgroundColor: '#333',
                              mr: 1,
                              '& .MuiLinearProgress-bar': {
                                backgroundColor:
                                  parseFloat(topic.mastery) >= 80
                                    ? '#4caf50'
                                    : parseFloat(topic.mastery) >= 50
                                    ? '#ff9800'
                                    : '#f44336',
                              },
                            }}
                          />
                          <Typography variant="body2" sx={{ width: '40px', textAlign: 'right', color: '#999' }}>
                            {topic.mastery}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          {getStatusIcon(topic.status)}
                          <Chip
                            label={topic.status.replace('_', ' ')}
                            color={getStatusColor(topic.status)}
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography variant="body2" sx={{ color: '#999', p: 2, textAlign: 'center' }}>
              No topics available yet. Start learning!
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardPage;
