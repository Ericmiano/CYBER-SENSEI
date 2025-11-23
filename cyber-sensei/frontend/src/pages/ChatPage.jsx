import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card,
  CardContent,
  TextField,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  Paper,
  Skeleton,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import { Send as SendIcon, Refresh as RefreshIcon } from '@mui/icons-material';

const ChatPage = ({ username }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const buildWsUrl = useCallback(() => {
    const envUrl = import.meta.env.VITE_WS_URL;
    if (envUrl) {
      return `${envUrl.replace(/\/$/, '')}/ws/chat/${username}`;
    }
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host =
      window.location.port === '5173'
        ? `${window.location.hostname}:8000`
        : window.location.host;
    return `${protocol}//${host}/ws/chat/${username}`;
  }, [username]);

  const connectWebSocket = useCallback(() => {
    try {
      const wsUrl = buildWsUrl();
      console.log('Connecting to', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        reconnectAttempts.current = 0;
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        setMessages([
          {
            sender: 'Cyber-Sensei',
            text: 'Hello! I am your Cyber-Sensei. How can I help you today?',
            timestamp: new Date(),
          },
        ]);
      };

      ws.current.onmessage = (event) => {
        const receivedMessage = {
          sender: 'Cyber-Sensei',
          text: event.data,
          timestamp: new Date(),
        };
        setMessages((prevMessages) => [...prevMessages, receivedMessage]);
        setLoading(false);
      };

      ws.current.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error. Attempting to reconnect...');
        setLoading(false);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        reconnectAttempts.current += 1;
        const delay = Math.min(3000 * reconnectAttempts.current, 15000);
        reconnectTimeout.current = setTimeout(connectWebSocket, delay);
      };
    } catch (err) {
      console.error('WebSocket connection error:', err);
      setError('Failed to connect. Retrying...');
      reconnectTimeout.current = setTimeout(connectWebSocket, 5000);
    }
  }, [buildWsUrl]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connectWebSocket]);

  const sendMessage = () => {
    if (input.trim() && ws.current && isConnected) {
      const userMessage = {
        sender: 'You',
        text: input,
        timestamp: new Date(),
      };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setLoading(true);
      ws.current.send(input);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetChat = () => {
    setMessages([
      {
        sender: 'Cyber-Sensei',
        text: 'Hello! I am your Cyber-Sensei. How can I help you today?',
        timestamp: new Date(),
      },
    ]);
    setInput('');
    setError(null);
    if (!isConnected) {
      connectWebSocket();
    }
  };

  return (
    <Box sx={{ height: '80vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Learning Path - Chat with Cyber-Sensei
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: isConnected ? '#4caf50' : '#f44336',
              animation: isConnected ? 'pulse 2s infinite' : 'none',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.5 },
                '100%': { opacity: 1 },
              },
            }}
          />
          <Typography variant="body2" sx={{ color: isConnected ? '#4caf50' : '#f44336' }}>
            {isConnected ? 'Connected' : 'Disconnected - Attempting to reconnect...'}
          </Typography>
        </Box>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {/* Chat Messages */}
      <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', mb: 2, overflow: 'hidden' }}>
        <CardContent
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 2,
            backgroundColor: '#0a0a0a',
            display: 'flex',
            flexDirection: 'column',
            gap: 1.5,
          }}
        >
          {messages.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Skeleton variant="circular" width={40} height={40} />
            </Box>
          ) : (
            <>
              <List sx={{ p: 0 }}>
                {messages.map((msg, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      flexDirection: 'column',
                      alignItems: msg.sender === 'You' ? 'flex-end' : 'flex-start',
                      mb: 1.5,
                      p: 0,
                    }}
                  >
                    <Typography variant="caption" sx={{ mb: 0.5, color: '#888' }}>
                      {msg.sender}
                    </Typography>
                    <Paper
                      sx={{
                        p: 1.5,
                        maxWidth: '70%',
                        backgroundColor: msg.sender === 'You' ? '#00acc1' : '#1e1e1e',
                        color: msg.sender === 'You' ? '#000' : '#d4d4d4',
                        borderRadius: 2,
                        wordWrap: 'break-word',
                      }}
                    >
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {msg.text}
                      </Typography>
                      <Typography variant="caption" sx={{ mt: 0.5, display: 'block', opacity: 0.7 }}>
                        {msg.timestamp?.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </ListItem>
                ))}
              </List>
              {loading && (
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <CircularProgress size={20} />
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    Cyber-Sensei is thinking...
                  </Typography>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </CardContent>
      </Card>

      {/* Input Box */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          label="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={!isConnected || loading}
          multiline
          maxRows={4}
          placeholder="Ask Cyber-Sensei for help..."
          sx={{
            '& .MuiOutlinedInput-root': {
              color: '#d4d4d4',
              '& fieldset': {
                borderColor: '#444',
              },
              '&:hover fieldset': {
                borderColor: '#00acc1',
              },
            },
          }}
        />
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          onClick={sendMessage}
          disabled={!isConnected || loading || !input.trim()}
          sx={{ minWidth: '100px' }}
        >
          Send
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={resetChat}
          disabled={loading}
        >
          Reset
        </Button>
      </Box>
    </Box>
  );
};

export default ChatPage;
