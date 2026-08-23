'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import {
  ArrowLeft,
  ThumbsUp,
  MapPin,
  Building2,
  Calendar,
  User,
  ShieldCheck,
  FileText,
  Image as ImageIcon,
  Compass,
  CheckCircle2,
  Clock,
  Share2,
  ExternalLink,
  Sparkles,
  Layers
} from 'lucide-react';

export default function ProblemDetailPage() {
  const params = useParams();
  const router = useRouter();
  const problemId = params?.id as string;

  const { language, upvoteProblem, hasUserUpvoted, showToast, getProblemById, fetchProblemById } =
    useAppStore();
  const t = translations[language];

  const cached = getProblemById(problemId);
  const [fetched, setFetched] = useState(cached ?? null);
  const [isLoading, setIsLoading] = useState(!cached);

  useEffect(() => {
    if (cached) return; // already have it — nothing to fetch
    // isLoading is already true here (initialized as !cached above) — no
    // need to set it again synchronously in the effect body.
    let cancelled = false;
    fetchProblemById(problemId).then((result) => {
      if (!cancelled) {
        setFetched(result);
        setIsLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problemId]);

  const problem = cached ?? fetched;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#FAF8F5] py-20 px-4 flex flex-col items-center justify-center text-center">
        <p className="text-sm font-semibold text-black/70">Loading report…</p>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="min-h-screen bg-[#FAF8F5] py-20 px-4 flex flex-col items-center justify-center text-center">
        <div className="bg-white border-2 border-black rounded-3xl p-10 max-w-lg shadow-md">
          <h2 className="text-2xl font-bold text-black mb-3">Problem Not Found</h2>
          <p className="text-sm text-black/70 mb-6">
            The civic challenge with tracking ID or identifier &quot;{problemId}&quot; could not be located.
          </p>
          <Link
            href="/dashboard"
            className="px-6 py-3 rounded-full bg-black text-white text-sm font-bold hover:bg-black/80 transition-colors inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t.backToDashboard}</span>
          </Link>
        </div>
      </div>
    );
  }

  const isUpvoted = hasUserUpvoted(problem.id);

  const handleUpvote = () => {
    const res = upvoteProblem(problem.id);
    if (res.success) {
      showToast('Upvote Recorded', `You supported "${problem.title.slice(0, 35)}..."`, 'success');
    } else {
      showToast('Notice', res.message || 'Already upvoted', 'info');
    }
  };

  const handleCopyLink = () => {
    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(window.location.href);
      showToast('Link Copied', 'Problem link copied to clipboard.', 'info');
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-black py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Top Navigation & Actions Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => router.push('/dashboard')}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-black text-xs font-bold text-black hover:bg-black hover:text-white transition-all duration-150 focus:outline-none"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{t.backToDashboard}</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleCopyLink}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-white border border-black/30 text-xs font-semibold text-black hover:border-black transition-colors"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>Share Problem</span>
            </button>

            <Link
              href={`/track?id=${encodeURIComponent(problem.trackingCode)}`}
              className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-black text-white text-xs font-bold hover:bg-black/85 transition-colors"
            >
              <Compass className="w-3.5 h-3.5" />
              <span>Track Milestones</span>
            </Link>
          </div>
        </div>

        {/* Main Problem Header Card */}
        <div className="bg-white border-2 border-black rounded-3xl p-6 sm:p-10 shadow-sm space-y-6">
          
          {/* Badges & Tracking Code */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-3.5 py-1 rounded-full text-xs font-bold bg-[#FAF8F5] border border-black text-black">
                {problem.category}
              </span>
              <span className="px-3.5 py-1 rounded-full text-xs font-bold bg-black text-white font-mono">
                {problem.trackingCode}
              </span>
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-950 border border-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
              <span>{problem.status}</span>
            </div>
          </div>

          {/* Title */}
          <h1 className="text-2xl sm:text-4xl font-extrabold text-black tracking-tight leading-tight">
            {problem.title}
          </h1>

          {/* Meta Info Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-black/10 text-xs text-black">
            <div className="flex items-center gap-2.5">
              <MapPin className="w-4 h-4 text-black flex-shrink-0" />
              <div>
                <span className="text-black/60 block">{t.locationSection}</span>
                <strong className="font-semibold">{problem.location.district} ({problem.location.villageOrArea})</strong>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <User className="w-4 h-4 text-black flex-shrink-0" />
              <div>
                <span className="text-black/60 block">Submitted By</span>
                <strong className="font-semibold">{problem.submittedBy.fullName}</strong>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <Calendar className="w-4 h-4 text-black flex-shrink-0" />
              <div>
                <span className="text-black/60 block">{t.submittedOn}</span>
                <strong className="font-semibold font-mono">
                  {new Date(problem.createdAt).toLocaleDateString('en-GB', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </strong>
              </div>
            </div>
          </div>

          {/* Upvote Callout Banner */}
          <div className="bg-[#FAF8F5] border border-black/20 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <p className="text-sm font-bold text-black">
                {problem.upvotes} Citizens have upvoted this challenge
              </p>
              <p className="text-xs text-black/70 mt-0.5">
                Upvotes increase priority ranking for university research grants and CSR funding.
              </p>
            </div>

            <button
              type="button"
              onClick={handleUpvote}
              disabled={isUpvoted}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-full text-xs font-bold border transition-all ${
                isUpvoted
                  ? 'bg-black text-white border-black cursor-default'
                  : 'bg-white text-black border-black hover:bg-black hover:text-white active:scale-95'
              }`}
            >
              <ThumbsUp className="w-4 h-4" />
              <span>{isUpvoted ? t.upvoted : t.upvote}</span>
            </button>
          </div>

        </div>

        {/* Detailed Problem Description & Media */}
        <div className="bg-white border-2 border-black rounded-3xl p-6 sm:p-10 shadow-xs space-y-6">
          <h2 className="text-lg sm:text-xl font-bold text-black border-b border-black/10 pb-3 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            <span>Problem Description & Context</span>
          </h2>

          <p className="text-sm sm:text-base text-black/90 leading-relaxed whitespace-pre-line">
            {problem.description}
          </p>

          {/* Geographic Coordinates & Map Preview */}
          <div className="pt-4 border-t border-black/10">
            <h3 className="text-xs font-bold uppercase tracking-wider text-black/60 mb-2">
              Geotagged GPS Coordinates
            </h3>
            <div className="p-4 bg-[#FAF8F5] border border-black/15 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div>
                <p className="font-semibold text-black">{problem.location.formattedAddress}</p>
                <p className="font-mono text-black/70 mt-0.5">
                  Lat: {problem.location.latitude.toFixed(4)}° N, Long: {problem.location.longitude.toFixed(4)}° E
                </p>
              </div>
              <a
                href={`https://maps.google.com/?q=${problem.location.latitude},${problem.location.longitude}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-black font-bold hover:underline"
              >
                <span>Open in Satellite Map</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          {/* Uploaded Evidence Media */}
          {problem.media.length > 0 && (
            <div className="pt-4 border-t border-black/10">
              <h3 className="text-xs font-bold uppercase tracking-wider text-black/60 mb-3">
                {t.evidenceSection}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {problem.media.map((med) => (
                  <div
                    key={med.id}
                    className="border border-black/20 rounded-2xl overflow-hidden bg-[#FAF8F5] p-3 flex items-center gap-3"
                  >
                    {med.type === 'image' ? (
                      <div className="w-16 h-16 rounded-xl overflow-hidden bg-black/10 flex-shrink-0 border border-black/20">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={med.url} alt={med.name} className="w-full h-full object-cover" />
                      </div>
                    ) : (
                      <div className="w-16 h-16 rounded-xl bg-white border border-black/20 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-8 h-8 text-black" />
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold text-black truncate">{med.name}</p>
                      <p className="text-[11px] text-black/60 uppercase">{med.type} • {med.size || '1.5 MB'}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Matched University & Solution Details (if available) */}
        {problem.matchedInstitution && (
          <div className="bg-white border-2 border-black rounded-3xl p-6 sm:p-10 shadow-xs space-y-6">
            <div className="flex items-center gap-2 border-b border-black/10 pb-3">
              <Building2 className="w-5 h-5 text-black" />
              <h2 className="text-lg sm:text-xl font-bold text-black">
                {t.matchedSection}
              </h2>
            </div>

            <div className="bg-[#FAF8F5] border border-black/20 rounded-2xl p-5 space-y-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-black/60">Institution</span>
                <h3 className="text-lg font-extrabold text-black mt-0.5">{problem.matchedInstitution.name}</h3>
                <p className="text-xs text-black/70">{problem.matchedInstitution.department}</p>
              </div>

              {problem.matchedInstitution.leadResearcher && (
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-black/60">{t.leadResearcher}</span>
                  <p className="text-sm font-semibold text-black mt-0.5">{problem.matchedInstitution.leadResearcher}</p>
                </div>
              )}

              {problem.matchedInstitution.projectTitle && (
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-black/60">{t.researchProject}</span>
                  <p className="text-sm font-bold text-black mt-0.5">{problem.matchedInstitution.projectTitle}</p>
                </div>
              )}
            </div>

            {problem.solutionSummary && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-black/60 mb-1.5">
                  {t.solutionSection}
                </h3>
                <p className="text-sm text-black/90 leading-relaxed bg-[#FAF8F5] p-4 rounded-xl border border-black/15">
                  {problem.solutionSummary}
                </p>
              </div>
            )}

            {problem.impactMetrics && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-black/60 mb-1.5">
                  {t.impactSection}
                </h3>
                <p className="text-sm font-semibold text-emerald-950 bg-emerald-50 p-4 rounded-xl border border-emerald-300">
                  🌱 {problem.impactMetrics}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Milestone Timeline Card */}
        <div className="bg-white border-2 border-black rounded-3xl p-6 sm:p-10 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-black/10 pb-3">
            <h2 className="text-lg sm:text-xl font-bold text-black flex items-center gap-2">
              <Clock className="w-5 h-5" />
              <span>{t.milestonesSection}</span>
            </h2>
            <Link
              href={`/track?id=${encodeURIComponent(problem.trackingCode)}`}
              className="text-xs font-bold text-black hover:underline inline-flex items-center gap-1"
            >
              <span>Full Tracker View</span>
              <ExternalLink className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-6 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-black/20">
            {problem.milestones.map((m, idx) => (
              <div key={m.id || idx} className="relative flex items-start gap-4">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${
                    m.completed ? 'bg-black text-white' : 'bg-white border-2 border-black text-black'
                  }`}
                >
                  {m.completed ? <CheckCircle2 className="w-4 h-4" /> : <span className="text-xs font-bold">{idx + 1}</span>}
                </div>
                <div className="bg-[#FAF8F5] border border-black/15 rounded-2xl p-4 flex-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-white border border-black/20 text-black">
                      Stage {idx + 1}: {m.stage}
                    </span>
                    <span className="text-xs font-mono text-black/60 font-semibold">{m.timestamp}</span>
                  </div>
                  <h4 className="text-sm font-bold text-black mt-2">{m.title}</h4>
                  <p className="text-xs text-black/80 mt-1 leading-relaxed">{m.description}</p>
                  {m.officerName && (
                    <p className="text-[11px] text-black/60 mt-2 font-medium">
                      Audited by: {m.officerName}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>

        </div>

      </div>
    </div>
  );
}
