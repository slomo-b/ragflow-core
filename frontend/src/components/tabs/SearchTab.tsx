import React, { useState } from 'react';
import { Search, MessageCircle, Loader2 } from 'lucide-react';
import { Document, SearchResult } from '@/types/document';
import { SearchInput } from '@/components/search/SearchInput';
import { SearchResults } from '@/components/search/SearchResults';
import { useSearch } from '@/hooks/useSearch';

interface SearchTabProps {
  documents: Document[];
  backendConnected: boolean;
  onError: (error: string) => void;
}

export function SearchTab({ documents, backendConnected, onError }: SearchTabProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const { searchResults, isSearching, performSearch } = useSearch();

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      await performSearch(searchQuery, 10);
    } catch (error) {
      onError(`Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const processedDocuments = documents.filter(d => d.status === 'completed');

  return (
    <div className="flex-1 flex flex-col">
      {/* Search Header */}
      <div className="border-b border-gray-200 p-6 bg-white">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Semantic Search</h2>
        
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          onSearch={handleSearch}
          isSearching={isSearching}
          disabled={!backendConnected}
        />
        
        {processedDocuments.length === 0 && (
          <p className="text-sm text-yellow-600 mt-2">
            No processed documents available for search. Upload and process documents first.
          </p>
        )}
      </div>

      {/* Search Results */}
      <div className="flex-1 p-6 overflow-y-auto">
        <SearchResults
          results={searchResults}
          documents={documents}
          query={searchQuery}
          isSearching={isSearching}
        />
      </div>
    </div>
  );
}
