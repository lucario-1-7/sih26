'use client';

import React from 'react';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';

export const OfficialLogos: React.FC<{ className?: string }> = ({ className = '' }) => {
  const language = useAppStore((state) => state.language);
  const t = translations[language];

  return (
    <div className={`flex items-center gap-3 sm:gap-4 select-none ${className}`}>
      
      {/* 1. Official Government of Jharkhand Seal & Credential */}
      <div className="flex items-center gap-2 group cursor-pointer">
        <div className="relative w-8 h-8 sm:w-9 sm:h-9 rounded-full overflow-hidden flex-shrink-0 border border-black/30 shadow-2xs transition-transform duration-300 group-hover:scale-105 group-hover:shadow-sm bg-white">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/government of jharkand logo.jpeg"
            alt="Government of Jharkhand"
            className="w-full h-full object-cover grayscale contrast-125 group-hover:grayscale-0 transition-all duration-300"
          />
          {/* Subtle live radar ping dot */}
          <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-600 border border-white" />
        </div>

        <div className="flex flex-col text-left leading-none">
          <span className="font-bold text-[11px] sm:text-xs text-black tracking-tight group-hover:text-black/80 transition-colors">
            {t.jharkhandGovTitle}
          </span>
          <span className="text-[9px] sm:text-[10px] text-black font-normal opacity-75 mt-0.5 max-w-[130px] leading-tight">
            {t.jharkhandGovSub}
          </span>
        </div>
      </div>

      {/* Thin Divider */}
      <div className="h-6 w-px bg-black/20 hidden sm:block" />

      {/* 2. AICTE Logo */}
      <div className="hidden sm:flex items-center gap-1.5 group cursor-pointer">
        <div className="w-7 h-7 sm:w-8 sm:h-8 flex-shrink-0 transition-transform duration-300 group-hover:scale-105">
          <svg
            viewBox="0 0 100 100"
            className="w-full h-full"
            fill="none"
            stroke="#111111"
            strokeWidth="2.5"
          >
            <circle cx="50" cy="50" r="42" strokeWidth="2.5" strokeDasharray="5 3" />
            <circle cx="50" cy="50" r="30" strokeWidth="2" fill="#111111" fillOpacity="0.06" />
            <path d="M32 62 C36 50, 44 44, 50 44 C56 44, 64 50, 68 62" strokeWidth="2.5" />
            <path d="M42 40 L50 28 L58 40 Z" fill="#111111" />
            <circle cx="50" cy="22" r="3" fill="#111111" />
            <text x="50" y="58" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#111111" fontFamily="sans-serif">
              AICTE
            </text>
          </svg>
        </div>
        <div className="flex flex-col text-left leading-none">
          <span className="font-bold text-[11px] sm:text-xs text-black tracking-tight">{t.aicteTitle}</span>
          <span className="text-[8px] sm:text-[9px] text-black font-normal opacity-75 mt-0.5 leading-tight">
            {t.aicteSub}
          </span>
        </div>
      </div>

      {/* Thin Divider */}
      <div className="h-6 w-px bg-black/20 hidden md:block" />

      {/* 3. MoE's Innovation Cell (MIC) */}
      <div className="hidden md:flex items-center gap-1.5 group cursor-pointer">
        <div className="w-7 h-7 sm:w-8 sm:h-8 flex-shrink-0 transition-transform duration-300 group-hover:scale-105">
          <svg
            viewBox="0 0 100 100"
            className="w-full h-full"
            fill="none"
            stroke="#111111"
            strokeWidth="2.5"
          >
            {/* Half Gear on left */}
            <path d="M48 18 C30 20, 18 34, 18 50 C18 66, 30 80, 48 82" strokeWidth="4" strokeDasharray="5 3" />
            {/* Half Bulb on right */}
            <path d="M52 18 C70 20, 82 34, 82 50 C82 60, 74 68, 68 74 L68 82 L52 82" strokeWidth="2.5" fill="#111111" fillOpacity="0.08" />
            {/* Brain / Synapse Nodes inside Bulb */}
            <path d="M54 36 Q64 42 58 52 T64 66" strokeWidth="2" />
            <circle cx="64" cy="42" r="2.5" fill="#111111" />
            <circle cx="58" cy="52" r="2.5" fill="#111111" />
            <circle cx="64" cy="66" r="2.5" fill="#111111" />
          </svg>
        </div>
        <div className="flex flex-col text-left leading-none">
          <span className="font-bold text-[10px] sm:text-[11px] text-black tracking-tight">{t.micTitle}</span>
          <span className="text-[8px] sm:text-[9px] text-black font-normal opacity-75 mt-0.5">{t.micSub}</span>
        </div>
      </div>

    </div>
  );
};
