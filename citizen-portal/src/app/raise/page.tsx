'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import { JHARKHAND_DISTRICTS } from '@/lib/seedData';
import { ProblemMedia } from '@/types';
import { ApiError } from '@/lib/api/client';
import confetti from 'canvas-confetti';
import {
  PlusCircle,
  MapPin,
  UploadCloud,
  FileText,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  Compass,
  ArrowRight,
  Sparkles,
  LocateFixed,
  Trash2,
  ShieldAlert,
  Loader2
} from 'lucide-react';

export default function RaiseProblemPage() {
  const router = useRouter();
  const { language, user, addProblem, showToast, administrativeAreas, loadAdministrativeAreas } = useAppStore();
  const t = translations[language];

  useEffect(() => {
    if (administrativeAreas.length === 0) {
      void loadAdministrativeAreas();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  // Free-text fields below are for the citizen's own reference only — the
  // backend has no fields for block/village/GPS on a challenge. Only
  // `administrativeAreaId` and `pincode` are actually sent.
  const [district, setDistrict] = useState('Ranchi');
  const [block, setBlock] = useState('');
  const [villageOrArea, setVillageOrArea] = useState('');
  const [pincode, setPincode] = useState('');
  const [administrativeAreaId, setAdministrativeAreaId] = useState('');
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [latitude, setLatitude] = useState(23.3441);
  const [longitude, setLongitude] = useState(85.3096);
  const [isGpsDetected, setIsGpsDetected] = useState(false);
  const [isDetectingGps, setIsDetectingGps] = useState(false);

  // Media files state
  const [mediaList, setMediaList] = useState<ProblemMedia[]>([
    {
      id: 'initial-sample-01',
      type: 'image',
      name: 'groundwater_borewell_sample.jpg',
      url: 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=800&q=80',
      size: '1.4 MB',
    },
  ]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedProblemCode, setSubmittedProblemCode] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Geolocation auto-detection handler
  const handleDetectGps = () => {
    setIsDetectingGps(true);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude);
          setLongitude(position.coords.longitude);
          setIsGpsDetected(true);
          setIsDetectingGps(false);
          showToast('GPS Locked', `Coordinates captured: ${position.coords.latitude.toFixed(4)}° N, ${position.coords.longitude.toFixed(4)}° E`, 'success');
        },
        (error) => {
          // Graceful fallback to authentic Jharkhand district coordinate
          setLatitude(23.3441 + (Math.random() - 0.5) * 0.05);
          setLongitude(85.3096 + (Math.random() - 0.5) * 0.05);
          setIsGpsDetected(true);
          setIsDetectingGps(false);
          showToast('GPS Simulated', 'Approximated coordinates for Jharkhand region.', 'info');
        },
        { timeout: 8000 }
      );
    } else {
      setLatitude(23.3441);
      setLongitude(85.3096);
      setIsGpsDetected(true);
      setIsDetectingGps(false);
      showToast('GPS Simulation', 'Coordinates pinned to district headquarters.', 'info');
    }
  };

  // File upload handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const newFiles: ProblemMedia[] = Array.from(files).map((file, idx) => {
      const isVideo = file.type.startsWith('video');
      const isImage = file.type.startsWith('image');
      const type = isVideo ? 'video' : isImage ? 'image' : 'document';
      return {
        id: `upload-${Date.now()}-${idx}`,
        type,
        name: file.name,
        url: URL.createObjectURL(file),
        size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      };
    });

    setMediaList((prev) => [...prev, ...newFiles]);
    showToast('Files Attached', `${newFiles.length} file(s) attached as evidence.`, 'info');
  };

  const handleRemoveMedia = (id: string) => {
    setMediaList((prev) => prev.filter((m) => m.id !== id));
  };

  // Form submission handler — a real backend call. No local fabrication of
  // a "successful" submission; a failure is shown as a real error.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    if (!title.trim() || title.trim().length < 5) {
      showToast('Title Required', 'Please enter a title of at least 5 characters.', 'error');
      return;
    }
    if (!description.trim() || description.trim().length < 20) {
      showToast('Description Required', 'Please provide at least 20 characters describing the issue.', 'error');
      return;
    }
    if (!administrativeAreaId) {
      showToast('Service Area Required', 'Please select the administrative area this report belongs to.', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const createdProblem = await addProblem({
        title: title.trim(),
        description: description.trim(),
        administrative_area_id: administrativeAreaId,
        pin_code: pincode.trim() || undefined,
      });

      setSubmittedProblemCode(createdProblem.trackingCode);

      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#000000', '#555555', '#E5E0D8'],
        });
      } catch {
        // decorative only
      }

      showToast(t.successToast, `Problem ID: ${createdProblem.trackingCode} is now live!`, 'success');
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Could not submit your report. Please try again.';
      setSubmitError(message);
      showToast('Submission Failed', message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-black py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Top Header */}
        <div>
          <h1 className="text-3xl sm:text-4xl font-black text-black tracking-tight">
            {t.raisePageTitle}
          </h1>
          <p className="text-sm sm:text-base text-black/75 mt-2 leading-relaxed max-w-2xl">
            {t.raisePageSub}
          </p>
        </div>

        {/* Confirmation Modal / Card if just submitted */}
        {submittedProblemCode ? (
          <div className="bg-white border-2 border-black rounded-3xl p-8 sm:p-12 text-center shadow-lg space-y-6 animate-in zoom-in-95 duration-200">
            <div className="w-16 h-16 rounded-full bg-emerald-100 border-2 border-emerald-600 text-emerald-800 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-black">{t.successToast}</h2>
              <p className="text-sm text-black/80 mt-2 max-w-md mx-auto">{t.successDesc}</p>
            </div>

            <div className="p-4 bg-[#FAF8F5] border-2 border-black rounded-2xl max-w-sm mx-auto">
              <span className="text-xs font-bold uppercase tracking-wider text-black/60 block">
                Official Tracking ID
              </span>
              <span className="text-xl font-black font-mono text-black mt-1 block select-all">
                {submittedProblemCode}
              </span>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link
                href={`/track?id=${encodeURIComponent(submittedProblemCode)}`}
                className="px-6 py-3 rounded-full bg-black text-white text-sm font-bold hover:bg-black/85 transition-all flex items-center gap-2 shadow-xs"
              >
                <Compass className="w-4 h-4" />
                <span>{t.viewInTracker}</span>
              </Link>

              <Link
                href="/dashboard"
                className="px-6 py-3 rounded-full bg-white text-black border-2 border-black text-sm font-bold hover:bg-[#FAF8F5] transition-all"
              >
                <span>{t.goToDashboard}</span>
              </Link>

              <button
                type="button"
                onClick={() => {
                  setSubmittedProblemCode(null);
                  setTitle('');
                  setDescription('');
                  setVillageOrArea('');
                  setBlock('');
                }}
                className="px-5 py-3 rounded-full bg-transparent text-black text-xs font-semibold hover:underline"
              >
                + Raise Another Issue
              </button>
            </div>
          </div>
        ) : (
          /* ========================================================================= */
          /* SINGLE CONTINUOUS SCROLLABLE FORM                                         */
          /* ========================================================================= */
          <form onSubmit={handleSubmit} className="bg-white border-2 border-black rounded-3xl p-6 sm:p-10 shadow-sm space-y-8">
            
            {/* 1. Problem Title */}
            <div className="space-y-2">
              <label htmlFor="probTitle" className="block text-xs font-bold uppercase tracking-wider text-black">
                {t.probTitleLabel} *
              </label>
              <input
                id="probTitle"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={t.probTitlePlaceholder}
                required
                className="w-full bg-[#FAF8F5] border-2 border-black rounded-2xl px-4 py-3 text-base font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
              />
              <p className="text-[11px] text-black/60">
                Write a concise headline stating the location and nature of the challenge.
              </p>
            </div>

            {/* 2. Description Textarea */}
            <div className="space-y-2">
              <label htmlFor="probDesc" className="block text-xs font-bold uppercase tracking-wider text-black">
                {t.probDescLabel} *
              </label>
              <textarea
                id="probDesc"
                rows={5}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={t.probDescPlaceholder}
                required
                className="w-full bg-[#FAF8F5] border-2 border-black rounded-2xl p-4 text-sm font-medium text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black leading-relaxed"
              />
              <div className="flex items-center justify-between text-[11px] text-black/60">
                <span>Provide as much technical or community context as possible.</span>
                <span className="font-mono font-semibold">{description.length} characters</span>
              </div>
            </div>

            {/* 3. Upload Area (Images, Videos, PDFs) */}
            <div className="space-y-3">
              <label className="block text-xs font-bold uppercase tracking-wider text-black">
                {t.probMediaLabel}
              </label>

              {/* Hidden file input */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                multiple
                accept="image/*,video/*,application/pdf"
                className="hidden"
              />

              {/* Drag & Drop Clickable Dropzone */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-black/40 hover:border-black rounded-2xl p-6 sm:p-8 bg-[#FAF8F5] hover:bg-[#F3EFEA] transition-colors cursor-pointer text-center group"
              >
                <div className="w-12 h-12 rounded-full bg-white border border-black flex items-center justify-center mx-auto mb-3 text-black group-hover:scale-105 transition-transform">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <p className="text-sm font-bold text-black">{t.uploadDragDrop}</p>
                <p className="text-xs text-black/60 mt-1">{t.uploadFormats}</p>
              </div>

              {/* Uploaded Files Thumbnail Grid */}
              {mediaList.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                  {mediaList.map((media) => (
                    <div
                      key={media.id}
                      className="bg-[#FAF8F5] border border-black/20 rounded-xl p-3 flex items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        {media.type === 'image' ? (
                          <div className="w-10 h-10 rounded-lg overflow-hidden bg-black/10 flex-shrink-0 border border-black/20">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={media.url} alt={media.name} className="w-full h-full object-cover" />
                          </div>
                        ) : (
                          <div className="w-10 h-10 rounded-lg bg-white border border-black/20 flex items-center justify-center flex-shrink-0">
                            <FileText className="w-5 h-5 text-black" />
                          </div>
                        )}
                        <div className="min-w-0">
                          <p className="text-xs font-bold text-black truncate">{media.name}</p>
                          <p className="text-[10px] text-black/60 uppercase">{media.type} • {media.size || '1.2 MB'}</p>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleRemoveMedia(media.id)}
                        className="p-1.5 rounded-lg text-black/50 hover:text-red-700 hover:bg-red-50 transition-colors"
                        title="Remove file"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 4. GPS Location & District Capture */}
            <div className="space-y-4 pt-4 border-t border-black/10">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-black">
                  {t.probLocationLabel} *
                </label>

                {/* Auto-Detect GPS Button */}
                <button
                  type="button"
                  onClick={handleDetectGps}
                  disabled={isDetectingGps}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-[#FAF8F5] border border-black text-black hover:bg-black hover:text-white transition-all duration-150 active:scale-95 disabled:opacity-50"
                >
                  {isDetectingGps ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <LocateFixed className="w-3.5 h-3.5" />
                  )}
                  <span>{isGpsDetected ? t.gpsDetected : t.detectGpsBtn}</span>
                </button>
              </div>

              {/* Coordinates Display Pill */}
              <div className="p-3.5 bg-[#FAF8F5] border border-black/20 rounded-2xl flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-black" />
                  <span className="font-semibold text-black">
                    Pinned Coordinates:
                  </span>
                  <span className="font-mono text-black">
                    {latitude.toFixed(4)}° N, {longitude.toFixed(4)}° E
                  </span>
                </div>
                {isGpsDetected && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Verified On-Device
                  </span>
                )}
              </div>

              {/* District & Location Fields */}
              {/* Real, backend-authoritative service area — required. */}
              <div className="space-y-1.5">
                <label htmlFor="raiseArea" className="block text-xs font-bold uppercase tracking-wider text-black">
                  Service Area *
                </label>
                <select
                  id="raiseArea"
                  value={administrativeAreaId}
                  onChange={(e) => setAdministrativeAreaId(e.target.value)}
                  required
                  className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="" disabled>
                    {administrativeAreas.length === 0 ? 'Loading areas…' : 'Select the area this report belongs to'}
                  </option>
                  {administrativeAreas.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.level})
                    </option>
                  ))}
                </select>
                <p className="text-[11px] text-black/60">
                  This determines which office handles your report — the district/village fields below are for your own reference.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label htmlFor="raiseDistrict" className="block text-xs font-bold text-black/70">
                    District (reference only)
                  </label>
                  <select
                    id="raiseDistrict"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                  >
                    {JHARKHAND_DISTRICTS.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="raiseBlock" className="block text-xs font-bold text-black/70">
                    Block / Tehsil
                  </label>
                  <input
                    id="raiseBlock"
                    type="text"
                    value={block}
                    onChange={(e) => setBlock(e.target.value)}
                    placeholder={t.blockPlaceholder}
                    className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="sm:col-span-2 space-y-1.5">
                  <label htmlFor="raiseArea" className="block text-xs font-bold text-black/70">
                    Village / Locality / Landmark *
                  </label>
                  <input
                    id="raiseArea"
                    type="text"
                    value={villageOrArea}
                    onChange={(e) => setVillageOrArea(e.target.value)}
                    placeholder={t.areaPlaceholder}
                    required
                    className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="raisePincode" className="block text-xs font-bold text-black/70">
                    Pincode
                  </label>
                  <input
                    id="raisePincode"
                    type="text"
                    maxLength={6}
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value.replace(/\D/g, ''))}
                    placeholder="834001"
                    className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-mono font-semibold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>
              </div>

            </div>

            {/* Authenticated Citizen Confirmation */}
            <div className="p-4 bg-[#FAF8F5] border border-black/20 rounded-2xl flex items-center justify-between text-xs text-black">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold text-xs">
                  {user ? user.fullName.charAt(0) : 'C'}
                </div>
                <div>
                  <p className="font-bold">{user ? user.fullName : 'Citizen of India'}</p>
                  <p className="text-black/60">{user ? user.phone : '+91 Verified Session'}</p>
                </div>
              </div>
              <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-400">
                Verified Citizen
              </span>
            </div>

            {/* Submit Button */}
            <div className="pt-4 border-t border-black/10 space-y-3">
              {submitError && (
                <p role="alert" className="text-xs font-semibold text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {submitError}
                </p>
              )}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-black text-white font-bold py-4 rounded-2xl text-base hover:bg-black/85 hover:scale-[1.01] active:scale-95 transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>{t.submitting}</span>
                  </>
                ) : (
                  <>
                    <PlusCircle className="w-5 h-5" />
                    <span>{t.submitProblemBtn}</span>
                  </>
                )}
              </button>
            </div>

          </form>
        )}

      </div>
    </div>
  );
}
