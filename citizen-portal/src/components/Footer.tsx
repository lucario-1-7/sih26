'use client';

import React from 'react';
import Link from 'next/link';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/lib/translations';
import { PhoneCall, Mail, MapPin, ShieldCheck, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  const language = useAppStore((state) => state.language);
  const t = translations[language];

  return (
    <footer className="w-full bg-[#FAF8F5] border-t border-black/15 pt-14 pb-10 px-6 sm:px-10 lg:px-16 text-black transition-colors">
      <div className="w-full max-w-7xl mx-auto">
        
        {/* Main 4-Column Footer Grid without duplicate official logos */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12 pb-10 border-b border-black/10">
          
          {/* Col 1: SocioSolve Brand Mission */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span
                className="text-2xl font-bold tracking-tight font-serif-italic text-black"
                style={{ fontFamily: 'var(--font-serif), "Playfair Display", Georgia, serif' }}
              >
                SocioSolve
              </span>
            </div>
            <p className="text-xs text-black/75 leading-relaxed max-w-xs">
              {t.heroSubtext}
            </p>
            <div className="inline-flex items-center gap-2 text-xs font-semibold text-black bg-white border border-black/20 px-3 py-1.5 rounded-lg shadow-2xs">
              <ShieldCheck className="w-4 h-4 text-emerald-700 flex-shrink-0" />
              <span>{t.jharkhandBadge}</span>
            </div>
          </div>

          {/* Col 2: Toll-Free Citizen Helpline & Support Email */}
          <div className="space-y-4">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-black/60 mb-2">
                {t.footerHelpline}
              </h4>
              <a
                href={`tel:${t.footerPhone}`}
                className="inline-flex items-center gap-3 text-base font-bold text-black hover:underline group"
              >
                <div className="w-8 h-8 rounded-full bg-black text-white flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                  <PhoneCall className="w-4 h-4 text-white" />
                </div>
                <span className="font-mono tracking-tight text-base sm:text-lg">{t.footerPhone}</span>
              </a>
              <p className="text-[11px] text-black/70 mt-1 pl-11">
                Mon - Sat: 9:00 AM - 6:00 PM IST (Toll-Free)
              </p>
            </div>

            <div className="pt-2 border-t border-black/10">
              <h4 className="text-xs font-bold uppercase tracking-wider text-black/60 mb-1">
                {t.footerEmailLabel}
              </h4>
              <a
                href={`mailto:${t.footerEmail}`}
                className="inline-flex items-center gap-2 text-sm font-semibold text-black hover:underline font-mono"
              >
                <Mail className="w-4 h-4 text-black/70 flex-shrink-0" />
                <span>{t.footerEmail}</span>
              </a>
            </div>
          </div>

          {/* Col 3: Quick Portal Navigation */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-black/60">
              {t.quickLinks}
            </h4>
            <ul className="space-y-2 text-xs sm:text-sm font-medium">
              <li>
                <Link href="/" className="hover:underline hover:text-black block py-0.5">
                  {t.homeNav}
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:underline hover:text-black block py-0.5">
                  {t.dashboardNav}
                </Link>
              </li>
              <li>
                <Link href="/raise" className="hover:underline hover:text-black block py-0.5">
                  {t.raiseNav}
                </Link>
              </li>
              <li>
                <Link href="/track" className="hover:underline hover:text-black block py-0.5">
                  {t.trackNav}
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:underline hover:text-black block py-0.5">
                  {t.login} / Verification
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: State Nodal Guidelines & Address */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-black/60">
              {t.nodalGuidelines}
            </h4>
            <div className="flex items-start gap-2 text-xs text-black/80 leading-relaxed">
              <MapPin className="w-4 h-4 text-black flex-shrink-0 mt-0.5" />
              <span>{t.footerAddress}</span>
            </div>
            <div className="pt-2 text-[11px] text-black/60 space-y-1">
              <p>State Nodal Agency: Directorate of Higher & Technical Education</p>
              <p>Academic Network: IIT ISM, BIT Mesra, NIT JSR, BAU, AIIMS</p>
            </div>
          </div>

        </div>

        {/* Bottom Bar: Copyright & Privacy */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-black/75">
          <p className="text-center sm:text-left">{t.footerRights}</p>
          <div className="flex items-center gap-4">
            <span className="hover:underline cursor-pointer">{t.privacyPolicy}</span>
            <span>•</span>
            <span className="hover:underline cursor-pointer">{t.termsOfUse}</span>
          </div>
        </div>

      </div>
    </footer>
  );
};
