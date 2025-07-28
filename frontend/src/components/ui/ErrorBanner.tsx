import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorBannerProps {
  error: string;
  onClose: () => void;
}

export function ErrorBanner({ error, onClose }: ErrorBannerProps) {
  return (
    <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-6 mt-4 rounded">
      <div className="flex">
        <AlertCircle className="w-5 h-5 text-red-400" />
        <div className="ml-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
        <button 
          onClick={onClose}
          className="ml-auto text-red-400 hover:text-red-600"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}