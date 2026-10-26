import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { searchCatalog } from '../api/client';

export default function SearchBar({ onSearch, initialQuery = '' }) {
  const [searchTerm, setSearchTerm] = useState(initialQuery);
  const [suggestions, setSuggestions] = useState([]);
  const [isSearchingSuggestions, setIsSearchingSuggestions] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Debounced catalog search for suggestions
  useEffect(() => {
    if (!searchTerm.trim() || searchTerm.length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearchingSuggestions(true);
      try {
        const results = await searchCatalog(searchTerm);
        setSuggestions(results);
        setShowDropdown(true);
      } catch (err) {
        console.error('Failed to fetch catalog suggestions:', err);
      } finally {
        setIsSearchingSuggestions(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e?.preventDefault();
    setShowDropdown(false);
    onSearch(searchTerm);
  };

  const handleSelectSuggestion = (productName) => {
    setSearchTerm(productName);
    setShowDropdown(false);
    onSearch(productName);
  };

  const handleClear = () => {
    setSearchTerm('');
    setSuggestions([]);
    setShowDropdown(false);
    onSearch('');
  };

  return (
    <div className="search-section" ref={dropdownRef}>
      <form onSubmit={handleSubmit} className="search-form" role="search" aria-label="Search local review catalog">
        <div className="search-input-wrapper">
          <Search className="search-icon" size={18} aria-hidden="true" />
          <input
            type="text"
            className="search-input"
            placeholder="Search a category or product (e.g. 'All Beauty', 'Appliances', 'ice maker')"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => { if (suggestions.length > 0) setShowDropdown(true); }}
            aria-autocomplete="list"
            aria-expanded={showDropdown}
            aria-label="Search product reviews"
          />
          {isSearchingSuggestions && (
            <div className="search-spinner" aria-label="Searching catalog">
              <Loader2 size={16} className="spin" />
            </div>
          )}
          {searchTerm && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={handleClear}
              aria-label="Clear search input"
            >
              <X size={16} />
            </button>
          )}
        </div>
        <button type="submit" className="search-submit-btn">
          Analyze Reviews
        </button>
      </form>

      {/* Suggestion Dropdown */}
      {showDropdown && suggestions.length > 0 && (
        <ul className="suggestions-dropdown" role="listbox">
          {suggestions.map((item) => (
            <li
              key={item.id}
              className="suggestion-item flex-between"
              onClick={() => handleSelectSuggestion(item.name)}
              role="option"
              aria-selected="false"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter') handleSelectSuggestion(item.name); }}
            >
              <div>
                <span className="suggestion-name">{item.name}</span>
                <span className="suggestion-meta"> in {item.category}</span>
              </div>
              <div className="suggestion-badges flex-center">
                <span className="badge-subtle">{item.total_reviews} reviews</span>
                {item.platforms?.map((p) => (
                  <span key={p} className={`badge-platform-tiny platform-${p.toLowerCase()}`}>{p}</span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
