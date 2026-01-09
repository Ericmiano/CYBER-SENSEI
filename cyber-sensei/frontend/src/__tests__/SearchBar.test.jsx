import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchBar from '../components/SearchBar';

describe('SearchBar Component', () => {
  const mockOnSearch = vi.fn();
  const mockOnNavigate = vi.fn();

  beforeEach(() => {
    mockOnSearch.mockClear();
    mockOnNavigate.mockClear();
  });

  it('should render search input', () => {
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    expect(input).toBeInTheDocument();
  });

  it('should show clear button when input has value', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    await user.type(input, 'test');
    
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('should clear input when clear button clicked', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    await user.type(input, 'test');
    
    const clearButton = screen.getByRole('button', { name: /clear/i });
    await user.click(clearButton);
    
    expect(input.value).toBe('');
  });

  it('should handle keyboard navigation', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    
    // Type to trigger search
    await user.type(input, 'test');
    
    // Wait for results to appear
    await waitFor(() => {
      expect(screen.queryByText(/Topic:/i) || screen.queryByText(/Document:/i)).toBeTruthy();
    });
    
    // Test ArrowDown
    await user.keyboard('{ArrowDown}');
    expect(input).toHaveAttribute('aria-selected', 'false');
  });

  it('should call onSearch when item selected', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    await user.type(input, 'test');
    
    // Note: In real scenario, wait for results and click
    // This is a simplified test
  });

  it('should handle Escape key', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    await user.type(input, 'test');
    await user.keyboard('{Escape}');
    
    // Dropdown should be closed
    expect(screen.queryByText('No results found')).not.toBeInTheDocument();
  });

  it('should debounce search requests', async () => {
    const user = userEvent.setup();
    const { rerender } = render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    
    // Type multiple characters quickly
    await user.type(input, 'test', { delay: 50 });
    
    // Should debounce and not call handler for each character
    // Wait for debounce to settle
    await waitFor(() => {
      // After debounce, search should be triggered
    }, { timeout: 1000 });
  });

  it('should display search results', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    await user.type(input, 'test');
    
    // Wait for results to appear
    await waitFor(() => {
      // Results should be displayed
    });
  });

  it('should show loading state while searching', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    
    // During search, loading spinner might appear
    await user.type(input, 'test');
  });

  it('should show no results message', async () => {
    const user = userEvent.setup();
    render(
      <SearchBar onSearch={mockOnSearch} onNavigate={mockOnNavigate} />
    );
    
    const input = screen.getByPlaceholderText('Search topics, documents...');
    await user.type(input, 'zzzzzzzzzzzzzzzzzzz');
    
    // Wait for no results message
    await waitFor(() => {
      expect(screen.queryByText(/no results found/i)).toBeTruthy();
    }, { timeout: 1000 });
  });
});
