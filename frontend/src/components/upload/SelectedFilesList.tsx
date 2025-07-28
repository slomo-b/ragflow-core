import React from 'react';
import { File, X, Loader2 } from 'lucide-react';
import { formatFileSize } from '@/utils/format';

interface SelectedFilesListProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  onUpload: (files: File[]) => void;
  uploading: boolean;
  backendConnected: boolean;
}

export function SelectedFilesList({ 
  files, 
  onFilesChange, 
  onUpload, 
  uploading, 
  backendConnected 
}: SelectedFilesListProps) {
  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    onFilesChange([]);
  };

  return (
    <div className="mt-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Selected Files</h3>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="space-y-2">
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center space-x-2">
                <File className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">{file.name}</span>
                <span className="text-xs text-gray-500">({formatFileSize(file.size)})</span>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="p-1 rounded hover:bg-gray-200"
                disabled={uploading}
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-end space-x-2">
          <button
            onClick={clearAll}
            disabled={uploading}
            className="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
          >
            Clear All
          </button>
          <button
            onClick={() => onUpload(files)}
            disabled={uploading || !backendConnected}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            {uploading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{uploading ? 'Uploading...' : 'Upload Files'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
