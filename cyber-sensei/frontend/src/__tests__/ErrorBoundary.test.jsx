import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import ErrorBoundary from '../components/ErrorBoundary.jsx';

// Mock component for testing
const TestComponent = () => <div>Test Component</div>;

const ThrowingComponent = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>Normal Component</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // Suppress console.error for error boundary tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <TestComponent />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    
    // Check for error message - error boundary renders multiple elements with error text
    const errorElements = screen.queryAllByText(/error|something went wrong/i);
    expect(errorElements.length).toBeGreaterThan(0);
  });

  it('catches errors in nested components', () => {
    const NestedThrowingComponent = () => (
      <div>
        <ThrowingComponent shouldThrow={true} />
      </div>
    );

    render(
      <ErrorBoundary>
        <NestedThrowingComponent />
      </ErrorBoundary>
    );
    
    // Verify error boundary handled it (no crash)
    expect(document.body).toBeInTheDocument();
  });
});
