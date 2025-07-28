import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';
import { SystemStatus } from '@/types/document';

interface ServicesStatusProps {
  systemStatus: SystemStatus;
}

export function ServicesStatus({ systemStatus }: ServicesStatusProps) {
  const getServiceIcon = (status: string) => {
    return status === 'healthy' || status === 'available' 
      ? <CheckCircle className="w-4 h-4 text-green-500" />
      : <AlertCircle className="w-4 h-4 text-red-500" />;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Services Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(systemStatus.services).map(([service, status]) => (
          <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <div className="flex items-center space-x-2">
              {getServiceIcon(status)}
              <span className="font-medium capitalize">{service.replace('_', ' ')}</span>
            </div>
            <span className={`text-sm font-medium ${
              status === 'healthy' || status === 'available' ? 'text-green-600' : 'text-red-600'
            }`}>
              {status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}