import React from 'react';
import { FileText, Trash2 } from 'lucide-react';
import { Document } from '@/types/document';
import { StatusIcon } from '@/components/ui/StatusIcon';
import { formatFileSize, formatDate } from '@/utils/format';

interface DocumentsListProps {
  documents: Document[];
  onDelete: (documentId: string) => void;
}

export function DocumentsList({ documents, onDelete }: DocumentsListProps) {
  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-8 text-center text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p>No documents uploaded yet</p>
          <p className="text-sm mt-1">Upload your first document to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="divide-y divide-gray-200">
        {documents.map((doc) => (
          <div key={doc.id} className="p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <StatusIcon status={doc.status} />
              <div>
                <div className="font-medium text-gray-900">{doc.filename}</div>
                <div className="text-sm text-gray-500">
                  {formatFileSize(doc.file_size)} • {formatDate(doc.created_at)}
                </div>
                {doc.status === 'failed' && (
                  <div className="text-xs text-red-600 mt-1">Processing failed</div>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                doc.status === 'completed' ? 'bg-green-100 text-green-800' :
                doc.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                doc.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {doc.status}
              </span>
              <button 
                onClick={() => onDelete(doc.id)}
                className="p-1 rounded hover:bg-gray-100"
                title="Delete document"
              >
                <Trash2 className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
