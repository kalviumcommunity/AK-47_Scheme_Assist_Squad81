import React, { useState, useMemo } from 'react';
import { Search, Filter, SlidersHorizontal, Sparkles, X } from 'lucide-react';
import SchemeCard from '../../components/dashboard/SchemeCard';
import Input from '../../components/ui/Input';
import Select from '../../components/ui/Select';
import EmptyState from '../../components/ui/EmptyState';
import { SCHEMES, SCHEME_CATEGORIES, GOVERNMENT_TYPES } from '../../data/schemesData';

export function SchemeDiscoveryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedGovt, setSelectedGovt] = useState('All Governments');
  const [savedSchemes, setSavedSchemes] = useState(['pm-kisan']);

  const filteredSchemes = useMemo(() => {
    return SCHEMES.filter((scheme) => {
      const matchesSearch =
        scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scheme.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scheme.category.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCat =
        selectedCategory === 'All Categories' || scheme.category === selectedCategory;

      const matchesGovt =
        selectedGovt === 'All Governments' || scheme.governmentType.includes(selectedGovt);

      return matchesSearch && matchesCat && matchesGovt;
    });
  }, [searchQuery, selectedCategory, selectedGovt]);

  const handleToggleSave = (id) => {
    setSavedSchemes((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('All Categories');
    setSelectedGovt('All Governments');
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
          Find Government Schemes
        </h1>
        <p className="text-xs sm:text-sm text-slate-muted mt-1">
          Explore gazetted central and state schemes filtered precisely for your needs.
        </p>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white border border-slate-border rounded-card p-4 shadow-subtle space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="flex-1">
            <Input
              icon={Search}
              placeholder="Search government schemes by name, category, or benefit..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="w-full md:w-56">
            <Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              options={SCHEME_CATEGORIES}
            />
          </div>
          <div className="w-full md:w-56">
            <Select
              value={selectedGovt}
              onChange={(e) => setSelectedGovt(e.target.value)}
              options={GOVERNMENT_TYPES}
            />
          </div>
        </div>

        {/* Active Filter Chips */}
        {(searchQuery || selectedCategory !== 'All Categories' || selectedGovt !== 'All Governments') && (
          <div className="flex items-center gap-2 pt-2 border-t border-slate-border text-xs">
            <span className="text-slate-muted font-semibold">Active Filters:</span>
            {searchQuery && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary-50 text-primary border border-primary/20">
                "{searchQuery}"
                <X className="w-3 h-3 cursor-pointer" onClick={() => setSearchQuery('')} />
              </span>
            )}
            {selectedCategory !== 'All Categories' && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary-50 text-primary border border-primary/20">
                Category: {selectedCategory}
                <X className="w-3 h-3 cursor-pointer" onClick={() => setSelectedCategory('All Categories')} />
              </span>
            )}
            {selectedGovt !== 'All Governments' && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary-50 text-primary border border-primary/20">
                {selectedGovt}
                <X className="w-3 h-3 cursor-pointer" onClick={() => setSelectedGovt('All Governments')} />
              </span>
            )}
            <button
              onClick={clearFilters}
              className="text-primary hover:underline font-bold ml-auto"
            >
              Reset All
            </button>
          </div>
        )}
      </div>

      {/* Schemes Grid */}
      {filteredSchemes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSchemes.map((scheme) => (
            <SchemeCard
              key={scheme.id}
              scheme={scheme}
              isSaved={savedSchemes.includes(scheme.id)}
              onSave={handleToggleSave}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Schemes Found"
          description="No government welfare schemes matched your active query or filter criteria. Try clearing filters or searching for broad terms like 'Farmer', 'Health', or 'Housing'."
          actionText="Clear All Filters"
          onAction={clearFilters}
        />
      )}
    </div>
  );
}

export default SchemeDiscoveryPage;
