import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import App from '../App.jsx';

// Mock the page components to avoid complex dependencies
vi.mock('../pages/DashboardPage.jsx', () => ({
  default: () => <div>Dashboard Page</div>,
}));

vi.mock('../pages/ChatPage.jsx', () => ({
  default: () => <div>Chat Page</div>,
}));

vi.mock('../pages/KnowledgeBasePage.jsx', () => ({
  default: () => <div>Knowledge Base Page</div>,
}));

vi.mock('../pages/CyberRangePage.jsx', () => ({
  default: () => <div>Cyber Range Page</div>,
}));

vi.mock('../pages/DashboardPageEnhanced.jsx', () => ({
  default: () => <div>Dashboard Enhanced</div>,
}));

vi.mock('../components/FileUploadComponent.jsx', () => ({
  default: () => <div>File Upload</div>,
}));

vi.mock('../pages/DeadLetterQueueDashboard.jsx', () => ({
  default: () => <div>DLQ Dashboard</div>,
}));

vi.mock('../pages/LabPage.jsx', () => ({
  default: () => <div>Lab Page</div>,
}));

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeInTheDocument();
  });

  it('renders the app bar with title', () => {
    render(<App />);
    expect(screen.getByText('Cyber-Sensei AI')).toBeInTheDocument();
  });

  it('renders navigation menu items', () => {
    render(<App />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Learning Path')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
  });

  it('renders default dashboard page on load', () => {
    render(<App />);
    expect(screen.getByText('Dashboard Page')).toBeInTheDocument();
  });
});
