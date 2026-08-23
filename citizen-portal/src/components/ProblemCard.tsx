'use client';

import React from 'react';
import Link from 'next/link';
import { Problem } from '@/types';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import {
  ThumbsUp,
  MapPin,
  ArrowUpRight,
  Building2,
  CheckCircle2,
  Clock,
  FileText,
  Camera,
  Layers,
  GraduationCap,
  Sparkles
} from 'lucide-react';

interface ProblemCardProps {
  problem: Problem;
  viewMode?: 'grid' | 'compact';
}

export const ProblemCard: React.FC<ProblemCardProps> = ({ problem, viewMode = 'grid' }) => {
  const { language, upvoteProblem, hasUserUpvoted, showToast } = useAppStore();
  const t = translations[language];

  const isUpvoted = hasUserUpvoted(problem.id);

  const handleUpvote = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const res = upvoteProblem(problem.id);
    if (res.success) {
      showToast('Upvote Recorded', `You supported "${problem.title.slice(0, 35)}..."`, 'success');
    } else {
      showToast('Notice', res.message || 'Already upvoted', 'info');
    }
  };

  const getStatusBadge = (status: Problem['status']) => {
    switch (status) {
      case 'Solution Implemented':
        return {
          text: t.statusImplemented,
          bg: 'bg-emerald-50 text-emerald-950 border-emerald-500',
          dot: 'bg-emerald-600',
        };
      case 'In Progress':
        return {
          text: t.statusInProgress,
          bg: 'bg-blue-50 text-blue-950 border-blue-500',
          dot: 'bg-blue-600 animate-pulse',
        };
      case 'Matched with Institution':
        return {
          text: t.statusMatched,
          bg: 'bg-purple-50 text-purple-950 border-purple-500',
          dot: 'bg-purple-600',
        };
      case 'Under Review':
        return {
          text: t.statusUnderReview,
          bg: 'bg-amber-50 text-amber-950 border-amber-500',
          dot: 'bg-amber-600',
        };
      default:
        return {
          text: t.statusSubmitted,
          bg: 'bg-zinc-100 text-zinc-900 border-zinc-400',
          dot: 'bg-zinc-500',
        };
    }
  };

  const statusInfo = getStatusBadge(problem.status);
  const completedMilestonesCount = problem.milestones.filter((m) => m.completed).length;
  const currentMilestone = problem.milestones.find((m) => !m.completed) || problem.milestones[problem.milestones.length - 1];

  // =========================================================================
  // COMPACT LEDGER ROW VIEW
  // =========================================================================
  if (viewMode === 'compact') {
    return (
      <article className="bg-white border-2 border-black rounded-xl p-4 shadow-2xs hover:shadow-md transition-all duration-150 flex flex-col md:flex-row md:items-center justify-between gap-4 group">
        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs font-bold text-black bg-[#FAF8F5] border border-black/30 px-2 py-0.5 rounded">
              {problem.trackingCode}
            </span>
            <span className="text-xs font-bold text-black/75 bg-white border border-black/20 px-2 py-0.5 rounded-full">
              {problem.category}
            </span>
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold border ${statusInfo.bg}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${statusInfo.dot}`} />
              {statusInfo.text}
            </span>
          </div>

          <h3 className="text-base font-bold text-black group-hover:text-black/80 truncate">
            <Link href={`/problem/${problem.id}`} className="hover:underline">
              {problem.title}
            </Link>
          </h3>

          <div className="flex items-center gap-3 text-xs text-black/70">
            <span className="flex items-center gap-1 font-semibold text-black">
              <MapPin className="w-3 h-3 text-black" />
              {problem.location.district}
            </span>
            <span>•</span>
            {problem.matchedInstitution ? (
              <span className="text-black/80 font-medium truncate">
                Adopted by <strong className="text-black">{problem.matchedInstitution.name}</strong>
              </span>
            ) : (
              <span>Citizen Dossier by {problem.submittedBy.fullName}</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <button
            type="button"
            onClick={handleUpvote}
            disabled={isUpvoted}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border transition-all ${
              isUpvoted
                ? 'bg-black text-white border-black'
                : 'bg-white text-black border-black hover:bg-black/5 active:scale-95'
            }`}
          >
            <ThumbsUp className={`w-3.5 h-3.5 ${isUpvoted ? 'text-white' : 'text-black'}`} />
            <span>{problem.upvotes}</span>
          </button>

          <Link
            href={`/problem/${problem.id}`}
            className="flex items-center gap-1 px-3.5 py-1.5 rounded-full text-xs font-bold bg-black text-white hover:bg-black/85 transition-all"
          >
            <span>Dossier</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </article>
    );
  }

  // =========================================================================
  // DETAILED EDITORIAL GRID CARD
  // =========================================================================
  return (
    <article className="bg-white border-2 border-black rounded-2xl p-5 sm:p-6 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between group relative overflow-hidden">
      
      {/* Top Header: Category, Tracking Code & Live Status Badge */}
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-[#FAF8F5] border border-black text-black">
              {problem.category}
            </span>
            <span className="text-[11px] font-mono font-bold text-black/60 bg-white border border-black/20 px-2 py-0.5 rounded">
              {problem.trackingCode}
            </span>
          </div>

          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold border flex-shrink-0 ${statusInfo.bg}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${statusInfo.dot}`} />
            {statusInfo.text}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-lg sm:text-xl font-bold text-black group-hover:text-black/85 transition-colors leading-snug font-sans">
          <Link href={`/problem/${problem.id}`} className="focus:outline-none hover:underline">
            {problem.title}
          </Link>
        </h3>

        {/* Geolocation & Citizen Submission Metadata */}
        <div className="flex flex-wrap items-center gap-y-1 gap-x-2 text-xs text-black/70 mt-2.5 font-medium">
          <span className="flex items-center gap-1 text-black font-semibold bg-[#FAF8F5] border border-black/15 px-2 py-0.5 rounded">
            <MapPin className="w-3 h-3 text-black flex-shrink-0" />
            {problem.location.district} {problem.location.block ? `(${problem.location.block})` : ''}
          </span>
          <span>•</span>
          <span className="truncate max-w-[140px]">{problem.submittedBy.fullName}</span>
          {problem.media && problem.media.length > 0 && (
            <>
              <span>•</span>
              <span className="flex items-center gap-1 text-black/60 font-mono text-[10px]">
                <Camera className="w-3 h-3" />
                {problem.media.length} media
              </span>
            </>
          )}
        </div>

        {/* Short Problem Narrative */}
        <p className="text-sm text-black/80 line-clamp-3 mt-3 leading-relaxed">
          {problem.description}
        </p>

        {/* Institutional R&D Adoption Dossier Box */}
        {problem.matchedInstitution ? (
          <div className="mt-4 p-3 rounded-xl bg-[#FAF8F5] border-2 border-black/15 text-xs text-black space-y-1.5">
            <div className="flex items-center justify-between gap-1 text-[11px] font-bold text-black">
              <span className="flex items-center gap-1 text-black">
                <GraduationCap className="w-3.5 h-3.5 text-black flex-shrink-0" />
                ACADEMIC R&D PARTNER
              </span>
              <span className="text-[10px] font-mono bg-black text-white px-1.5 py-0.2 rounded">
                Active
              </span>
            </div>
            <p className="font-bold text-black text-xs leading-snug">{problem.matchedInstitution.name}</p>
            <p className="text-[11px] text-black/75 leading-tight truncate">
              {problem.matchedInstitution.projectTitle}
            </p>
          </div>
        ) : (
          <div className="mt-4 p-2.5 rounded-xl bg-[#FAF8F5]/60 border border-dashed border-black/25 text-xs text-black/70 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-black/60 flex-shrink-0" />
            <span className="text-[11px]">Under Nodal Peer Review for Academic Assignment</span>
          </div>
        )}

        {/* 5-Stage Stepped Segmented Progress Gauge */}
        <div className="mt-4 pt-3 border-t border-black/10 space-y-1.5">
          <div className="flex items-center justify-between text-[11px] font-bold text-black">
            <span className="flex items-center gap-1 text-black/75">
              <Clock className="w-3 h-3 text-black/60" />
              Stage {completedMilestonesCount} of 5:
            </span>
            <span className="text-black font-semibold text-[10px] truncate max-w-[150px]">
              {currentMilestone?.title || 'Review'}
            </span>
          </div>

          {/* 5-segment bar */}
          <div className="grid grid-cols-5 gap-1.5">
            {[0, 1, 2, 3, 4].map((stepIdx) => {
              const isDone = stepIdx < completedMilestonesCount;
              const isCurrent = stepIdx === completedMilestonesCount;
              return (
                <div
                  key={stepIdx}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    isDone
                      ? 'bg-black'
                      : isCurrent
                      ? 'bg-black/40 animate-pulse'
                      : 'bg-black/10'
                  }`}
                  title={problem.milestones[stepIdx]?.title || `Stage ${stepIdx + 1}`}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* Bottom Actions: Tactile Upvote & Open Dossier */}
      <div className="flex items-center justify-between gap-3 pt-4 mt-4 border-t border-black/10">
        
        {/* Upvote Button with Tactile Feedback */}
        <button
          type="button"
          onClick={handleUpvote}
          disabled={isUpvoted}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-full text-xs font-bold border transition-all duration-150 cursor-pointer ${
            isUpvoted
              ? 'bg-black text-white border-black cursor-default'
              : 'bg-white text-black border-black hover:bg-black/5 active:scale-95'
          }`}
          title={isUpvoted ? t.upvoted : t.upvote}
          aria-label={isUpvoted ? t.upvoted : t.upvote}
        >
          <ThumbsUp className={`w-3.5 h-3.5 ${isUpvoted ? 'text-white' : 'text-black'}`} />
          <span className="font-mono text-xs font-bold">{problem.upvotes}</span>
          <span className="text-[11px] font-normal opacity-90 hidden sm:inline">
            {isUpvoted ? t.upvoted : t.upvote}
          </span>
        </button>

        {/* Read Full Dossier Button */}
        <Link
          href={`/problem/${problem.id}`}
          className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-white text-black border-2 border-black hover:bg-black hover:text-white transition-all duration-150 focus:outline-none shadow-2xs group-hover:border-black"
        >
          <span>Explore Dossier</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>

      </div>

    </article>
  );
};
