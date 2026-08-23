'use client';

import React, { useEffect } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export const Toast: React.FC = () => {
  const { toast, hideToast } = useAppStore();

  useEffect(() => {
    if (toast?.show) {
      const timer = setTimeout(() => {
        hideToast();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [toast, hideToast]);

  if (!toast?.show) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-md w-[calc(100vw-3rem)] animate-in fade-in slide-in-from-bottom-5 duration-200">
      <div className="bg-white border-2 border-black rounded-xl p-4 shadow-xl flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {toast.type === 'success' && <CheckCircle2 className="w-5 h-5 text-black" />}
          {toast.type === 'error' && <AlertCircle className="w-5 h-5 text-red-600" />}
          {toast.type === 'info' && <Info className="w-5 h-5 text-black" />}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-bold text-black leading-tight">{toast.title}</h4>
          <p className="text-xs text-black/80 mt-1 leading-normal">{toast.message}</p>
        </div>
        <button
          type="button"
          onClick={hideToast}
          className="flex-shrink-0 p-1 text-black/60 hover:text-black hover:bg-black/5 rounded-lg transition-colors"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
