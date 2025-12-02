import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Tabs,
  Tab,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DocumentIcon,
  VideoLibrary as VideoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as HourglassIcon,
} from '@mui/icons-material';
import {
  addDocument,
  uploadDocumentFile,
  uploadVideo,
  getKnowledgeBaseItems,
} from '../services/api';

const KnowledgeBasePage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [filePath, setFilePath] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingList, setLoadingList] = useState(true);
  const [error, setError] = useState('');
  const username = 'testuser';

  const fetchDocuments = useCallback(async () => {
    try {
      setLoadingList(true);
      const response = await getKnowledgeBaseItems();
      setDocuments(response.data || []);
    } catch (err) {
      console.error('Error loading documents:', err);
      setError('Failed to load knowledge base items.');
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleAddDocument = async (mode = 'auto') => {
    const useSelectedFile = mode === 'file' || (mode === 'auto' && selectedFile);
    const usePath = mode === 'path' || (mode === 'auto' && !useSelectedFile);

    if (useSelectedFile && !selectedFile) {
      setError('Please choose a file to upload.');
      return;
    }
    if (usePath && !filePath.trim()) {
      setError('Please enter a file path.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setStatus('');

      if (useSelectedFile && selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        if (username) formData.append('username', username);
        const response = await uploadDocumentFile(formData);
        setStatus(`Uploaded "${response.data.filename}". Ingestion has started.`);
        setSelectedFile(null);
      } else if (usePath) {
        const response = await addDocument({
          file_path: filePath,
          username,
          display_name: filePath.split(/[\\/]/).pop(),
        });
        setStatus(`Queued "${response.data.filename}" for ingestion.`);
        setFilePath('');
      }

      await fetchDocuments();
    } catch (err) {
      console.error('Error adding document:', err);
      setError(err.message || 'Error adding document. See console for details.');
      setStatus('');
    } finally {
      setLoading(false);
    }
  };

  const handleVideoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      setError('');
      setStatus('Uploading video... This may take a few minutes.');

      const formData = new FormData();
      formData.append('file', file);
      if (username) formData.append('username', username);

      const response = await uploadVideo(formData);
      setStatus(`Video "${response.data.filename}" registered. Transcription pending.`);
      await fetchDocuments();
    } catch (err) {
      console.error('Error uploading video:', err);
      setError('Error processing video. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (docStatus) => {
    switch (docStatus) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'registered':
      case 'processing':
      case 'pending_transcription':
      case 'transcribing':
        return <HourglassIcon sx={{ color: '#ff9800', animation: 'spin 2s linear infinite' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return null;
    }
  };

  const getStatusLabel = (docStatus) => {
    switch (docStatus) {
      case 'completed':
        return 'Completed';
      case 'registered':
        return 'Registered';
      case 'processing':
        return 'Processing';
      case 'pending_transcription':
        return 'Awaiting Transcript';
      case 'transcribing':
        return 'Transcribing';
      case 'failed':
        return 'Failed';
      default:
        return docStatus ? docStatus.replace('_', ' ') : 'Unknown';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        My Knowledge Base
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {status && <Alert severity="success" sx={{ mb: 2 }}>{status}</Alert>}

      <Card>
        <CardContent>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 2 }}>
            <Tab label="Text & PDFs" icon={<DocumentIcon />} iconPosition="start" />
            <Tab label="Videos" icon={<VideoIcon />} iconPosition="start" />
            <Tab label="Uploaded Documents" icon={<CloudUploadIcon />} iconPosition="start" />
          </Tabs>

          <Divider sx={{ mb: 2 }} />

          {/* Text & PDFs Tab */}
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Add Text or PDF Documents
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, color: '#999' }}>
                Upload a local file or reference a document already placed in the shared folder.
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    label="Enter file path (e.g., /path/to/notes.txt)"
                    value={filePath}
                    onChange={(e) => setFilePath(e.target.value)}
                    placeholder="Example: C:/documents/security-notes.pdf"
                    disabled={loading}
                  />
                  <Button
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                    onClick={() => handleAddDocument('path')}
                    disabled={loading}
                    sx={{ minWidth: '150px' }}
                  >
                    {loading ? 'Adding...' : 'Add Document'}
                  </Button>
                </Box>
                <Divider textAlign="left">or upload a file</Divider>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                  <input
                    type="file"
                    accept=".txt,.pdf"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    disabled={loading}
                    style={{ maxWidth: '260px' }}
                  />
                  {selectedFile && (
                    <Chip
                      label={selectedFile.name}
                      onDelete={() => setSelectedFile(null)}
                      sx={{ backgroundColor: '#1e1e1e' }}
                    />
                  )}
                </Box>
                <Button
                  variant="outlined"
                  onClick={() => handleAddDocument('file')}
                  disabled={loading || !selectedFile}
                  sx={{ alignSelf: 'flex-start' }}
                >
                  {loading ? 'Uploading...' : 'Upload Selected File'}
                </Button>
              </Box>
            </Box>
          )}

          {/* Videos Tab */}
          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Upload Video Files
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, color: '#999' }}>
                Upload a video file. It will be transcribed in the background. Processing may take a few minutes
                depending on video length.
              </Typography>
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoUpload}
                disabled={loading}
                style={{ display: 'block', marginBottom: '1rem' }}
              />
              {loading && (
                <Box>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Processing video...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}
            </Box>
          )}

          {/* Uploaded Documents Tab */}
          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Your Learning Materials
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, gap: 2, flexWrap: 'wrap' }}>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Track ingestion status and transcripts for all uploaded materials.
                </Typography>
                <Button variant="outlined" size="small" onClick={fetchDocuments} disabled={loadingList}>
                  Refresh
                </Button>
              </Box>
              {loadingList ? (
                <Box sx={{ py: 4 }}>
                  <LinearProgress />
                </Box>
              ) : documents.length === 0 ? (
                <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 4 }}>
                  No documents uploaded yet. Start by adding documents or videos!
                </Typography>
              ) : (
                <List>
                  {documents.map((doc) => (
                    <Box key={doc.id}>
                      <ListItem alignItems="flex-start">
                        <ListItemIcon>{getStatusIcon(doc.status)}</ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                              <Typography sx={{ fontWeight: 'bold', color: '#d4d4d4' }}>
                                {doc.filename}
                              </Typography>
                              <Chip
                                label={doc.doc_type === 'video' ? 'Video' : 'Document'}
                                size="small"
                                variant="outlined"
                              />
                              <Chip label={getStatusLabel(doc.status)} size="small" />
                            </Box>
                          }
                          secondary={
                            <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                              <Typography variant="caption" sx={{ color: '#999' }}>
                                Added: {doc.created_at ? new Date(doc.created_at).toLocaleString() : 'N/A'}
                              </Typography>
                              {doc.notes && (
                                <Typography variant="body2" sx={{ color: '#b0bec5' }}>
                                  {doc.notes}
                                </Typography>
                              )}
                              {doc.transcript && doc.doc_type === 'video' && (
                                <Typography variant="body2" sx={{ color: '#b0bec5' }}>
                                  Transcript: {doc.transcript}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      <Divider />
                    </Box>
                  ))}
                </List>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default KnowledgeBasePage;
