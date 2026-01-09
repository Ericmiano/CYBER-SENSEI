import React from 'react';
import { Box, Typography, Button, Container, Card, CardContent } from '@mui/material';
import {
  ErrorOutline as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Home as HomeIcon
} from '@mui/icons-material';

function ErrorPage({ code = 404, message = 'Page not found', onRetry = null }) {
  const getErrorDetails = () => {
    switch (code) {
      case 404:
        return {
          title: '404',
          message: 'Page Not Found',
          description: 'Sorry, the page you are looking for does not exist.',
          icon: ErrorIcon,
          color: '#f44336',
          suggestions: [
            'Check the URL and try again',
            'Return to the dashboard',
            'Contact support if the issue persists'
          ]
        };
      case 500:
        return {
          title: '500',
          message: 'Server Error',
          description: 'Something went wrong on our server.',
          icon: WarningIcon,
          color: '#ff9800',
          suggestions: [
            'Try refreshing the page',
            'Come back in a few moments',
            'Report the issue if it continues'
          ]
        };
      case 403:
        return {
          title: '403',
          message: 'Access Denied',
          description: 'You do not have permission to access this resource.',
          icon: InfoIcon,
          color: '#2196f3',
          suggestions: [
            'Check your access permissions',
            'Request access from an administrator',
            'Return to your dashboard'
          ]
        };
      case 401:
        return {
          title: '401',
          message: 'Unauthorized',
          description: 'You need to be logged in to access this page.',
          icon: WarningIcon,
          color: '#f44336',
          suggestions: [
            'Log in to your account',
            'Create a new account if you don\'t have one',
            'Reset your password if you forgot it'
          ]
        };
      default:
        return {
          title: code,
          message: message || 'An Error Occurred',
          description: 'An unexpected error has occurred.',
          icon: ErrorIcon,
          color: '#f44336',
          suggestions: [
            'Try refreshing the page',
            'Return to the dashboard',
            'Contact support if the issue persists'
          ]
        };
    }
  };

  const error = getErrorDetails();
  const Icon = error.icon;

  return (
    <Box sx={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      p: 2
    }}>
      <Container maxWidth="sm">
        <Card sx={{
          textAlign: 'center',
          p: 4,
          backgroundColor: '#fff',
          borderRadius: 2
        }}>
          <CardContent>
            {/* Icon */}
            <Box sx={{ mb: 2 }}>
              <Icon sx={{
                fontSize: 80,
                color: error.color,
                mb: 1
              }} />
            </Box>

            {/* Error Code */}
            <Typography variant="h2" sx={{
              fontWeight: 'bold',
              color: error.color,
              mb: 1,
              lineHeight: 1
            }}>
              {error.title}
            </Typography>

            {/* Error Message */}
            <Typography variant="h5" sx={{
              fontWeight: 600,
              mb: 1,
              color: '#333'
            }}>
              {error.message}
            </Typography>

            {/* Error Description */}
            <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
              {error.description}
            </Typography>

            {/* Suggestions */}
            <Box sx={{
              backgroundColor: '#f5f5f5',
              borderRadius: 1,
              p: 2,
              mb: 3,
              textAlign: 'left'
            }}>
              <Typography variant="subtitle2" sx={{
                fontWeight: 'bold',
                mb: 1,
                color: '#333'
              }}>
                What you can try:
              </Typography>
              <ul style={{
                margin: 0,
                paddingLeft: '20px',
                color: '#666'
              }}>
                {error.suggestions.map((suggestion, idx) => (
                  <li key={idx} style={{ marginBottom: '8px' }}>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<HomeIcon />}
                href="/"
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                Go to Dashboard
              </Button>

              {onRetry && (
                <Button
                  variant="outlined"
                  size="large"
                  onClick={onRetry}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600
                  }}
                >
                  Try Again
                </Button>
              )}
            </Box>

            {/* Support Info */}
            <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid #eee' }}>
              <Typography variant="caption" color="textSecondary">
                Still need help? <a href="mailto:support@cybersensei.com" style={{ color: '#667eea', textDecoration: 'none' }}>Contact Support</a>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}

export default ErrorPage;
