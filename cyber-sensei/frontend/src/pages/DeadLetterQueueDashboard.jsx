import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  Pagination
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  CheckCircle as RetryIcon
} from '@mui/icons-material';
import './DeadLetterQueueDashboard.css';

const DeadLetterQueueDashboard = () => {
  const [deadLetterQueue, setDeadLetterQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [retryingTaskId, setRetryingTaskId] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const itemsPerPage = 10;

  // Fetch dead letter queue
  const fetchDeadLetterQueue = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `/api/monitoring/dlq?skip=${(page - 1) * itemsPerPage}&limit=${itemsPerPage}`
      );

      if (!response.ok) throw new Error('Failed to fetch dead letter queue');

      const data = await response.json();
      setDeadLetterQueue(data.tasks || []);
      setTotalPages(Math.ceil((data.total || 0) / itemsPerPage));
    } catch (err) {
      console.error('Error fetching DLQ:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 30 seconds
  useEffect(() => {
    fetchDeadLetterQueue();
    const interval = setInterval(fetchDeadLetterQueue, 30000);
    return () => clearInterval(interval);
  }, [page]);

  // Get status color
  const getStatusColor = (status) => {
    const colors = {
      failed: 'error',
      retry_pending: 'warning',
      max_retries_exceeded: 'error',
      awaiting_inspection: 'info'
    };
    return colors[status] || 'default';
  };

  // Get status label
  const getStatusLabel = (status) => {
    const labels = {
      failed: 'Failed',
      retry_pending: 'Retry Pending',
      max_retries_exceeded: 'Max Retries Exceeded',
      awaiting_inspection: 'Awaiting Inspection'
    };
    return labels[status] || status;
  };

  // Retry a task
  const handleRetryTask = async (taskId) => {
    try {
      setRetryingTaskId(taskId);

      const response = await fetch('/api/monitoring/dlq/retry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId })
      });

      if (!response.ok) throw new Error('Failed to retry task');

      // Refresh the list
      await fetchDeadLetterQueue();

      // Show success
      setError(null);
      Alert({
        type: 'success',
        message: 'Task retry initiated'
      });
    } catch (err) {
      console.error('Error retrying task:', err);
      setError(err.message);
    } finally {
      setRetryingTaskId(null);
    }
  };

  // Delete a task from DLQ
  const handleDeleteTask = async (taskId) => {
    try {
      const response = await fetch(`/api/monitoring/dlq/${taskId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete task');

      // Refresh the list
      await fetchDeadLetterQueue();
    } catch (err) {
      console.error('Error deleting task:', err);
      setError(err.message);
    }
  };

  // Show task details
  const handleShowDetails = (task) => {
    setSelectedTask(task);
    setShowDetails(true);
  };

  // Format date
  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  // Format error message
  const formatError = (error) => {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    return JSON.stringify(error, null, 2);
  };

  if (loading && deadLetterQueue.length === 0) {
    return (
      <Box className="dlq-container">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="dlq-container">
      <Box className="dlq-header">
        <h1>Dead Letter Queue Dashboard</h1>
        <Button
          startIcon={<RefreshIcon />}
          onClick={fetchDeadLetterQueue}
          disabled={loading}
          variant="outlined"
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {deadLetterQueue.length === 0 ? (
        <Paper className="dlq-empty">
          <h3>✓ Dead Letter Queue is Empty</h3>
          <p>All tasks are processing successfully!</p>
        </Paper>
      ) : (
        <>
          <TableContainer component={Paper} className="dlq-table-container">
            <Table>
              <TableHead>
                <TableRow className="dlq-table-header">
                  <TableCell>Task ID</TableCell>
                  <TableCell>Task Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Error</TableCell>
                  <TableCell>Failed At</TableCell>
                  <TableCell>Attempts</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {deadLetterQueue.map((task) => (
                  <TableRow key={task.id} className="dlq-table-row">
                    <TableCell className="dlq-task-id">
                      {task.task_id.substring(0, 8)}...
                    </TableCell>
                    <TableCell>{task.task_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(task.status)}
                        color={getStatusColor(task.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell className="dlq-error-cell">
                      <span title={formatError(task.error_message)}>
                        {formatError(task.error_message).substring(0, 50)}...
                      </span>
                    </TableCell>
                    <TableCell>
                      {formatDate(task.failed_at)}
                    </TableCell>
                    <TableCell className="dlq-attempts">
                      {task.retry_count}/{task.max_retries}
                    </TableCell>
                    <TableCell className="dlq-actions">
                      <Button
                        size="small"
                        startIcon={<InfoIcon />}
                        onClick={() => handleShowDetails(task)}
                        variant="text"
                        title="View Details"
                      >
                        Details
                      </Button>
                      {task.status !== 'max_retries_exceeded' && (
                        <Button
                          size="small"
                          startIcon={<RetryIcon />}
                          onClick={() => handleRetryTask(task.task_id)}
                          disabled={retryingTaskId === task.task_id}
                          color="success"
                          variant="text"
                          title="Retry Task"
                        >
                          Retry
                        </Button>
                      )}
                      <Button
                        size="small"
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDeleteTask(task.id)}
                        color="error"
                        variant="text"
                        title="Delete Task"
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Box className="dlq-pagination">
            <Pagination
              count={totalPages}
              page={page}
              onChange={(e, value) => setPage(value)}
              color="primary"
            />
          </Box>
        </>
      )}

      {/* Details Dialog */}
      <Dialog
        open={showDetails}
        onClose={() => setShowDetails(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Task Details</DialogTitle>
        <DialogContent className="dlq-dialog-content">
          {selectedTask && (
            <Box className="dlq-details">
              <div className="dlq-detail-row">
                <strong>Task ID:</strong>
                <code>{selectedTask.task_id}</code>
              </div>
              <div className="dlq-detail-row">
                <strong>Task Name:</strong>
                <span>{selectedTask.task_name}</span>
              </div>
              <div className="dlq-detail-row">
                <strong>Status:</strong>
                <Chip
                  label={getStatusLabel(selectedTask.status)}
                  color={getStatusColor(selectedTask.status)}
                  size="small"
                />
              </div>
              <div className="dlq-detail-row">
                <strong>Error Message:</strong>
                <pre className="dlq-error-message">
                  {formatError(selectedTask.error_message)}
                </pre>
              </div>
              <div className="dlq-detail-row">
                <strong>Failed At:</strong>
                <span>{formatDate(selectedTask.failed_at)}</span>
              </div>
              <div className="dlq-detail-row">
                <strong>Retry Attempts:</strong>
                <span>{selectedTask.retry_count}/{selectedTask.max_retries}</span>
              </div>
              {selectedTask.arguments && (
                <div className="dlq-detail-row">
                  <strong>Arguments:</strong>
                  <pre className="dlq-arguments">
                    {JSON.stringify(selectedTask.arguments, null, 2)}
                  </pre>
                </div>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedTask && selectedTask.status !== 'max_retries_exceeded' && (
            <Button
              onClick={() => {
                handleRetryTask(selectedTask.task_id);
                setShowDetails(false);
              }}
              color="success"
              variant="contained"
              startIcon={<RetryIcon />}
            >
              Retry Task
            </Button>
          )}
          <Button onClick={() => setShowDetails(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DeadLetterQueueDashboard;
