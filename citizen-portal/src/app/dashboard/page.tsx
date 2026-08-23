'use client';

import React, { useState, useMemo, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import { JHARKHAND_DISTRICTS } from '@/lib/seedData';
import { Category, ProblemStatus } from '@/types';
import { ProblemCard } from '@/components/ProblemCard';
import {
  PlusCircle,
  Compass,
  Search,
  SlidersHorizontal,
  MapPin,
  TrendingUp,
  RotateCcw,
  LayoutGrid,
  List,
  GraduationCap,
  CheckCircle2,
  Clock,
  Sparkles,
  Layers,
  ArrowRight
} from 'lucide-react';

const ALL_CATEGORIES: Category[] = [
  'Education',
  'Agriculture',
  'Healthcare',
  'Water Resources',
  'Environment',
  'Energy',
  'Urban Development',
  'Accessibility',
  'Public Administration',
  'Rural Livelihoods',
];

const ALL_STATUSES: ProblemStatus[] = [
  'Submitted',
  'Under Review',
  'Matched with Institution',
  'In Progress',
  'Solution Implemented',
];

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const districtParam = searchParams.get('district');

  const { language, problems, user, isHydrating, isLoadingProblems, problemsError, syncLiveChallenges } =
    useAppStore();
  const t = translations[language];

  useEffect(() => {
    if (isHydrating) return;
    if (!user) {
      router.replace('/login');
      return;
    }
    void syncLiveChallenges();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isHydrating, user]);

  // Filters & View state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedDistrict, setSelectedDistrict] = useState<string>(districtParam || 'ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<'upvotes' | 'recent' | 'oldest'>('upvotes');
  const [quickFilter, setQuickFilter] = useState<'all' | 'rd' | 'implemented' | 'trending'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'compact'>('grid');

  // Sync if URL param changes
  useEffect(() => {
    if (districtParam) {
      setSelectedDistrict(districtParam);
    }
  }, [districtParam]);

  // Overall Platform Intelligence Metrics
  const stats = useMemo(() => {
    const total = problems.length;
    const inRD = problems.filter(
      (p) => p.status === 'Matched with Institution' || p.status === 'In Progress'
    ).length;
    const implemented = problems.filter((p) => p.status === 'Solution Implemented').length;
    const totalUpvotes = problems.reduce((acc, p) => acc + p.upvotes, 0);

    return { total, inRD, implemented, totalUpvotes };
  }, [problems]);

  // Filtered & Sorted problems
  const filteredProblems = useMemo(() => {
    return problems
      .filter((p) => {
        // Quick filter shortcuts
        if (quickFilter === 'rd' && p.status !== 'Matched with Institution' && p.status !== 'In Progress') {
          return false;
        }
        if (quickFilter === 'implemented' && p.status !== 'Solution Implemented') {
          return false;
        }
        if (quickFilter === 'trending' && p.upvotes < 200) {
          return false;
        }

        // Search query match
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase().trim();
          const matchTitle = p.title.toLowerCase().includes(q);
          const matchDesc = p.description.toLowerCase().includes(q);
          const matchCode = p.trackingCode.toLowerCase().includes(q);
          const matchDistrict = p.location.district.toLowerCase().includes(q);
          const matchCat = p.category.toLowerCase().includes(q);
          const matchInst = p.matchedInstitution?.name.toLowerCase().includes(q);
          if (!matchTitle && !matchDesc && !matchCode && !matchDistrict && !matchCat && !matchInst) {
            return false;
          }
        }

        // Category filter
        if (selectedCategory !== 'ALL' && p.category !== selectedCategory) {
          return false;
        }

        // District filter
        if (selectedDistrict !== 'ALL') {
          if (!p.location.district.toLowerCase().includes(selectedDistrict.toLowerCase())) {
            return false;
          }
        }

        // Status filter
        if (selectedStatus !== 'ALL' && p.status !== selectedStatus) {
          return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'upvotes') {
          return b.upvotes - a.upvotes;
        }
        if (sortBy === 'recent') {
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        }
        if (sortBy === 'oldest') {
          return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
        }
        return 0;
      });
  }, [problems, searchQuery, selectedCategory, selectedDistrict, selectedStatus, sortBy, quickFilter]);

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('ALL');
    setSelectedDistrict('ALL');
    setSelectedStatus('ALL');
    setQuickFilter('all');
    setSortBy('upvotes');
  };

  const hasActiveFilters =
    searchQuery !== '' ||
    selectedCategory !== 'ALL' ||
    selectedDistrict !== 'ALL' ||
    selectedStatus !== 'ALL' ||
    quickFilter !== 'all';

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-black py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* ========================================================================= */}
        {/* 1. CIVIC INTELLIGENCE HERO HEADER                                         */}
        {/* ========================================================================= */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 pb-6 border-b border-black/15">
          <div>
            {user && (
              <div className="mb-2">
                <span className="text-xs font-semibold text-black/70">
                  Logged in as <strong className="text-black">{user.fullName}</strong> ({user.phone})
                </span>
              </div>
            )}
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-black tracking-tight">
              {t.dashboardTitle}
            </h1>
            <p className="text-sm sm:text-base text-black/75 mt-2 max-w-2xl leading-relaxed">
              {t.dashboardSub}
            </p>
          </div>

          {/* Action CTAs: Raise Grievance & Track */}
          <div className="flex items-center gap-3 flex-wrap">
            <Link
              href="/raise"
              className="flex items-center gap-2 bg-black text-white px-5 py-3 rounded-full text-sm font-bold shadow hover:bg-black/85 hover:scale-[1.02] active:scale-95 transition-all focus:outline-none"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t.raiseProblemBtn}</span>
            </Link>

            <Link
              href="/track"
              className="flex items-center gap-2 bg-white text-black border-2 border-black px-5 py-3 rounded-full text-sm font-bold shadow-2xs hover:bg-[#FAF8F5] hover:scale-[1.02] active:scale-95 transition-all focus:outline-none"
            >
              <Compass className="w-4 h-4" />
              <span>{t.trackProblemsBtn}</span>
            </Link>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 2. EXECUTIVE CIVIC INTELLIGENCE METRIC STRIP                              */}
        {/* ========================================================================= */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          
          <button
            type="button"
            onClick={() => {
              setQuickFilter('all');
              setSelectedStatus('ALL');
            }}
            className={`p-4 rounded-2xl border-2 text-left transition-all ${
              quickFilter === 'all' && selectedStatus === 'ALL'
                ? 'bg-black text-white border-black shadow-sm'
                : 'bg-white text-black border-black/20 hover:border-black'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider opacity-75">
                Active Dossiers
              </span>
              <Layers className="w-4 h-4 opacity-75" />
            </div>
            <p className="text-2xl sm:text-3xl font-black font-mono mt-2">{stats.total}</p>
            <p className="text-[11px] opacity-70 mt-0.5">Across 24 Jharkhand Districts</p>
          </button>

          <button
            type="button"
            onClick={() => setQuickFilter('rd')}
            className={`p-4 rounded-2xl border-2 text-left transition-all ${
              quickFilter === 'rd'
                ? 'bg-black text-white border-black shadow-sm'
                : 'bg-white text-black border-black/20 hover:border-black'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider opacity-75">
                In Active R&D
              </span>
              <GraduationCap className="w-4 h-4 opacity-75" />
            </div>
            <p className="text-2xl sm:text-3xl font-black font-mono mt-2">{stats.inRD}</p>
            <p className="text-[11px] opacity-70 mt-0.5">IIT ISM, BIT Mesra, NIT JSR</p>
          </button>

          <button
            type="button"
            onClick={() => setQuickFilter('implemented')}
            className={`p-4 rounded-2xl border-2 text-left transition-all ${
              quickFilter === 'implemented'
                ? 'bg-black text-white border-black shadow-sm'
                : 'bg-white text-black border-black/20 hover:border-black'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider opacity-75">
                Deployed Solutions
              </span>
              <CheckCircle2 className="w-4 h-4 opacity-75" />
            </div>
            <p className="text-2xl sm:text-3xl font-black font-mono mt-2">{stats.implemented}</p>
            <p className="text-[11px] opacity-70 mt-0.5">Field Verified in Villages</p>
          </button>

          <button
            type="button"
            onClick={() => setQuickFilter('trending')}
            className={`p-4 rounded-2xl border-2 text-left transition-all ${
              quickFilter === 'trending'
                ? 'bg-black text-white border-black shadow-sm'
                : 'bg-white text-black border-black/20 hover:border-black'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider opacity-75">
                Citizen Upvotes
              </span>
              <TrendingUp className="w-4 h-4 opacity-75" />
            </div>
            <p className="text-2xl sm:text-3xl font-black font-mono mt-2">{stats.totalUpvotes}</p>
            <p className="text-[11px] opacity-70 mt-0.5">Community Endorsements</p>
          </button>

        </div>

        {/* ========================================================================= */}
        {/* 3. INTERACTIVE JHARKHAND DISTRICT HORIZONTAL QUICK SELECTOR               */}
        {/* ========================================================================= */}
        <div className="bg-white border-2 border-black rounded-2xl p-4 shadow-xs space-y-2">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold uppercase tracking-wider text-black flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-black" />
              Jharkhand District Filter Matrix
            </span>
            {selectedDistrict !== 'ALL' && (
              <button
                type="button"
                onClick={() => setSelectedDistrict('ALL')}
                className="text-xs font-bold text-black/60 hover:text-black underline cursor-pointer"
              >
                Reset to All Districts
              </button>
            )}
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none pt-1">
            <button
              type="button"
              onClick={() => setSelectedDistrict('ALL')}
              className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                selectedDistrict === 'ALL'
                  ? 'bg-black text-white'
                  : 'bg-[#FAF8F5] text-black border border-black/20 hover:border-black'
              }`}
            >
              All 24 Districts ({problems.length})
            </button>

            {JHARKHAND_DISTRICTS.map((dist) => {
              const count = problems.filter((p) =>
                p.location.district.toLowerCase().includes(dist.toLowerCase())
              ).length;
              return (
                <button
                  key={dist}
                  type="button"
                  onClick={() => setSelectedDistrict(dist)}
                  className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                    selectedDistrict.toLowerCase() === dist.toLowerCase()
                      ? 'bg-black text-white'
                      : 'bg-[#FAF8F5] text-black border border-black/20 hover:border-black'
                  }`}
                >
                  {dist} {count > 0 && <span className="font-mono opacity-75">({count})</span>}
                </button>
              );
            })}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 4. SEARCH, CATEGORY CHIPS, SORT & VIEW SWITCHER                           */}
        {/* ========================================================================= */}
        <div className="bg-white border-2 border-black rounded-2xl p-5 sm:p-6 shadow-xs space-y-4">
          
          {/* Top Row: Search + Sort + View Mode Toggle */}
          <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-black/60 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by keywords, tracking ID (e.g. JH-2026-001), district, or university..."
                className="w-full bg-[#FAF8F5] border border-black/30 rounded-xl pl-10 pr-4 py-2.5 text-sm font-medium text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-black/60 hover:text-black cursor-pointer"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Controls Right: Sort & View Toggle */}
            <div className="flex items-center gap-3 justify-between sm:justify-end">
              
              {/* Sort Selector */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-black/60 whitespace-nowrap hidden sm:inline">
                  {t.sortBy}:
                </span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="bg-[#FAF8F5] border border-black/30 rounded-xl px-3 py-2 text-xs font-bold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black cursor-pointer"
                >
                  <option value="upvotes">{t.sortUpvotes}</option>
                  <option value="recent">{t.sortRecent}</option>
                  <option value="oldest">{t.sortOldest}</option>
                </select>
              </div>

              {/* View Mode Toggle: Grid vs Compact Ledger */}
              <div className="flex items-center bg-[#FAF8F5] border border-black/25 rounded-xl p-0.5">
                <button
                  type="button"
                  onClick={() => setViewMode('grid')}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    viewMode === 'grid' ? 'bg-black text-white shadow-2xs' : 'text-black/60 hover:text-black'
                  }`}
                  title="Grid View"
                  aria-label="Grid View"
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('compact')}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    viewMode === 'compact' ? 'bg-black text-white shadow-2xs' : 'text-black/60 hover:text-black'
                  }`}
                  title="Compact Ledger View"
                  aria-label="Compact Ledger View"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

            </div>
          </div>

          {/* Category Filter Chips */}
          <div className="pt-3 border-t border-black/10 overflow-x-auto pb-1 scrollbar-none">
            <div className="flex items-center gap-2 min-w-max">
              <button
                type="button"
                onClick={() => setSelectedCategory('ALL')}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                  selectedCategory === 'ALL'
                    ? 'bg-black text-white'
                    : 'bg-[#FAF8F5] text-black border border-black/20 hover:border-black'
                }`}
              >
                {t.allCategories} ({problems.length})
              </button>

              {ALL_CATEGORIES.map((cat) => {
                const count = problems.filter((p) => p.category === cat).length;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      selectedCategory === cat
                        ? 'bg-black text-white'
                        : 'bg-[#FAF8F5] text-black border border-black/20 hover:border-black'
                    }`}
                  >
                    {cat} {count > 0 && <span className="opacity-75 font-mono text-[10px]">({count})</span>}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Filter Clear Bar */}
          {hasActiveFilters && (
            <div className="pt-2 border-t border-black/10 flex items-center justify-between gap-2 text-xs">
              <span className="text-black/70">
                Active filters applied: <strong className="text-black">{filteredProblems.length}</strong> matching records found
              </span>
              <button
                type="button"
                onClick={resetFilters}
                className="flex items-center gap-1 font-bold text-black hover:underline cursor-pointer"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset All Filters</span>
              </button>
            </div>
          )}

        </div>

        {/* ========================================================================= */}
        {/* 5. PROBLEMS DOSSIER REPOSITORY & LEDGER                                   */}
        {/* ========================================================================= */}
        <div>
          <div className="flex items-center justify-between mb-4 px-1">
            <span className="text-xs font-bold uppercase tracking-wider text-black/70 font-mono">
              Displaying {filteredProblems.length} of {problems.length} Verified Submissions
            </span>
          </div>

          {isLoadingProblems ? (
            <div className="bg-white border-2 border-black rounded-3xl p-12 text-center shadow-xs">
              <p className="text-sm font-semibold text-black/70">Loading your reports…</p>
            </div>
          ) : problemsError ? (
            <div className="bg-white border-2 border-red-600 rounded-3xl p-12 text-center shadow-xs">
              <p className="text-sm font-semibold text-red-700">{problemsError}</p>
              <button
                type="button"
                onClick={() => void syncLiveChallenges()}
                className="mt-4 px-5 py-2.5 rounded-full bg-black text-white text-xs font-bold hover:bg-black/80 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : filteredProblems.length > 0 ? (
            viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-7 items-stretch">
                {filteredProblems.map((problem) => (
                  <ProblemCard key={problem.id} problem={problem} viewMode="grid" />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {filteredProblems.map((problem) => (
                  <ProblemCard key={problem.id} problem={problem} viewMode="compact" />
                ))}
              </div>
            )
          ) : (
            <div className="bg-white border-2 border-black rounded-3xl p-12 text-center shadow-xs">
              <div className="w-16 h-16 rounded-full bg-[#FAF8F5] border border-black flex items-center justify-center mx-auto mb-4 text-black">
                <Search className="w-8 h-8 opacity-60" />
              </div>
              <h3 className="text-xl font-bold text-black">{t.noProblemsFound}</h3>
              <p className="text-sm text-black/70 mt-2 max-w-md mx-auto">
                No matching civic issues found under the current filter combination. Try clearing filters or submit a new grievance.
              </p>
              <div className="flex items-center justify-center gap-3 mt-6">
                <button
                  type="button"
                  onClick={resetFilters}
                  className="px-5 py-2.5 rounded-full bg-black text-white text-xs font-bold hover:bg-black/80 transition-colors inline-flex items-center gap-2 cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>{t.clearFilters}</span>
                </button>
                <Link
                  href="/raise"
                  className="px-5 py-2.5 rounded-full bg-white text-black border-2 border-black text-xs font-bold hover:bg-[#FAF8F5] transition-colors inline-flex items-center gap-2"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Submit Grievance</span>
                </Link>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#FAF8F5] flex items-center justify-center">
          <div className="w-10 h-10 border-2 border-black border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
