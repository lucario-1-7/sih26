import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SocioSolveLogo } from '../src/components/SocioSolveLogo';
import { OfficialLogos } from '../src/components/OfficialLogos';
import { StatsCircles } from '../src/components/StatsCircles';
import { Footer } from '../src/components/Footer';
import { ProblemCard } from '../src/components/ProblemCard';
import { INITIAL_PROBLEMS } from '../src/lib/seedData';

describe('SocioSolve Citizen Components', () => {
  it('renders SocioSolveLogo with both circular image emblems', () => {
    const { container } = render(<SocioSolveLogo />);
    const images = container.querySelectorAll('img');
    expect(images.length).toBe(2);

    const firstImage = images[0];
    const secondImage = images[1];

    expect(decodeURI(firstImage.getAttribute('src') || '')).toContain('1st O.jpeg');
    expect(decodeURI(secondImage.getAttribute('src') || '')).toContain('2nd O.jpeg');
  });

  it('renders OfficialLogos with Government of Jharkhand seal', () => {
    const { container } = render(<OfficialLogos />);
    const jharkhandLogo = container.querySelector('img[alt="Government of Jharkhand"]');
    expect(jharkhandLogo).toBeDefined();
    expect(decodeURI(jharkhandLogo?.getAttribute('src') || '')).toContain('government of jharkand logo.jpeg');
  });

  it('renders StatsCircles with key transformation metrics', () => {
    render(<StatsCircles />);
    expect(screen.getByText('78%')).toBeDefined();
    expect(screen.getByText('124+')).toBeDefined();
    expect(screen.getByText('12')).toBeDefined();
    expect(screen.getByText('9')).toBeDefined();
    expect(screen.getByText('4,820+')).toBeDefined();
  });

  it('renders Footer with citizen helpline 1800-889-2026', () => {
    render(<Footer />);
    expect(screen.getByText('1800-889-2026')).toBeDefined();
    expect(screen.getByText('support@sociosolve.in')).toBeDefined();
  });

  it('renders ProblemCard with title, tracking code, and upvote button', () => {
    const mockProblem = INITIAL_PROBLEMS[0];
    render(<ProblemCard problem={mockProblem} />);

    expect(screen.getByText(mockProblem.title)).toBeDefined();
    expect(screen.getByText(mockProblem.trackingCode)).toBeDefined();
    expect(screen.getByText(mockProblem.category)).toBeDefined();
  });
});
