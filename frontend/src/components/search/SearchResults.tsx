import React from 'react';
import { Search, MessageCircle } from 'lucide-react';
import { SearchResult, Document } from '@/types/document';
import { formatRelevanceScore } from '@/utils/format';

interface SearchResultsProps {
  results: SearchResult[];
  documents: Document[];
  query: string;
  isSearching: boolean;
}

export function SearchResults({ results, documents, query, isSearching }: SearchResultsProps) {
  if (results.length > 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">
          Found {results.length} relevant results
        </h3>
        {results.map((result, index) => (
          <div key={result.id || index} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-4">
                <div className="text-sm font-medium text-blue-600">
                  Relevance: {formatRelevanceScore(result.score)}
                </div>
                <div className="text-sm text-gray-500">
                  Document: {documents.find(d => d.id === result.document_id)?.filename || result.document_id}
                </div>
              </div>
              <div className="text-xs text-gray-400">
                Chunk {result.chunk_index}
              </div>
            </div>
            <div className="text-gray-800 leading-relaxed">
              {result.text}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (query && !isSearching) {
    return (
      <div className="text-center py-12">
        <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">No results found for your query.</p>
        <p className="text-sm text-gray-400 mt-1">Try different keywords or make sure your documents are processed.</p>
      </div>
    );
  }

  return (
    <div className="text-center py-12">
      <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
      <p className="text-gray-500">Enter a question to search through your documents.</p>
      <p className="text-sm text-gray-400 mt-1">Use natural language to find relevant information.</p>
    </div>
  );
}