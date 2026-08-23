'use client';

import React from 'react';
import Image from 'next/image';

export const SocioSolveLogo: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`inline-flex items-center justify-center select-none font-serif-italic font-normal tracking-tight text-black ${className}`}
      style={{
        fontFamily: 'var(--font-serif), "Playfair Display", "Times New Roman", Georgia, serif',
      }}
    >
      {/* S */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        S
      </span>

      {/* 1st O: Official Government of Jharkhand Seal from /1st O.jpeg */}
      <span className="inline-flex items-center justify-center mx-[0.03em] -translate-y-[0.02em] group">
        <span className="relative w-[3.2rem] h-[3.2rem] sm:w-[4.6rem] sm:h-[4.6rem] md:w-[5.8rem] md:h-[5.8rem] lg:w-[6.8rem] lg:h-[6.8rem] rounded-full overflow-hidden inline-block transition-transform duration-300 group-hover:scale-105">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/1st O.jpeg"
            alt="Government of Jharkhand Seal"
            className="w-full h-full object-cover grayscale contrast-125 hover:grayscale-0 transition-all duration-300"
          />
        </span>
      </span>

      {/* c */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        c
      </span>

      {/* i */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        i
      </span>

      {/* o */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        o
      </span>

      {/* S */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6 ml-[0.02em]">
        S
      </span>

      {/* 2nd O: Brain & Circuit Lightbulb Innovation Icon from /2nd O.jpeg */}
      <span className="inline-flex items-center justify-center mx-[0.03em] -translate-y-[0.02em] group">
        <span className="relative w-[3.2rem] h-[3.2rem] sm:w-[4.6rem] sm:h-[4.6rem] md:w-[5.8rem] md:h-[5.8rem] lg:w-[6.8rem] lg:h-[6.8rem] rounded-full overflow-hidden inline-block transition-transform duration-300 group-hover:scale-105">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/2nd O.jpeg"
            alt="Innovation & Brain Circuit Emblem"
            className="w-full h-full object-cover grayscale contrast-125 hover:grayscale-0 transition-all duration-300"
          />
        </span>
      </span>

      {/* l */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        l
      </span>

      {/* v */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        v
      </span>

      {/* e */}
      <span className="text-[4rem] sm:text-[5.8rem] md:text-[7.2rem] lg:text-[8.6rem] leading-none transform -skew-x-6">
        e
      </span>
    </div>
  );
};
