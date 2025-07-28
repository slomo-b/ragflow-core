import React, { useState } from 'react';
import { Upload } from 'lucide-react';

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  maxFileSize: number;
}

export function FileUploadZone({ onFilesSelected, maxFileSize }: FileUploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const files = Array.from(e.dataTransfer.files);
    onFilesSelected(files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    onFilesSelected(files);
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Drop files here</h3>
      <p className="text-gray-500 mb-4">or click to browse</p>
      
      <input
        type="file"
        multiple
        className="hidden"
        id="file-upload"
        onChange={handleFileSelect}
        accept=".pdf,.docx,.txt,.md,.html"
      />
      <label
        htmlFor="file-upload"
        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
      >
        Choose Files
      </label>
      <p className="text-sm text-gray-400 mt-2">
        Supports PDF, DOCX, TXT, Markdown, HTML • Max {maxFileSize}MB per file
      </p>
    </div>
  );
}
