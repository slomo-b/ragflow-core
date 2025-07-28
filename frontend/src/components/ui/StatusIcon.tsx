import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader2, File } from 'lucide-react';
import { Document } from '@/types/document';

interface StatusIconProps {
  status: Document['status'];
}

export function StatusIcon({ status }: StatusIconProps) {
  switch (status) {
    case 'completed': 
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case 'processing': 
      return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
    case 'pending': 
      return <Clock className="w-4 h-4 text-yellow-500" />;
    case 'failed': 
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    default: 
      return <File className="w-4 h-4 text-gray-500" />;
  }
}