'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import punkNames from '@/public/punk-names.json';

export default function AllPunksPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showMissingOnly, setShowMissingOnly] = useState(false);

  // Generate expected punk numbers
  const generateExpectedPunks = () => {
    const expected = [];
    // Ladies 0-99, Lads 1-106
    for (let i = 0; i <= 99; i++) {
      expected.push(`lady_${i.toString().padStart(3, '0')}`);
    }
    for (let i = 1; i <= 106; i++) {
      expected.push(`lad_${i.toString().padStart(3, '0')}`);
    }
    return expected;
  };

  const expectedPunks = generateExpectedPunks();
  const existingPunkPrefixes = punkNames.map(name => {
    const parts = name.split('_');
    return `${parts[0]}_${parts[1]}`;
  });

  const missingPunks = expectedPunks.filter(prefix => !existingPunkPrefixes.includes(prefix));

  const allPunksWithStatus = [
    ...punkNames.map(name => ({ name, exists: true })),
    ...missingPunks.map(name => ({ name, exists: false }))
  ].sort((a, b) => {
    const [aType, aNum] = a.name.split('_');
    const [bType, bNum] = b.name.split('_');
    if (aType === bType) {
      return parseInt(aNum) - parseInt(bNum);
    }
    return aType.localeCompare(bType);
  });

  const filteredPunks = allPunksWithStatus.filter(punk => {
    const matchesSearch = punk.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMissingFilter = !showMissingOnly || !punk.exists;
    return matchesSearch && matchesMissingFilter;
  });

  const stats = {
    total: existingPunkPrefixes.length,
    missing: missingPunks.length,
    ladies: punkNames.filter(p => p.startsWith('lady_')).length,
    lads: punkNames.filter(p => p.startsWith('lad_')).length,
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-4xl font-bold text-[#c9a96e] mb-2">All Punks Directory</h1>
            <p className="text-[#c9a96e]/60 text-sm">Complete collection overview with missing punks highlighted</p>
          </div>
          <Link
            href="/gallery"
            className="px-6 py-3 border border-[#c9a96e]/30 text-[#c9a96e]/60 hover:border-[#c9a96e] hover:text-[#c9a96e] transition-all text-sm tracking-wider"
          >
            ← GALLERY
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#c9a96e]/10 border border-[#c9a96e]/30 p-4">
            <p className="text-xs text-[#c9a96e]/60 mb-1">TOTAL PUNKS</p>
            <p className="text-3xl font-bold text-[#c9a96e]">{stats.total}</p>
          </div>
          <div className="bg-red-900/20 border border-red-500/30 p-4">
            <p className="text-xs text-red-400/60 mb-1">MISSING</p>
            <p className="text-3xl font-bold text-red-400">{stats.missing}</p>
          </div>
          <div className="bg-blue-900/20 border border-blue-400/30 p-4">
            <p className="text-xs text-blue-400/60 mb-1">LADS</p>
            <p className="text-3xl font-bold text-blue-400">{stats.lads}</p>
          </div>
          <div className="bg-pink-900/20 border border-pink-400/30 p-4">
            <p className="text-xs text-pink-400/60 mb-1">LADIES</p>
            <p className="text-3xl font-bold text-pink-400">{stats.ladies}</p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex gap-4 mb-6 flex-wrap">
          <input
            type="text"
            placeholder="Search by name or number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 bg-black border border-[#c9a96e]/30 text-[#c9a96e] placeholder:text-[#c9a96e]/30 focus:outline-none focus:border-[#c9a96e]"
          />
          <button
            onClick={() => setShowMissingOnly(!showMissingOnly)}
            className={`px-6 py-2 transition-all ${
              showMissingOnly
                ? 'bg-red-500 text-white'
                : 'border border-[#c9a96e]/30 text-[#c9a96e]/60 hover:border-[#c9a96e] hover:text-[#c9a96e]'
            }`}
          >
            {showMissingOnly ? 'SHOWING MISSING ONLY' : 'SHOW MISSING ONLY'}
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
          {filteredPunks.map((punk) => {
            const punkId = punk.name.split('_').slice(0, 2).join('_');
            const punkNumber = punk.name.split('_')[1];
            const punkType = punk.name.split('_')[0];
            const punkFullName = punk.exists ? punk.name : `${punkId}_MISSING`;

            return (
              <div
                key={punkFullName}
                className={`aspect-square relative border-2 transition-all ${
                  punk.exists
                    ? 'border-[#c9a96e]/30 hover:border-[#c9a96e] hover:scale-105'
                    : 'border-red-500/50 bg-red-900/20'
                }`}
              >
                {punk.exists ? (
                  <>
                    <Image
                      src={`/punks-display/${punk.name}.png`}
                      alt={punk.name}
                      width={200}
                      height={200}
                      className="w-full h-full object-cover"
                      style={{ imageRendering: 'pixelated' }}
                      unoptimized
                    />
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black via-black/80 to-transparent p-2">
                      <p className="text-[10px] text-[#c9a96e] font-mono truncate">
                        {punk.name.split('_').slice(2).join('_')}
                      </p>
                      <p className="text-[8px] text-[#c9a96e]/50 font-mono">
                        {punkId}
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center p-2">
                    <div className="text-6xl text-red-400/30 mb-2">?</div>
                    <p className="text-xs text-red-400 font-mono text-center">
                      MISSING
                    </p>
                    <p className="text-[10px] text-red-400/60 font-mono">
                      {punkId}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {filteredPunks.length === 0 && (
          <div className="text-center py-20">
            <p className="text-[#c9a96e]/40 text-lg">No punks found matching your search</p>
          </div>
        )}
      </div>

      {/* Missing Punks List */}
      {!showMissingOnly && missingPunks.length > 0 && (
        <div className="max-w-7xl mx-auto mt-12 p-6 bg-red-900/10 border border-red-500/30">
          <h2 className="text-2xl font-bold text-red-400 mb-4">Missing Punks ({missingPunks.length})</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
            {missingPunks.map(punk => (
              <div key={punk} className="text-xs text-red-400/80 font-mono">
                {punk}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
