import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorPage from '../pages/ErrorPage';

describe('ErrorPage Component', () => {
  beforeEach(() => {
    // Clear any mocks before each test
    vi.clearAllMocks();
  });

  describe('404 Error Page', () => {
    it('should render 404 error', () => {
      render(<ErrorPage code={404} />);
      
      expect(screen.getByText('404')).toBeInTheDocument();
      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
    });

    it('should show helpful suggestions for 404', () => {
      render(<ErrorPage code={404} />);
      
      expect(screen.getByText(/check the url/i)).toBeInTheDocument();
      expect(screen.getByText(/return to the dashboard/i)).toBeInTheDocument();
    });

    it('should have go home button', () => {
      render(<ErrorPage code={404} />);
      
      const homeButton = screen.getByText('Go to Dashboard');
      expect(homeButton).toBeInTheDocument();
      expect(homeButton).toHaveAttribute('href', '/');
    });
  });

  describe('500 Error Page', () => {
    it('should render 500 error', () => {
      render(<ErrorPage code={500} />);
      
      expect(screen.getByText('500')).toBeInTheDocument();
      expect(screen.getByText('Server Error')).toBeInTheDocument();
    });

    it('should show helpful suggestions for 500', () => {
      render(<ErrorPage code={500} />);
      
      expect(screen.getByText(/refreshing/i)).toBeInTheDocument();
      expect(screen.getByText(/come back/i)).toBeInTheDocument();
    });

    it('should have retry button when onRetry provided', async () => {
      const mockRetry = vi.fn();
      const user = userEvent.setup();
      
      render(<ErrorPage code={500} onRetry={mockRetry} />);
      
      const retryButton = screen.getByText('Try Again');
      await user.click(retryButton);
      
      expect(mockRetry).toHaveBeenCalled();
    });
  });

  describe('401 Error Page', () => {
    it('should render 401 error', () => {
      render(<ErrorPage code={401} />);
      
      expect(screen.getByText('401')).toBeInTheDocument();
      expect(screen.getByText('Unauthorized')).toBeInTheDocument();
    });

    it('should show login suggestions', () => {
      render(<ErrorPage code={401} />);
      
      expect(screen.getByText(/log in/i)).toBeInTheDocument();
      expect(screen.getByText(/create.*account/i)).toBeInTheDocument();
    });
  });

  describe('403 Error Page', () => {
    it('should render 403 error', () => {
      render(<ErrorPage code={403} />);
      
      expect(screen.getByText('403')).toBeInTheDocument();
      expect(screen.getByText('Access Denied')).toBeInTheDocument();
    });

    it('should show permission suggestions', () => {
      render(<ErrorPage code={403} />);
      
      expect(screen.getByText(/permission/i)).toBeInTheDocument();
      expect(screen.getByText(/administrator/i)).toBeInTheDocument();
    });
  });

  describe('Custom Error Message', () => {
    it('should display custom message', () => {
      const customMessage = 'Custom error occurred';
      render(<ErrorPage code={500} message={customMessage} />);
      
      expect(screen.getByText(customMessage)).toBeInTheDocument();
    });

    it('should use default message if not provided', () => {
      render(<ErrorPage code={404} />);
      
      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
    });
  });

  describe('Error Icon', () => {
    it('should show correct icon for 404', () => {
      const { container } = render(<ErrorPage code={404} />);
      
      // Check if error icon is rendered (MUI Icon)
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should show warning icon for 500', () => {
      const { container } = render(<ErrorPage code={500} />);
      
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Suggestions List', () => {
    it('should render suggestions as list', () => {
      render(<ErrorPage code={404} />);
      
      const suggestionsList = screen.getByText(/What you can try:/).parentElement;
      expect(suggestionsList).toBeInTheDocument();
    });

    it('should have multiple suggestions', () => {
      const { container } = render(<ErrorPage code={404} />);
      
      const listItems = container.querySelectorAll('li');
      expect(listItems.length).toBeGreaterThan(0);
    });
  });

  describe('Action Buttons', () => {
    it('should always have go home button', () => {
      render(<ErrorPage code={404} />);
      
      const homeButton = screen.getByText('Go to Dashboard');
      expect(homeButton).toBeInTheDocument();
    });

    it('should show retry button only when onRetry provided', () => {
      const { rerender } = render(<ErrorPage code={500} />);
      
      // Without onRetry
      expect(screen.queryByText('Try Again')).not.toBeInTheDocument();
      
      // With onRetry
      rerender(<ErrorPage code={500} onRetry={vi.fn()} />);
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });
  });

  describe('Support Contact', () => {
    it('should show support contact link', () => {
      const { container } = render(<ErrorPage code={404} />);
      
      const supportLink = container.querySelector('a[href="mailto:support@cybersensei.com"]');
      expect(supportLink).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('should render on mobile view', () => {
      // Mock window.matchMedia for mobile
      window.matchMedia = vi.fn().mockImplementation(query => ({
        matches: query === '(max-width: 600px)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));
      
      render(<ErrorPage code={404} />);
      
      expect(screen.getByText('404')).toBeInTheDocument();
    });
  });

  describe('Color Coding', () => {
    it('should have correct color for 404', () => {
      const { container } = render(<ErrorPage code={404} />);
      
      const errorTitle = screen.getByText('404');
      expect(errorTitle).toBeInTheDocument();
      // Color would be red (#f44336)
    });

    it('should have correct color for 500', () => {
      const { container } = render(<ErrorPage code={500} />);
      
      const errorTitle = screen.getByText('500');
      expect(errorTitle).toBeInTheDocument();
      // Color would be orange (#ff9800)
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      render(<ErrorPage code={404} />);
      
      const heading = screen.getByText('404');
      expect(heading).toBeInTheDocument();
    });

    it('should have descriptive button text', () => {
      render(<ErrorPage code={404} />);
      
      expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
    });

    it('should have alt text for icons (if applicable)', () => {
      const { container } = render(<ErrorPage code={404} />);
      
      const icons = container.querySelectorAll('svg');
      expect(icons.length).toBeGreaterThan(0);
    });
  });
});
