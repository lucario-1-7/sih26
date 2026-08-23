'use client';

import React from 'react';
import Link from 'next/link';
import { SocioSolveLogo } from '@/components/SocioSolveLogo';
import { StatsCircles } from '@/components/StatsCircles';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import {
  ArrowRight,
  PlusCircle,
  Compass,
  FileEdit,
  Users2,
  Lightbulb,
  CheckCircle2,
  Sparkles,
  ChevronDown
} from 'lucide-react';

export default function LandingPage() {
  const language = useAppStore((state) => state.language);
  const t = translations[language];

  return (
    <div className="w-full bg-[#FAF8F5] text-black overflow-x-hidden">
      
      {/* ========================================================================= */}
      {/* 2.1 HERO VIEWPORT (EXACT MATCH TO LOCKED REFERENCE IMAGE)                */}
      {/* ========================================================================= */}
      <section className="relative w-full min-h-[calc(100vh-65px)] flex flex-col justify-between items-center px-6 sm:px-12 py-8 sm:py-12 overflow-hidden select-none">
        
        {/* Empty top spacing anchor */}
        <div className="w-full h-2" />

        {/* Centered Hero Typography Cluster */}
        <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-center text-center z-10 my-auto px-2">
          
          {/* Large Serif Italic Logotype with Dual Proportional Circular Emblems */}
          <div className="hover:scale-[1.01] transition-transform duration-200 cursor-default">
            <SocioSolveLogo />
          </div>

          {/* Primary Tagline directly below logotype */}
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-black tracking-tight mt-6 sm:mt-8 font-sans">
            {t.tagline1}
          </h1>

          {/* Subtext Paragraph */}
          <p className="text-sm sm:text-base md:text-lg text-black/90 max-w-xl mx-auto mt-4 sm:mt-5 font-normal leading-relaxed">
            {t.heroSubtext}
          </p>

        </div>

        {/* Subtle scroll down indicator */}
        <div className="z-10 text-center pb-2 opacity-40 hover:opacity-100 transition-opacity">
          <ChevronDown className="w-5 h-5 mx-auto animate-bounce text-black" />
        </div>

      </section>


      {/* ========================================================================= */}
      {/* ACTION PORTAL STRIP (IMMEDIATELY BELOW HERO)                              */}
      {/* ========================================================================= */}
      <section className="py-8 px-6 sm:px-12 border-t border-black/10 bg-[#FAF8F5]">
        <div className="max-w-4xl mx-auto flex flex-wrap items-center justify-center gap-3 sm:gap-4">
          <Link
            href="/raise"
            className="flex items-center gap-2 bg-black text-white px-6 py-3 rounded-full text-sm font-bold shadow-xs hover:bg-black/85 hover:scale-[1.02] active:scale-95 transition-all focus:outline-none"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{t.raiseProblemBtn}</span>
          </Link>

          <Link
            href="/dashboard"
            className="flex items-center gap-2 bg-white text-black border-2 border-black px-6 py-3 rounded-full text-sm font-bold shadow-2xs hover:bg-[#FAF8F5] hover:scale-[1.02] active:scale-95 transition-all focus:outline-none"
          >
            <span>{t.dashboardTitle}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            href="/track"
            className="flex items-center gap-2 bg-white text-black border border-black/30 px-5 py-3 rounded-full text-sm font-semibold hover:border-black transition-all focus:outline-none"
          >
            <Compass className="w-4 h-4" />
            <span>{t.trackProblemsBtn}</span>
          </Link>
        </div>
      </section>


      {/* ========================================================================= */}
      {/* 2.2 SECOND TAGLINE SECTION                                                */}
      {/* ========================================================================= */}
      <section className="py-16 sm:py-24 px-6 sm:px-12 border-t border-black/10 bg-[#FAF8F5] text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-5xl md:text-6xl font-black text-black tracking-tight leading-tight">
            {t.tagline2}
          </h2>

          <p className="text-base sm:text-lg md:text-xl text-black/80 mt-6 leading-relaxed max-w-3xl mx-auto">
            {t.tagline2Sub}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-12 text-left">
            <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-xs">
              <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center font-bold font-mono text-sm mb-4">
                01
              </div>
              <h3 className="font-bold text-lg text-black">Grassroots Ingestion</h3>
              <p className="text-xs sm:text-sm text-black/75 mt-2 leading-relaxed">
                Problems are documented by citizens with geotagged media, bypassing bureaucratic silos for direct visibility.
              </p>
            </div>

            <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-xs">
              <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center font-bold font-mono text-sm mb-4">
                02
              </div>
              <h3 className="font-bold text-lg text-black">University R&D Pairing</h3>
              <p className="text-xs sm:text-sm text-black/75 mt-2 leading-relaxed">
                IITs, NITs, and state universities adopt verified challenges as sponsored capstone and faculty research projects.
              </p>
            </div>

            <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-xs">
              <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center font-bold font-mono text-sm mb-4">
                03
              </div>
              <h3 className="font-bold text-lg text-black">Field Deployment</h3>
              <p className="text-xs sm:text-sm text-black/75 mt-2 leading-relaxed">
                Tested prototypes are manufactured with CSR grants and handed over to panchayats with verifiable milestones.
              </p>
            </div>
          </div>

        </div>
      </section>


      {/* ========================================================================= */}
      {/* 2.3 "HOW IT WORKS" SECTION                                                */}
      {/* ========================================================================= */}
      <section className="py-16 sm:py-24 px-6 sm:px-12 border-t border-black/10 bg-[#FAF8F5]">
        <div className="max-w-6xl mx-auto">
          
          <div className="text-center max-w-2xl mx-auto mb-14 sm:mb-18">
            <span className="text-xs sm:text-sm font-bold uppercase tracking-widest text-black/70">
              {t.howItWorksEyebrow}
            </span>
            <h2 className="text-3xl sm:text-5xl font-black text-black tracking-tight mt-2">
              {t.howItWorksTitle}
            </h2>
          </div>

          {/* 4 Steps Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
            
            {/* Step 1 */}
            <div className="bg-white border-2 border-black rounded-2xl p-6 sm:p-7 shadow-xs flex flex-col justify-between hover:shadow-md transition-all duration-200 group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-[#FAF8F5] border border-black flex items-center justify-center text-black mb-5 group-hover:scale-105 transition-transform">
                  <FileEdit className="w-6 h-6" />
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-black leading-snug">
                  {t.step1Title}
                </h3>
                <p className="text-sm text-black/80 mt-3 leading-relaxed">
                  {t.step1Desc}
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-black/10 text-xs font-bold text-black/50 font-mono">
                STAGE 01 / INTAKE
              </div>
            </div>

            {/* Step 2 */}
            <div className="bg-white border-2 border-black rounded-2xl p-6 sm:p-7 shadow-xs flex flex-col justify-between hover:shadow-md transition-all duration-200 group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-[#FAF8F5] border border-black flex items-center justify-center text-black mb-5 group-hover:scale-105 transition-transform">
                  <Users2 className="w-6 h-6" />
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-black leading-snug">
                  {t.step2Title}
                </h3>
                <p className="text-sm text-black/80 mt-3 leading-relaxed">
                  {t.step2Desc}
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-black/10 text-xs font-bold text-black/50 font-mono">
                STAGE 02 / REVIEW
              </div>
            </div>

            {/* Step 3 */}
            <div className="bg-white border-2 border-black rounded-2xl p-6 sm:p-7 shadow-xs flex flex-col justify-between hover:shadow-md transition-all duration-200 group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-[#FAF8F5] border border-black flex items-center justify-center text-black mb-5 group-hover:scale-105 transition-transform">
                  <Lightbulb className="w-6 h-6" />
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-black leading-snug">
                  {t.step3Title}
                </h3>
                <p className="text-sm text-black/80 mt-3 leading-relaxed">
                  {t.step3Desc}
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-black/10 text-xs font-bold text-black/50 font-mono">
                STAGE 03 / R&D
              </div>
            </div>

            {/* Step 4 */}
            <div className="bg-white border-2 border-black rounded-2xl p-6 sm:p-7 shadow-xs flex flex-col justify-between hover:shadow-md transition-all duration-200 group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-black text-white flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-black leading-snug">
                  {t.step4Title}
                </h3>
                <p className="text-sm text-black/80 mt-3 leading-relaxed">
                  {t.step4Desc}
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-black/10 text-xs font-bold text-black/50 font-mono">
                STAGE 04 / IMPACT
              </div>
            </div>

          </div>

        </div>
      </section>


      {/* ========================================================================= */}
      {/* 2.4 "STATISTICS" SECTION (CIRCULAR BADGES)                                 */}
      {/* ========================================================================= */}
      <StatsCircles />


      {/* ========================================================================= */}
      {/* BOTTOM CITIZEN ACTION STRIP                                               */}
      {/* ========================================================================= */}
      <section className="py-16 sm:py-20 px-6 sm:px-12 border-t border-black/10 bg-white">
        <div className="max-w-4xl mx-auto bg-[#FAF8F5] border-2 border-black rounded-3xl p-8 sm:p-12 text-center shadow-xs">
          <h2 className="text-2xl sm:text-4xl font-extrabold text-black tracking-tight">
            Be the Catalyst for Change in Your District
          </h2>
          <p className="text-sm sm:text-base text-black/75 max-w-xl mx-auto mt-3 leading-relaxed">
            Whether it is drinking water purity, forest produce drying, or school lab accessibility, your submission mobilizes Jharkhand’s brightest minds.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
            <Link
              href="/raise"
              className="flex items-center gap-2 bg-black text-white px-7 py-3.5 rounded-full text-sm font-bold shadow hover:bg-black/85 hover:scale-[1.02] active:scale-95 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t.raiseProblemBtn}</span>
            </Link>

            <Link
              href="/track"
              className="flex items-center gap-2 bg-white text-black border border-black px-6 py-3.5 rounded-full text-sm font-bold hover:bg-[#FAF8F5] transition-all"
            >
              <Compass className="w-4 h-4" />
              <span>{t.trackProblemsBtn}</span>
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
