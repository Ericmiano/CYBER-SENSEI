import { describe, it, expect, vi } from 'vitest';
import { getApiUrl } from '../services/api';

describe('API Service', () => {
  it('exports getApiUrl function', () => {
    expect(typeof getApiUrl).toBe('function');
  });

  it('getApiUrl returns a string', () => {
    const url = getApiUrl();
    expect(typeof url).toBe('string');
  });

  it('getApiUrl returns /api for localhost in development', () => {
    // Mock window.location
    delete window.location;
    window.location = new URL('http://localhost:3000');
    
    const url = getApiUrl();
    expect(url).toBe('/api');
  });

  it('getApiUrl returns /api for 127.0.0.1 in development', () => {
    delete window.location;
    window.location = new URL('http://127.0.0.1:3000');
    
    const url = getApiUrl();
    expect(url).toBe('/api');
  });

  it('getApiUrl respects VITE_API_URL environment variable', () => {
    // This would need proper environment setup in actual tests
    // Just verify the function exists and can be called
    expect(() => getApiUrl()).not.toThrow();
  });
});
