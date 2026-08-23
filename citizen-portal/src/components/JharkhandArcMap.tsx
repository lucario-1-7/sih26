'use client';

import React from 'react';

export const JharkhandArcMap: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`relative select-none pointer-events-none ${className}`}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 600 600"
        className="w-full h-full overflow-visible"
        fill="none"
        stroke="#111111"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <defs>
          {/* Exact Quarter Circle Path with Center at Bottom-Left Corner (0, 600) */}
          <path id="jharkhandQuarterArc" d="M 0 100 A 500 500 0 0 1 500 600" fill="none" />
        </defs>

        {/* Outer Quarter Circle Arc */}
        <path
          d="M 0 80 A 520 520 0 0 1 520 600"
          strokeWidth="2.4"
          stroke="#111111"
          fill="none"
        />

        {/* Inner Concentric Quarter Circle Arc */}
        <path
          d="M 0 100 A 500 500 0 0 1 500 600"
          strokeWidth="1.4"
          stroke="#111111"
          fill="none"
        />

        {/* Curved 'JHARKHAND' Text along the inner quarter arc */}
        <text
          fill="#111111"
          fontSize="24"
          fontWeight="600"
          fontFamily="system-ui, -apple-system, 'Inter', sans-serif"
          letterSpacing="0.26em"
        >
          <textPath href="#jharkhandQuarterArc" startOffset="30%" textAnchor="middle">
            JHARKHAND
          </textPath>
        </text>

        {/* Authentic Smooth Geographical Vector Outline of Jharkhand State */}
        {/* Placed cleanly inside the quarter-circle quadrant */}
        <g transform="translate(45, 230) scale(1.15)">
          <path
            d="
              M 70 50
              C 80 42, 95 45, 110 38
              C 125 30, 140 35, 155 25
              C 170 18, 185 24, 198 15
              C 210 22, 222 18, 230 28
              C 238 40, 248 48, 252 62
              C 255 78, 245 90, 250 105
              C 256 120, 268 132, 260 148
              C 252 162, 240 170, 238 185
              C 235 200, 245 212, 238 225
              C 230 238, 215 242, 202 248
              C 188 255, 175 248, 160 252
              C 145 258, 132 268, 118 262
              C 105 256, 92 260, 80 250
              C 68 240, 58 245, 48 235
              C 38 225, 42 210, 35 198
              C 28 185, 32 172, 38 160
              C 45 148, 40 135, 38 122
              C 35 108, 42 95, 48 82
              C 55 70, 60 60, 70 50
              Z
            "
            stroke="#111111"
            strokeWidth="2.2"
            fill="none"
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Capital Ranchi subtle geographic centroid marker */}
          <circle cx="140" cy="145" r="3.5" fill="#111111" />
          <circle cx="140" cy="145" r="7" stroke="#111111" strokeWidth="1" strokeDasharray="2 2" />
        </g>
      </svg>
    </div>
  );
};
