'use client';

import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';

export const StatsCircles: React.FC = () => {
  const language = useAppStore((state) => state.language);
  const t = translations[language];

  const stats = [
    { value: t.stat1Val, label: t.stat1Label, sub: 'from pilot to deployment', ringProgress: 78 },
    { value: t.stat2Val, label: t.stat2Label, sub: 'academic innovations', ringProgress: 88 },
    { value: t.stat3Val, label: t.stat3Label, sub: 'intellectual property', ringProgress: 60 },
    { value: t.stat4Val, label: t.stat4Label, sub: 'grassroots enterprises', ringProgress: 50 },
    { value: t.stat5Val, label: t.stat5Label, sub: 'districts actively engaged', ringProgress: 75 },
    { value: t.stat6Val, label: t.stat6Label, sub: 'citizens positively impacted', ringProgress: 95 },
  ];

  return (
    <section className="py-16 sm:py-24 px-6 sm:px-12 border-t border-black/10 bg-[#FAF8F5]">
      <div className="max-w-7xl mx-auto text-center">
        
        {/* Section Header */}
        <div className="max-w-3xl mx-auto mb-14 sm:mb-20">
          <h2 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold text-black tracking-tight">
            {t.statsTitle}
          </h2>
          <p className="text-sm sm:text-base text-black/75 mt-3 max-w-2xl mx-auto leading-relaxed">
            {t.statsSub}
          </p>
        </div>

        {/* 6 Circular Statistics Badges with Subtle SVG Arc Ring */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6 sm:gap-8 items-start justify-items-center">
          {stats.map((stat, idx) => (
            <div key={idx} className="flex flex-col items-center max-w-[170px] group">
              
              {/* Circular Badge with Double Concentric Ring & Hover Depth */}
              <div className="relative w-28 h-28 sm:w-32 sm:h-32 md:w-36 md:h-36 rounded-full bg-white border-2 border-black flex items-center justify-center shadow-xs transition-all duration-300 group-hover:scale-105 group-hover:shadow-md">
                
                {/* SVG Progress Ring */}
                <svg className="absolute inset-0 w-full h-full -rotate-90 pointer-events-none p-1">
                  <circle
                    cx="50%"
                    cy="50%"
                    r="44%"
                    stroke="#E5E0D8"
                    strokeWidth="2"
                    fill="none"
                  />
                  <circle
                    cx="50%"
                    cy="50%"
                    r="44%"
                    stroke="#111111"
                    strokeWidth="2.5"
                    strokeDasharray="280"
                    strokeDashoffset={280 - (280 * stat.ringProgress) / 100}
                    strokeLinecap="round"
                    fill="none"
                    className="transition-all duration-1000 ease-out"
                  />
                </svg>

                {/* Inner dashed ring */}
                <div className="absolute inset-2.5 rounded-full border border-dashed border-black/20 pointer-events-none" />
                
                {/* Number inside circle */}
                <div className="relative z-10 flex flex-col items-center justify-center p-2 text-center">
                  <span className="text-xl sm:text-2xl md:text-3xl font-black text-black tracking-tight font-mono">
                    {stat.value}
                  </span>
                </div>
              </div>

              {/* Label below circle */}
              <div className="mt-4 text-center">
                <h3 className="text-xs sm:text-sm font-bold text-black leading-snug">
                  {stat.label}
                </h3>
                <p className="text-[11px] text-black/60 mt-0.5 leading-tight hidden sm:block">
                  {stat.sub}
                </p>
              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
};
