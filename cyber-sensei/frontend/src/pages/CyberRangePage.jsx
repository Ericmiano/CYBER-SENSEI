import React, { useEffect, useRef } from 'react';
import { Box, Typography, Paper, Divider } from '@mui/material';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

const CyberRangePage = () => {
  const terminalRef = useRef(null);
  const terminalInstance = useRef(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize XTerm.js terminal
    const term = new Terminal({
      cursorBlink: true,
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
      },
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    // Add welcome message
    term.writeln('Welcome to Cyber-Sensei Lab Environment');
    term.writeln('This is a simulated terminal. Real implementation would connect to a backend.');
    term.writeln('');
    term.write('$ ');

    // Handle terminal input (simulation only - no real backend)
    let inputBuffer = '';
    term.onData((data) => {
      if (data === '\r') {
        // Enter pressed
        term.writeln('');
        // Simulate command echo
        if (inputBuffer.toLowerCase() === 'help') {
          term.writeln('Available commands: help, ls, pwd, echo');
        } else if (inputBuffer) {
          term.writeln(`Command executed: ${inputBuffer}`);
        }
        inputBuffer = '';
        term.write('$ ');
      } else if (data === '\u007F') {
        // Backspace
        if (inputBuffer.length > 0) {
          inputBuffer = inputBuffer.slice(0, -1);
          term.write('\b \b');
        }
      } else {
        // Regular character
        inputBuffer += data;
        term.write(data);
      }
    });

    terminalInstance.current = term;

    // Handle window resize
    const handleResize = () => {
      try {
        fitAddon.fit();
      } catch (e) {
        console.error('Fit error:', e);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      term.dispose();
    };
  }, []);

  return (
    <Box sx={{ display: 'flex', height: '80vh', gap: 2 }}>
      {/* Left side: Instructions */}
      <Paper
        sx={{
          flex: 1,
          p: 2,
          overflow: 'auto',
          backgroundColor: '#1e1e1e',
          color: '#d4d4d4',
        }}
      >
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          Lab Instructions
        </Typography>
        <Divider sx={{ my: 2, backgroundColor: '#444' }} />
        <Typography variant="h6" sx={{ mb: 1 }}>
          Objective: Network Troubleshooting
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.8 }}>
          In this lab, you'll practice basic network troubleshooting commands. Follow the steps
          below to complete the exercise.
        </Typography>

        <Typography variant="h6" sx={{ mb: 1 }}>
          Steps:
        </Typography>
        <ol>
          <li>
            <Typography variant="body2">
              Use the <code>ifconfig</code> or <code>ipconfig</code> command to view network
              interfaces
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Use <code>ping</code> to test connectivity to a remote host
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Use <code>tracert</code> or <code>traceroute</code> to trace the path to a server
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Analyze the output and identify any potential network issues
            </Typography>
          </li>
        </ol>

        <Divider sx={{ my: 2, backgroundColor: '#444' }} />
        <Typography variant="body2" sx={{ color: '#888' }}>
          Expected Duration: 10 minutes
        </Typography>
      </Paper>

      {/* Right side: Terminal */}
      <Paper
        sx={{
          flex: 1,
          p: 1,
          backgroundColor: '#1e1e1e',
          overflow: 'hidden',
          border: '1px solid #444',
        }}
      >
        <div
          ref={terminalRef}
          style={{
            width: '100%',
            height: '100%',
            overflow: 'hidden',
          }}
        />
      </Paper>
    </Box>
  );
};

export default CyberRangePage;
