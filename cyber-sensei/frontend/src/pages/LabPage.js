import React, { useState, useEffect, useRef } from 'react';
import {
  Card, CardContent, Typography, Box, Button, Alert,
  Grid, Paper, TextField, CircularProgress
} from '@mui/material';
import { PlayArrow, Stop, Terminal } from '@mui/icons-material';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

const LabPage = () => {
  const [labStatus, setLabStatus] = useState('stopped');
  const [labInstructions, setLabInstructions] = useState('');
  const terminalRef = useRef(null);
  const fitAddon = new FitAddon();

  useEffect(() => {
    const term = new XTerm();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    // Placeholder for future WebSocket connection to a backend terminal service
    // const ws = new WebSocket('ws://localhost:8000/ws/terminal');
    // ws.onmessage = (event) => term.write(event.data);
    // term.onData(data => ws.send(data));

    return () => {
      term.dispose();
    };
  }, []);

  const handleStartLab = () => {
    setLabStatus('starting...');
    setLabInstructions('1. Ensure Docker is running.\n2. Run `docker-compose up -d` to start target containers.\n3. Your target IP is 172.17.0.3.');
    // In a real app, this would call an API to start the lab
    setTimeout(() => setLabStatus('running'), 1500);
  };

  const handleStopLab = () => {
    setLabStatus('stopping...');
    setLabInstructions('');
    setTimeout(() => setLabStatus('stopped'), 1500);
  };

  return (
    <Box sx={{ height: '85vh', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Typography variant="h4" gutterBottom>Cyber Range Labs</Typography>

      <Grid container spacing={2} sx={{ flexGrow: 1 }}>
        {/* Left Panel: Instructions */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" gutterBottom>Lab Instructions</Typography>
              <Paper sx={{ p: 2, bgcolor: 'background.default', flexGrow: 1, overflow: 'auto' }}>
                <Typography component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                  {labInstructions || 'Click "Start Lab" to begin.'}
                </Typography>
              </Paper>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={handleStartLab}
                  disabled={labStatus === 'running'}
                  fullWidth
                >
                  Start Lab
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Stop />}
                  onClick={handleStopLab}
                  disabled={labStatus !== 'running'}
                  fullWidth
                  sx={{ mt: 1 }}
                >
                  Stop Lab
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Panel: Terminal */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, p: 1, display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>Interactive Terminal</Typography>
              <Paper sx={{ flexGrow: 1, p: 1, bgcolor: '#000' }}>
                <div
                  ref={terminalRef}
                  style={{ height: '100%', width: '100%' }}
                />
              </Paper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default LabPage;