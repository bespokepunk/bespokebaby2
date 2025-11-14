'use client';

import { motion } from 'framer-motion';
import { useState, useEffect, useRef, useCallback } from 'react';
import Image from 'next/image';
import punkNames from '@/public/punk-names.json';

export default function GalleryPage() {
  const [filter, setFilter] = useState<'all' | 'lad' | 'lady'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [visiblePunks, setVisiblePunks] = useState(60);
  const observerTarget = useRef<HTMLDivElement>(null);

  // Randomize punk order for display
  const allPunks = [...punkNames].sort(() => Math.random() - 0.5);

  const filteredPunks = allPunks.filter(punk => {
    const matchesFilter = filter === 'all' || punk.startsWith(filter);
    const punkName = punk.split('_').slice(2).join('_');
    const matchesSearch = punkName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          punk.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const displayedPunks = filteredPunks.slice(0, visiblePunks);

  const loadMore = useCallback(() => {
    if (visiblePunks < filteredPunks.length) {
      setVisiblePunks(prev => Math.min(prev + 30, filteredPunks.length));
    }
  }, [visiblePunks, filteredPunks.length]);

  useEffect(() => {
    setVisiblePunks(60);
  }, [filter, searchTerm]);

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { threshold: 0.5 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [loadMore]);

  return (
    <div className="min-h-screen py-16 px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-16"
        >
          <p className="text-xs tracking-wider uppercase text-stone-500 mb-3">Collection</p>
          <h1 className="serif text-5xl sm:text-6xl md:text-7xl mb-6">
            The Collection
          </h1>
          <p className="text-lg text-stone-600 dark:text-stone-400 max-w-2xl mb-4">
            174 portraits, hand-selected from 250+ variants. Each one represents someone real.
          </p>
          <p className="text-sm text-stone-500 dark:text-stone-500 max-w-2xl italic">
            Look closely—you might spot a few familiar faces. Some honoraries have multiple characters in the collection.
          </p>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-12 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center"
        >
          <div className="flex gap-3">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 text-sm tracking-wide transition-all ${
                filter === 'all'
                  ? 'border-b-2 border-stone-900 dark:border-stone-100'
                  : 'text-stone-500 hover:text-stone-900 dark:hover:text-stone-100'
              }`}
            >
              All ({allPunks.length})
            </button>
            <button
              onClick={() => setFilter('lad')}
              className={`px-4 py-2 text-sm tracking-wide transition-all ${
                filter === 'lad'
                  ? 'border-b-2 border-stone-900 dark:border-stone-100'
                  : 'text-stone-500 hover:text-stone-900 dark:hover:text-stone-100'
              }`}
            >
              Lads
            </button>
            <button
              onClick={() => setFilter('lady')}
              className={`px-4 py-2 text-sm tracking-wide transition-all ${
                filter === 'lady'
                  ? 'border-b-2 border-stone-900 dark:border-stone-100'
                  : 'text-stone-500 hover:text-stone-900 dark:hover:text-stone-100'
              }`}
            >
              Ladies
            </button>
          </div>

          <input
            type="text"
            placeholder="Search by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-4 py-2 text-sm border border-stone-300 dark:border-stone-700 rounded-none bg-transparent focus:outline-none focus:border-stone-900 dark:focus:border-stone-100 w-full sm:w-64"
          />
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mb-12 pb-8 border-b border-stone-200 dark:border-stone-800"
        >
          <p className="text-sm text-stone-600 dark:text-stone-400">
            Showing {displayedPunks.length} of {filteredPunks.length} punks
          </p>
        </motion.div>

        {/* Gallery Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {displayedPunks.map((punk, i) => {
              const punkId = punk.split('_').slice(0, 2).join(' #').replace('_', ' ');
              return (
                <motion.div
                  key={punk}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: Math.min(i * 0.02, 0.5) }}
                  className="group"
                >
                  <div className="aspect-square relative overflow-hidden bg-stone-100 dark:bg-stone-900 hover-lift cursor-pointer border border-stone-200 dark:border-stone-800">
                    <Image
                      src={`/punks-display/${punk}.png`}
                      alt={punkId}
                      width={512}
                      height={512}
                      className="w-full h-full object-cover pixel-perfect group-hover:scale-105 transition-transform duration-500"
                      loading="lazy"
                    />
                  </div>
                  <p className="mt-2 text-xs tracking-wide text-stone-600 dark:text-stone-400 truncate">
                    {punkId}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Infinite scroll trigger */}
        {displayedPunks.length < filteredPunks.length && (
          <div ref={observerTarget} className="mt-16 text-center py-8">
            <p className="text-sm text-stone-400 animate-pulse">
              Loading more punks...
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
