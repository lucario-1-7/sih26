'use client';

import React, { useState, useEffect, useMemo, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import { Problem, Milestone } from '@/types';
import {
  Compass,
  Search,
  CheckCircle2,
  Clock,
  Building2,
  MapPin,
  Copy,
  Check,
  ArrowRight,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';

function TrackContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get('id') || '';

  const { language, problems, showToast, user, isHydrating, syncLiveChallenges } = useAppStore();
  const t = translations[language];

  useEffect(() => {
    if (!isHydrating && user && problems.length === 0) {
      void syncLiveChallenges();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isHydrating, user]);

  const [searchCode, setSearchCode] = useState(initialId);
  const [selectedProblemId, setSelectedProblemId] = useState<string>(
    problems.find((p) => p.trackingCode.toLowerCase() === initialId.toLowerCase() || p.id === initialId)?.id ||
      problems[0]?.id ||
      ''
  );
  const [copied, setCopied] = useState(false);

  // Update selected problem if searchCode or URL param changes
  useEffect(() => {
    if (initialId) {
      const match = problems.find(
        (p) => p.trackingCode.toLowerCase() === initialId.toLowerCase() || p.id === initialId
      );
      if (match) {
        setSelectedProblemId(match.id);
        setSearchCode(match.trackingCode);
      }
    }
  }, [initialId, problems]);

  const currentProblem: Problem | undefined = useMemo(() => {
    return problems.find((p) => p.id === selectedProblemId) || problems[0];
  }, [problems, selectedProblemId]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchCode.trim()) return;

    const match = problems.find(
      (p) =>
        p.trackingCode.toLowerCase() === searchCode.trim().toLowerCase() ||
        p.id.toLowerCase() === searchCode.trim().toLowerCase() ||
        p.title.toLowerCase().includes(searchCode.trim().toLowerCase())
    );

    if (match) {
      setSelectedProblemId(match.id);
      showToast('Problem Located', `Loaded tracking for: ${match.trackingCode}`, 'success');
    } else {
      showToast('Not Found', 'No problem found matching the tracking code or keywords.', 'error');
    }
  };

  const handleCopyCode = () => {
    if (!currentProblem || typeof window === 'undefined') return;
    navigator.clipboard.writeText(currentProblem.trackingCode);
    setCopied(true);
    showToast(t.codeCopied, currentProblem.trackingCode, 'info');
    setTimeout(() => setCopied(false), 2000);
  };

  const getStageBadge = (stage: string) => {
    switch (stage) {
      case 'Solution Implemented':
        return 'bg-emerald-100 text-emerald-950 border-emerald-400';
      case 'In Progress':
        return 'bg-blue-100 text-blue-950 border-blue-400';
      case 'Matched with Institution':
        return 'bg-purple-100 text-purple-950 border-purple-400';
      case 'Under Review':
        return 'bg-amber-100 text-amber-950 border-amber-400';
      default:
        return 'bg-zinc-100 text-zinc-900 border-zinc-300';
    }
  };

  const completedCount = currentProblem ? currentProblem.milestones.filter((m) => m.completed).length : 0;
  const progressPercent = Math.round((completedCount / (currentProblem?.milestones.length || 5)) * 100);

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-black py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Page Header */}
        <div className="text-left">
          <h1 className="text-3xl sm:text-4xl font-black text-black tracking-tight">
            {t.trackPageTitle}
          </h1>
          <p className="text-sm sm:text-base text-black/75 mt-2 max-w-2xl leading-relaxed">
            {t.trackPageSub}
          </p>
        </div>

        {/* Search by Tracking ID Bar */}
        <div className="bg-white border-2 border-black rounded-2xl p-5 sm:p-6 shadow-xs space-y-4">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-black/60 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchCode}
                onChange={(e) => setSearchCode(e.target.value)}
                placeholder={t.searchTrackCode}
                className="w-full bg-[#FAF8F5] border border-black/30 rounded-xl pl-10 pr-4 py-3 text-sm font-mono font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>
            <button
              type="submit"
              className="bg-black text-white px-6 py-3 rounded-xl text-sm font-bold hover:bg-black/85 transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-2xs"
            >
              <Search className="w-4 h-4" />
              <span>Lookup Problem</span>
            </button>
          </form>

          {/* Quick Problem Selector Dropdown */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-black/10 text-xs">
            <span className="font-bold text-black/70">{t.selectOrSearch}</span>
            <select
              value={selectedProblemId}
              onChange={(e) => {
                setSelectedProblemId(e.target.value);
                const selected = problems.find((p) => p.id === e.target.value);
                if (selected) setSearchCode(selected.trackingCode);
              }}
              className="bg-[#FAF8F5] border border-black/30 rounded-xl px-3 py-2 text-xs font-semibold text-black focus:outline-none focus:ring-2 focus:ring-black max-w-md truncate"
            >
              {problems.map((p) => (
                <option key={p.id} value={p.id}>
                  [{p.trackingCode}] {p.title.slice(0, 45)}... ({p.location.district})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Problem Overview Banner */}
        {currentProblem && (
          <div className="bg-white border-2 border-black rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
            
            {/* Header: Title, Category & Tracking Code */}
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#FAF8F5] border border-black text-black">
                    {currentProblem.category}
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyCode}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold bg-[#FAF8F5] border border-black/30 hover:border-black text-black transition-colors"
                    title={t.copyTrackingCode}
                  >
                    <span>{currentProblem.trackingCode}</span>
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-700" /> : <Copy className="w-3.5 h-3.5 opacity-60" />}
                  </button>
                </div>

                <h2 className="text-xl sm:text-2xl font-black text-black leading-tight">
                  <Link href={`/problem/${currentProblem.id}`} className="hover:underline">
                    {currentProblem.title}
                  </Link>
                </h2>

                <div className="flex flex-wrap items-center gap-3 text-xs text-black/70">
                  <span className="flex items-center gap-1 text-black font-semibold">
                    <MapPin className="w-3.5 h-3.5 text-black" />
                    {currentProblem.location.formattedAddress}
                  </span>
                  <span>•</span>
                  <span>Submitted by <strong>{currentProblem.submittedBy.fullName}</strong></span>
                </div>
              </div>

              <div className="flex flex-col items-end gap-2 flex-shrink-0">
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStageBadge(currentProblem.status)}`}>
                  {t.currentStage}: {currentProblem.status}
                </span>
                <Link
                  href={`/problem/${currentProblem.id}`}
                  className="text-xs font-bold text-black hover:underline inline-flex items-center gap-1 mt-1"
                >
                  <span>View Full Problem File</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Overall Progress Meter */}
            <div className="p-4 bg-[#FAF8F5] border border-black/15 rounded-2xl space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-black">
                <span>Milestone Lifecycle Progress</span>
                <span className="font-mono text-sm">{progressPercent}% Completed</span>
              </div>
              <div className="w-full bg-black/10 h-3 rounded-full overflow-hidden flex">
                <div
                  className="bg-black h-full transition-all duration-500 rounded-full"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            {/* Matched Institution Banner (if matched) */}
            {currentProblem.matchedInstitution && (
              <div className="p-4 rounded-2xl bg-purple-50 border border-purple-300 text-xs text-purple-950 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <Building2 className="w-5 h-5 text-purple-900 flex-shrink-0" />
                  <div>
                    <span className="font-bold text-sm block">{currentProblem.matchedInstitution.name}</span>
                    <span className="text-purple-900/80">{currentProblem.matchedInstitution.projectTitle}</span>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-purple-200 text-purple-950 text-[11px] font-bold self-start sm:self-auto">
                  Active R&D Grant
                </span>
              </div>
            )}

            {/* Sequential Stages Timeline (Section 7) */}
            <div className="pt-6 border-t border-black/10 space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-black/70">
                Chronological Milestone Journey
              </h3>

              <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:inset-0 before:left-3 sm:before:left-3.5 before:w-0.5 before:bg-black/20">
                {currentProblem.milestones.map((milestone, idx) => {
                  const isDone = milestone.completed;
                  return (
                    <div key={milestone.id || idx} className="relative group">
                      
                      {/* Timeline Dot Icon */}
                      <div
                        className={`absolute -left-6 sm:-left-8 top-1 w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center text-xs font-bold transition-transform ${
                          isDone
                            ? 'bg-black text-white shadow-xs'
                            : 'bg-white border-2 border-black/40 text-black/60'
                        }`}
                      >
                        {isDone ? (
                          <CheckCircle2 className="w-4 h-4 text-white" />
                        ) : (
                          <span className="text-[11px]">{idx + 1}</span>
                        )}
                      </div>

                      {/* Milestone Card Content */}
                      <div
                        className={`border rounded-2xl p-4 sm:p-5 transition-all ${
                          isDone
                            ? 'bg-white border-black shadow-xs'
                            : 'bg-[#FAF8F5]/60 border-black/20 opacity-75'
                        }`}
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#FAF8F5] border border-black/20 text-black">
                              Stage {idx + 1}: {milestone.stage}
                            </span>
                            {isDone ? (
                              <span className="text-[11px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-md">
                                {t.completedMilestone}
                              </span>
                            ) : (
                              <span className="text-[11px] font-semibold text-black/50 bg-black/5 px-2 py-0.5 rounded-md">
                                {t.pendingMilestone}
                              </span>
                            )}
                          </div>

                          <span className="text-xs font-mono text-black/60 font-semibold flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            {milestone.timestamp}
                          </span>
                        </div>

                        <h4 className="text-base font-bold text-black mt-2.5">{milestone.title}</h4>
                        <p className="text-xs sm:text-sm text-black/80 mt-1 leading-relaxed">
                          {milestone.description}
                        </p>

                        {(milestone.institution || milestone.officerName) && (
                          <div className="mt-3 pt-2.5 border-t border-black/10 flex flex-wrap items-center gap-4 text-xs text-black/70">
                            {milestone.institution && (
                              <span className="font-semibold text-black">
                                🏛️ Participating Institute: <u>{milestone.institution}</u>
                              </span>
                            )}
                            {milestone.officerName && (
                              <span>
                                ✍️ Verified by: <strong>{milestone.officerName}</strong>
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                    </div>
                  );
                })}
              </div>

            </div>

          </div>
        )}

      </div>
    </div>
  );
}

export default function TrackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#FAF8F5] flex items-center justify-center p-8">
          <div className="w-8 h-8 rounded-full border-2 border-black border-t-transparent animate-spin" />
        </div>
      }
    >
      <TrackContent />
    </Suspense>
  );
}
