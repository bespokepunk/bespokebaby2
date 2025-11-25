'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import { useState } from 'react';

interface PunkWorldProps {
  punkIndex: number;
  punkName: string;
  colorShift: number;
}

export default function PunkWorld({ punkIndex, punkName, colorShift }: PunkWorldProps) {
  const [imageError, setImageError] = useState(false);
  const displayName = punkName.replace(/_/g, ' ').split(' ').slice(0, 2).join(' ').toUpperCase();

  // Mapping: display names -> world image names
  const worldNameMap: Record<string, string> = {
    'lady_052_pinksilkabstract': 'lady_008_pinksilk',
    'lady_053_pepperabstract': 'lady_006_pepper',
    'lady_056_alloyabstract': 'lady_007_alloy',
  };

  // Get the world image name (use mapping if exists, otherwise use punk name)
  const worldName = worldNameMap[punkName] || punkName;
  const worldImagePath = `/punk-worlds/${worldName}W.png`;

  return (
    <>
      {!imageError ? (
        // ACTUAL PUNK WORLD IMAGE - Smooth pan in effect with magnetizing zoom
        <motion.div
          className="absolute inset-0 overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          {/* Background blur for letterboxing areas */}
          <motion.div
            className="absolute inset-0"
            initial={{ scale: 1.15 }}
            animate={{ scale: 1.05 }}
            transition={{ duration: 8, ease: "easeOut" }}
          >
            <Image
              src={worldImagePath}
              alt={`${punkName} world background`}
              fill
              className="object-cover blur-2xl opacity-40"
              style={{ objectPosition: 'center center' }}
              onError={() => setImageError(true)}
              unoptimized
            />
          </motion.div>

          {/* Main sharp image - cover mode for 16:9 immersion */}
          <motion.div
            className="absolute inset-0 z-10"
            initial={{ scale: 1.15 }}
            animate={{ scale: 1.05 }}
            transition={{ duration: 8, ease: "easeOut" }}
          >
            <Image
              src={worldImagePath}
              alt={`${punkName} world`}
              fill
              className="object-cover"
              style={{ objectPosition: 'center center' }}
              onError={() => setImageError(true)}
              unoptimized
              priority
            />
          </motion.div>

          {/* Vignette overlay for depth - subtle */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent z-20" />
        </motion.div>
      ) : (
        // Error state - minimal and elegant
        <div className="absolute inset-0 flex items-center justify-center bg-black">
          <div className="text-center">
            <p className="font-mono text-sm text-[#c9a96e]/50">
              World image unavailable
            </p>
            <p className="font-mono text-xs text-[#c9a96e]/30 mt-2">
              {punkName}
            </p>
          </div>
        </div>
      )}
    </>
  );
}
