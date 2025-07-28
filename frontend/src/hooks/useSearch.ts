import { useState, useCallback } from 'react';
import { SearchResult } from '@/types/document';
import { api } from '@/lib/api';

export function useSearch() {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performSearch = useCallback(async (query: string, topK = 5, documentIds?: string[]) => {
    setIsSearching(true);
    setError(null);
    
    try {
      const results = await api.semanticSearch(query, topK, documentIds);
      setSearchResults(results.results || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Search failed';
      setError(errorMessage);
      setSearchResults([]);
      throw err;
    } finally {
      setIsSearching(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setSearchResults([]);
    setError(null);
  }, []);

  return {
    searchResults,
    isSearching,
    error,
    performSearch,
    clearResults
  };
}