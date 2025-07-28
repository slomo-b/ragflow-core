import React from 'react';
import { Activity, FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Document, SystemStatus } from '@/types/document';
import { SystemInfo } from '@/components/admin/SystemInfo';
import { ServicesStatus } from '@/components/admin/ServicesStatus';

interface AdminTabProps {
  documents: Document[];
  systemStatus: SystemStatus | null;
  backendConnected: boolean;
}

export function AdminTab({ documents, systemStatus, backendConnected }: AdminTabProps) {
  const completedCount = documents.filter(d => d.status === 'completed').length;
  const processingCount = documents.filter(d => d.status === 'processing').length;
  const failedCount = documents.filter(d => d.status === 'failed').length;

  return (
    <div className="flex-1 p-6">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h2>
        
        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <Activity className={`w-8 h-8 ${backendConnected ? 'text-green-500' : 'text-red-500'}`} />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Backend Status</p>
                <p className={`text-lg font-semibold ${backendConnected ? 'text-green-600' : 'text-red-600'}`}>
                  {backendConnected ? 'Connected' : 'Disconnected'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-lg font-semibold text-gray-900">{documents.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Processed</p>
                <p className="text-lg font-semibold text-gray-900">{completedCount}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Processing</p>
                <p className="text-lg font-semibold text-gray-900">{processingCount}</p>
              </div>
            </div>
          </div>
        </div>

        {/* System Information */}
        {systemStatus && (
          <>
            <SystemInfo systemStatus={systemStatus} />
            <ServicesStatus systemStatus={systemStatus} />
          </>
        )}

        {/* Document Status Breakdown */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Document Status Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{completedCount}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{processingCount}</div>
              <div className="text-sm text-gray-600">Processing</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {documents.filter(d => d.status === 'pending').length}
              </div>
              <div className="text-sm text-gray-600">Pending</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{failedCount}</div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
