'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { OfficialLogos } from './OfficialLogos';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import { Globe, User as UserIcon, LogOut, ChevronDown, Check, LayoutDashboard, PlusCircle, Compass, Minus, Plus, Home } from 'lucide-react';

export const TopBar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();

  const {
    language,
    setLanguage,
    textScale,
    increaseTextScale,
    decreaseTextScale,
    cycleTextScale,
    user,
    logoutUser,
  } = useAppStore();

  const t = translations[language];

  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  const langRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Update HTML data-font-size attribute when textScale changes
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-font-size', textScale);
    }
  }, [textScale]);

  // Click outside listener for dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setLangDropdownOpen(false);
      }
      if (userRef.current && !userRef.current.contains(event.target as Node)) {
        setUserDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!mounted) {
    return (
      <header className="w-full bg-[#FAF8F5] py-4 px-6 sm:px-10 lg:px-12">
        <div className="w-full flex items-center justify-between">
          <div className="h-9 w-48 bg-black/5 animate-pulse rounded" />
          <div className="h-9 w-52 bg-black/5 animate-pulse rounded-full" />
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 w-full bg-[#FAF8F5]/95 backdrop-blur-md transition-colors duration-200">
      <div className="w-full px-4 sm:px-8 lg:px-12 py-3 flex items-center justify-between gap-4">
        
        {/* Top-Left Corner: Official Credibility Strip */}
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="hover:opacity-90 transition-opacity focus:outline-none rounded-lg"
            title="SocioSolve Home"
          >
            <OfficialLogos />
          </Link>
        </div>

        {/* Top Middle-Right & Right Cluster */}
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap justify-end">
          
          {/* Persistent Navigation Bar (from Landing Page Onwards) */}
          <nav className="hidden lg:flex items-center gap-1 bg-white border border-black/25 rounded-full px-1.5 py-1 text-xs font-semibold shadow-2xs">
            <Link
              href="/"
              className={`px-3 py-1 rounded-full transition-colors flex items-center gap-1 ${
                pathname === '/' ? 'bg-black text-white' : 'hover:bg-black/5 text-black'
              }`}
            >
              <Home className="w-3 h-3" />
              <span>{t.homeNav}</span>
            </Link>
            <Link
              href="/dashboard"
              className={`px-3 py-1 rounded-full transition-colors flex items-center gap-1 ${
                pathname === '/dashboard' ? 'bg-black text-white' : 'hover:bg-black/5 text-black'
              }`}
            >
              <LayoutDashboard className="w-3 h-3" />
              <span>{t.dashboardNav}</span>
            </Link>
            <Link
              href="/raise"
              className={`px-3 py-1 rounded-full transition-colors flex items-center gap-1 ${
                pathname === '/raise' ? 'bg-black text-white' : 'hover:bg-black/5 text-black'
              }`}
            >
              <PlusCircle className="w-3 h-3" />
              <span>{t.raiseNav}</span>
            </Link>
            <Link
              href="/track"
              className={`px-3 py-1 rounded-full transition-colors flex items-center gap-1 ${
                pathname === '/track' ? 'bg-black text-white' : 'hover:bg-black/5 text-black'
              }`}
            >
              <Compass className="w-3 h-3" />
              <span>{t.trackNav}</span>
            </Link>
          </nav>

          {/* 1. Pill-shaped Text Size Control: [ -  T  + ] */}
          <div
            className="flex items-center bg-white border border-black/30 rounded-full px-2.5 py-1 shadow-2xs hover:border-black transition-colors"
            title={`${t.fontSizeToggle}: ${textScale}`}
          >
            <button
              type="button"
              onClick={decreaseTextScale}
              disabled={textScale === 'normal'}
              className={`p-0.5 rounded-full text-black hover:bg-black/10 transition-colors focus:outline-none cursor-pointer ${
                textScale === 'normal' ? 'opacity-30 cursor-not-allowed' : 'opacity-80'
              }`}
              aria-label="Decrease text size"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              onClick={cycleTextScale}
              className="px-2 text-xs font-bold tracking-wider text-black hover:text-black/70 transition-colors focus:outline-none select-none cursor-pointer"
              aria-label="Cycle text size"
            >
              T
            </button>

            <button
              type="button"
              onClick={increaseTextScale}
              disabled={textScale === 'larger'}
              className={`p-0.5 rounded-full text-black hover:bg-black/10 transition-colors focus:outline-none cursor-pointer ${
                textScale === 'larger' ? 'opacity-30 cursor-not-allowed' : 'opacity-80'
              }`}
              aria-label="Increase text size"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* 2. Rounded Language Dropdown with Globe icon */}
          <div className="relative" ref={langRef}>
            <button
              type="button"
              onClick={() => setLangDropdownOpen(!langDropdownOpen)}
              className="flex items-center gap-1.5 bg-white border border-black/30 rounded-full px-3 py-1 text-xs sm:text-sm font-medium text-black hover:border-black shadow-2xs transition-colors focus:outline-none cursor-pointer"
              aria-expanded={langDropdownOpen}
              aria-label={t.languageToggle}
            >
              <Globe className="w-3.5 h-3.5 text-black" />
              <span>{language === 'en' ? 'English' : 'हिन्दी'}</span>
              <ChevronDown className="w-3.5 h-3.5 text-black opacity-60 ml-0.5" />
            </button>

            {langDropdownOpen && (
              <div className="absolute right-0 mt-1.5 w-36 bg-white border border-black/20 rounded-xl shadow-lg py-1 z-50 overflow-hidden text-sm animate-in fade-in zoom-in-95 duration-100">
                <button
                  type="button"
                  onClick={() => {
                    setLanguage('en');
                    setLangDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3.5 py-2 flex items-center justify-between text-black hover:bg-[#FAF8F5] transition-colors cursor-pointer ${
                    language === 'en' ? 'font-semibold bg-[#FAF8F5]' : ''
                  }`}
                >
                  <span>English</span>
                  {language === 'en' && <Check className="w-4 h-4 text-black" />}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setLanguage('hi');
                    setLangDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3.5 py-2 flex items-center justify-between text-black hover:bg-[#FAF8F5] transition-colors cursor-pointer ${
                    language === 'hi' ? 'font-semibold bg-[#FAF8F5]' : ''
                  }`}
                >
                  <span>हिन्दी</span>
                  {language === 'hi' && <Check className="w-4 h-4 text-black" />}
                </button>
              </div>
            )}
          </div>

          {/* 3. Rounded Login / Citizen Profile Button */}
          {user ? (
            <div className="relative" ref={userRef}>
              <button
                type="button"
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2 bg-white border border-black/30 rounded-full pl-2 pr-3 py-1 text-xs sm:text-sm font-medium text-black hover:border-black shadow-2xs transition-colors focus:outline-none cursor-pointer"
              >
                <span className="w-5 h-5 rounded-full bg-black text-white flex items-center justify-center text-[10px] font-bold">
                  {user.fullName.slice(0, 1).toUpperCase()}
                </span>
                <span className="max-w-[80px] sm:max-w-[110px] truncate">{user.fullName.split(' ')[0]}</span>
                <ChevronDown className="w-3.5 h-3.5 text-black opacity-60" />
              </button>

              {userDropdownOpen && (
                <div className="absolute right-0 mt-1.5 w-56 bg-white border border-black/20 rounded-xl shadow-lg p-2 z-50 text-sm animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3 py-2 border-b border-black/10">
                    <p className="font-semibold text-black leading-tight">{user.fullName}</p>
                    <p className="text-xs text-black/60 font-mono mt-0.5">{user.phone}</p>
                    <div className="mt-1.5 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#FAF8F5] border border-black/20 text-[10px] font-medium text-black">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                      {t.citizenBadge}
                    </div>
                  </div>

                  <div className="py-1">
                    <Link
                      href="/dashboard"
                      onClick={() => setUserDropdownOpen(false)}
                      className="w-full text-left px-3 py-2 rounded-lg text-black hover:bg-[#FAF8F5] transition-colors flex items-center gap-2 text-xs font-semibold"
                    >
                      <LayoutDashboard className="w-3.5 h-3.5 text-black/70" />
                      <span>{t.dashboardNav}</span>
                    </Link>
                    <Link
                      href="/raise"
                      onClick={() => setUserDropdownOpen(false)}
                      className="w-full text-left px-3 py-2 rounded-lg text-black hover:bg-[#FAF8F5] transition-colors flex items-center gap-2 text-xs font-semibold"
                    >
                      <PlusCircle className="w-3.5 h-3.5 text-black/70" />
                      <span>{t.raiseNav}</span>
                    </Link>
                    <Link
                      href="/track"
                      onClick={() => setUserDropdownOpen(false)}
                      className="w-full text-left px-3 py-2 rounded-lg text-black hover:bg-[#FAF8F5] transition-colors flex items-center gap-2 text-xs font-semibold"
                    >
                      <Compass className="w-3.5 h-3.5 text-black/70" />
                      <span>{t.trackNav}</span>
                    </Link>
                  </div>

                  <div className="pt-1 border-t border-black/10">
                    <button
                      type="button"
                      onClick={() => {
                        logoutUser();
                        setUserDropdownOpen(false);
                        router.push('/');
                      }}
                      className="w-full text-left px-3 py-1.5 rounded-lg text-red-700 hover:bg-red-50 transition-colors flex items-center gap-2 text-xs font-semibold cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5 text-red-700" />
                      <span>{t.logout}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link
              href="/login"
              className="flex items-center gap-1.5 bg-white border border-black/30 rounded-full px-3.5 py-1 text-xs sm:text-sm font-semibold text-black hover:bg-black hover:text-white shadow-2xs transition-all duration-150 focus:outline-none"
            >
              <UserIcon className="w-3.5 h-3.5" />
              <span>{t.login}</span>
            </Link>
          )}

        </div>

      </div>
    </header>
  );
};
