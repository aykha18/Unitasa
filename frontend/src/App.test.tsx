import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Unitasa landing page', () => {
  render(<App />);
  const linkElement = screen.getByText(/Unitasa/i);
  expect(linkElement).toBeInTheDocument();
});
