'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAppStore } from '@/store/useAppStore';
import { authApi } from '@/lib/api/authApi';
import { translations } from '@/lib/translations';
import {
  sendMsg91Otp,
  verifyMsg91Otp,
  retryMsg91Otp,
  Msg91WidgetError,
} from '@/lib/msg91Widget';
import {
  KeyRound,
  ArrowRight,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { language, user, completeLogin, showToast } = useAppStore();
  const t = translations[language];

  // Steps: 1: Phone -> 2: OTP. Real MSG91 verification only — no local
  // "profile details" step, since the backend has nothing to store one in.
  const [step, setStep] = useState<1 | 2>(1);
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');

  const [resendTimer, setResendTimer] = useState(30);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // PRESENTATION-ONLY. OFF unless the deployment explicitly sets
  // NEXT_PUBLIC_DEMO_MODE=true at build time — this flag only shows/hides
  // the button; the backend independently re-checks its own DEMO_MODE
  // (404s the demo endpoint otherwise), so this can never grant access by
  // itself. Never triggered automatically by a real OTP failure.
  const demoModeAvailable = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';
  const [isDemoSubmitting, setIsDemoSubmitting] = useState(false);

  async function handleDemoLogin() {
    setError(null);
    setIsDemoSubmitting(true);
    try {
      await authApi.demoLogin('citizen');
      await completeLogin();
      showToast('Demo Session', 'Signed in as a presentation demo citizen.', 'info');
      router.push('/dashboard');
    } catch {
      setError('Demo mode is not enabled on this backend.');
    } finally {
      setIsDemoSubmitting(false);
    }
  }

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (step === 2 && resendTimer > 0) {
      interval = setInterval(() => setResendTimer((prev) => prev - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [step, resendTimer]);

  async function handleSendOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const digits = phone.replace(/\D/g, '');
    if (digits.length !== 10) {
      setError('Please enter a valid 10-digit Indian mobile number.');
      return;
    }

    setIsSubmitting(true);
    try {
      // Real MSG91 Widget call — the widget itself sends the real SMS;
      // this app never generates or sees the OTP.
      await sendMsg91Otp(`91${digits}`);
      setStep(2);
      setResendTimer(30);
      showToast('OTP Sent', `A verification code has been sent to +91 ${digits}.`, 'info');
    } catch (err) {
      setError(err instanceof Msg91WidgetError ? err.message : 'Could not send the OTP. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleVerifyOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (otp.length < 4) {
      setError('Please enter the verification code.');
      return;
    }

    setIsSubmitting(true);
    try {
      // 1. MSG91 verifies the OTP itself and returns an access-token.
      const accessToken = await verifyMsg91Otp(otp);
      // 2. Our backend independently re-verifies that token with MSG91
      //    server-side before issuing a SocioSolve session, the phone number
      //    is never taken on the client's word.
      await authApi.verifyMsg91AccessToken(accessToken);
      await completeLogin();
      showToast('Verified', 'You are signed in.', 'success');
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Msg91WidgetError ? err.message : 'Sign-in failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleResend() {
    setError(null);
    try {
      await retryMsg91Otp();
      setResendTimer(30);
      showToast('OTP Resent', 'A new verification code has been dispatched.', 'info');
    } catch (err) {
      setError(err instanceof Msg91WidgetError ? err.message : 'Could not resend the OTP.');
    }
  }

  return (
    <div className="min-h-[calc(100vh-140px)] w-full bg-[#FAF8F5] py-10 sm:py-16 px-4 sm:px-6 lg:px-8 flex flex-col justify-center items-center">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-black tracking-tight">
            {t.loginHeading}
          </h1>
          <p className="text-xs sm:text-sm text-black/75 mt-2 leading-relaxed">
            {t.loginSubheading}
          </p>
        </div>

        {user && (
          <div className="mb-6 bg-white border-2 border-black rounded-2xl p-4 shadow-xs flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center font-bold text-sm">
                {user.fullName.charAt(0)}
              </div>
              <div>
                <p className="text-sm font-bold text-black">{user.fullName}</p>
                <p className="text-xs text-black/60 font-mono">{user.phone}</p>
              </div>
            </div>
            <Link
              href="/dashboard"
              className="px-3.5 py-1.5 rounded-full bg-black text-white text-xs font-bold hover:bg-black/80 transition-colors"
            >
              {t.dashboardNav} →
            </Link>
          </div>
        )}

        <div className="bg-white border-2 border-black rounded-2xl p-6 sm:p-8 shadow-md">
          <div className="flex items-center justify-between mb-8 pb-4 border-b border-black/10">
            <div className={`flex flex-col items-center gap-1 ${step >= 1 ? 'text-black font-bold' : 'text-black/40'}`}>
              <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-mono font-bold ${
                step >= 1 ? 'border-black bg-black text-white' : 'border-black/30 bg-white'
              }`}>
                {step > 1 ? <CheckCircle2 className="w-4 h-4 text-white" /> : '1'}
              </div>
              <span className="text-[10px] uppercase tracking-wider">Mobile</span>
            </div>
            <div className={`flex-1 h-0.5 mx-2 ${step >= 2 ? 'bg-black' : 'bg-black/20'}`} />
            <div className={`flex flex-col items-center gap-1 ${step >= 2 ? 'text-black font-bold' : 'text-black/40'}`}>
              <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-mono font-bold ${
                step >= 2 ? 'border-black bg-black text-white' : 'border-black/30 bg-white'
              }`}>
                2
              </div>
              <span className="text-[10px] uppercase tracking-wider">OTP</span>
            </div>
          </div>

          {step === 1 && (
            <form onSubmit={handleSendOtp} className="space-y-4">
              <div className="space-y-1.5">
                <label htmlFor="phoneInput" className="block text-xs font-bold uppercase tracking-wider text-black">
                  {t.mobileNumberLabel}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-black/60 font-mono text-sm font-semibold">
                    +91
                  </div>
                  <input
                    id="phoneInput"
                    type="tel"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                    placeholder="98351 04221"
                    required
                    className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl pl-14 pr-4 py-3 text-base font-mono font-bold text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>
                <p className="text-[11px] text-black/60 mt-1">
                  We will send a real one-time password via SMS to verify your Indian mobile number.
                </p>
              </div>

              {error && (
                <p role="alert" className="text-xs font-semibold text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-black text-white font-bold py-3.5 rounded-xl text-sm hover:bg-black/85 transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer active:scale-95 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>{t.sendOtpBtn}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label htmlFor="otpInput" className="block text-xs font-bold uppercase tracking-wider text-black">
                    {t.otpLabel}
                  </label>
                  <button
                    type="button"
                    onClick={() => { setStep(1); setOtp(''); setError(null); }}
                    className="text-xs text-black font-semibold hover:underline"
                  >
                    Change +91 {phone}
                  </button>
                </div>

                <input
                  id="otpInput"
                  type="text"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  required
                  className="w-full bg-[#FAF8F5] border-2 border-black rounded-xl px-4 py-3 text-xl font-mono font-bold tracking-[0.4em] text-center text-black focus:bg-white focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              {error && (
                <p role="alert" className="text-xs font-semibold text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <div className="flex items-center justify-between text-xs text-black/70 pt-1">
                {resendTimer > 0 ? (
                  <span>{t.resendOtp} <strong className="font-mono text-black">{resendTimer}s</strong></span>
                ) : (
                  <button type="button" onClick={() => void handleResend()} className="font-bold text-black hover:underline">
                    {t.resendNow}
                  </button>
                )}
              </div>

              <button
                type="submit"
                disabled={isSubmitting || otp.length < 4}
                className="w-full bg-black text-white font-bold py-3.5 rounded-xl text-sm hover:bg-black/85 transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer active:scale-95 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <KeyRound className="w-4 h-4" />
                    <span>{t.verifyOtpBtn}</span>
                  </>
                )}
              </button>
            </form>
          )}

          {demoModeAvailable && step === 1 && (
            <div className="mt-6 pt-5 border-t-2 border-dashed border-amber-400">
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2 py-0.5 rounded-full bg-amber-400 text-black text-[10px] font-black uppercase tracking-wider">
                  Demo Mode
                </span>
                <span className="text-[11px] text-black/60">Presentation only — not real authentication</span>
              </div>
              <button
                type="button"
                onClick={() => void handleDemoLogin()}
                disabled={isDemoSubmitting}
                className="w-full bg-amber-400 text-black font-bold py-3 rounded-xl text-sm hover:bg-amber-300 transition-all cursor-pointer active:scale-95 disabled:opacity-50"
              >
                {isDemoSubmitting ? 'Signing in…' : 'Continue as Demo Citizen'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
