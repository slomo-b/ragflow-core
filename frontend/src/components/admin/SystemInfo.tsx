import React from 'react';
import { SystemStatus } from '@/types/document';

interface SystemInfoProps {
  systemStatus: SystemStatus;
}

export function SystemInfo({ systemStatus }: SystemInfoProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-medium text-gray-700 mb-2">General</h4>
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-600">Status:</dt>
              <dd className="font-medium">{systemStatus.status}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Version:</dt>
              <dd className="font-medium">{systemStatus.version}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Mode:</dt>
              <dd className="font-medium">{systemStatus.mode}</dd>
            </div>
          </dl>
        </div>
        
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Configuration</h4>
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-600">Max File Size:</dt>
              <dd className="font-medium">{systemStatus.configuration.max_file_size_mb}MB</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Chunk Size:</dt>
              <dd className="font-medium">{systemStatus.configuration.chunk_size}</dd>
            </div>
            {systemStatus.configuration.embedding_model && (
              <div className="flex justify-between">
                <dt className="text-gray-600">Embedding Model:</dt>
                <dd className="font-medium">{systemStatus.configuration.embedding_model}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}
