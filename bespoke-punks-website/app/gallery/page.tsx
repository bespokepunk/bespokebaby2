'use client';

import { motion, useMotionValue, useSpring } from 'framer-motion';
import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import punkNames from '@/public/punk-names-validated.json';

type ImageState = 'loading' | 'loaded' | 'error';

export default function GalleryPage() {
  const [filter, setFilter] = useState<'all' | 'lad' | 'lady'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [visiblePunks, setVisiblePunks] = useState(60);
  const [hoveredPunk, setHoveredPunk] = useState<string | null>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [randomizedPunks, setRandomizedPunks] = useState<string[]>([]);
  const [imageStatus, setImageStatus] = useState<Record<string, ImageState>>({});
  const [imageSources, setImageSources] = useState<Record<string, string>>({});
  const [particles, setParticles] = useState<Array<{ left: number; top: number; duration: number; delay: number }>>([]);
  const [trailPixels, setTrailPixels] = useState<Array<{ x: number; y: number; size: number; id: number }>>([]);
  const [colorShift, setColorShift] = useState(40);
  const observerTarget = useRef<HTMLDivElement>(null);
  const fallbackAttempts = useRef<Set<string>>(new Set());
  const imageRefs = useRef<Record<string, HTMLImageElement | null>>({});
  const pixelIdCounter = useRef(0);

  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);

  const springConfig = { damping: 25, stiffness: 150 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  // Randomize on client side only
  useEffect(() => {
    setRandomizedPunks([...punkNames].sort(() => Math.random() - 0.5));
    // Generate particle positions once on mount
    setParticles(
      [...Array(15)].map(() => ({
        left: Math.random() * 100,
        top: Math.random() * 100,
        duration: 4 + Math.random() * 2,
        delay: Math.random() * 2,
      }))
    );
  }, []);

  useEffect(() => {
    let rafId: number;
    let lastUpdate = 0;
    const throttleMs = 32;

    const handleMouseMove = (e: MouseEvent) => {
      const now = Date.now();

      cursorX.set(e.clientX);
      cursorY.set(e.clientY);

      if (now - lastUpdate < throttleMs) return;
      lastUpdate = now;

      if (rafId) cancelAnimationFrame(rafId);

      rafId = requestAnimationFrame(() => {
        // Color shift based on mouse position
        const windowWidth = typeof window !== 'undefined' ? window.innerWidth : 1920;
        const hue = (e.clientX / windowWidth) * 60 + 20;
        setColorShift(hue);

        // Add cursor trail pixel
        if (window.innerWidth >= 768) {
          const sizes = [4, 5, 6, 7];
          const randomSize = sizes[Math.floor(Math.random() * sizes.length)];

          pixelIdCounter.current += 1;
          // Add some randomness and offset behind cursor center
          const offsetX = (Math.random() - 0.5) * 8;
          const offsetY = (Math.random() - 0.5) * 8;
          const newPixel = {
            x: e.clientX - randomSize / 2 + offsetX - 3, // Offset slightly back
            y: e.clientY - randomSize / 2 + offsetY - 3,
            size: randomSize,
            id: pixelIdCounter.current,
          };

          setTrailPixels(prev => {
            const updated = [...prev, newPixel];
            return updated.slice(-15);
          });
        }
      });
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, [cursorX, cursorY]);

  // Clean up old trail pixels
  useEffect(() => {
    const interval = setInterval(() => {
      setTrailPixels(prev => {
        if (prev.length === 0) return prev;
        return prev.slice(1);
      });
    }, 120);

    return () => clearInterval(interval);
  }, []);

  const filteredPunks = randomizedPunks.filter(punk => {
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

  const handleImageLoad = useCallback((punk: string) => {
    setImageStatus(prev => ({
      ...prev,
      [punk]: 'loaded',
    }));
  }, []);

  const handleImageError = useCallback((punk: string) => {
    if (!fallbackAttempts.current.has(punk)) {
      fallbackAttempts.current.add(punk);
      setImageSources(prev => ({
        ...prev,
        [punk]: `/punks/${punk}.png`,
      }));
      setImageStatus(prev => ({
        ...prev,
        [punk]: 'loading',
      }));
      return;
    }

    setImageStatus(prev => ({
      ...prev,
      [punk]: 'error',
    }));
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0806] cursor-none">
      {/* CURSOR TRAIL PIXELS */}
      <div className="hidden md:block fixed inset-0 pointer-events-none z-[90]">
        {trailPixels.map((pixel, index) => {
          const age = trailPixels.length - index;
          const opacity = Math.max(0.3, 1 - (age / trailPixels.length));
          const hue = colorShift + (index * 5); // More dramatic color shift

          return (
            <div
              key={pixel.id}
              className="absolute transition-opacity duration-200"
              style={{
                left: pixel.x,
                top: pixel.y,
                width: pixel.size,
                height: pixel.size,
                opacity: opacity,
                background: `hsl(${hue}, 90%, 65%)`,
                boxShadow: `
                  0 0 ${pixel.size * 3}px hsl(${hue}, 95%, 60%),
                  0 0 ${pixel.size * 6}px hsl(${hue}, 85%, 50%, 0.6)
                `,
              }}
            />
          );
        })}
      </div>

      {/* Custom cursor */}
      <motion.div
        className="fixed w-8 h-8 pointer-events-none z-[100] mix-blend-difference"
        style={{
          left: cursorXSpring,
          top: cursorYSpring,
          x: '-50%',
          y: '-50%',
        }}
      >
        <div className={`w-full h-full border-2 rounded-full transition-all duration-200 ${
          isHovering ? 'border-white scale-150' : 'border-[#c9a96e]'
        }`} />
      </motion.div>

      {/* Floating header - Ultra Compact */}
      <div className="fixed top-0 left-0 right-0 z-30 pointer-events-none">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 pt-20">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="flex items-center justify-between"
          >
            <h1 className="serif text-2xl sm:text-3xl text-[#c9a96e]">
              The Collection
            </h1>
          </motion.div>
        </div>
      </div>

      {/* Floating controls */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="fixed top-32 left-0 right-0 z-30 pointer-events-none"
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
            <div className="flex gap-3 pointer-events-auto">
              <button
                onClick={() => setFilter('all')}
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
                className={`px-6 py-2 text-xs tracking-widest transition-all ${
                  filter === 'all'
                    ? 'bg-[#c9a96e] text-[#0a0806]'
                    : 'border border-[#c9a96e]/30 text-[#c9a96e]/60 hover:border-[#c9a96e] hover:text-[#c9a96e]'
                }`}
              >
                ALL ({randomizedPunks.length})
              </button>
              <button
                onClick={() => setFilter('lad')}
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
                className={`px-6 py-2 text-xs tracking-widest transition-all ${
                  filter === 'lad'
                    ? 'bg-[#c9a96e] text-[#0a0806]'
                    : 'border border-[#c9a96e]/30 text-[#c9a96e]/60 hover:border-[#c9a96e] hover:text-[#c9a96e]'
                }`}
              >
                LADS
              </button>
              <button
                onClick={() => setFilter('lady')}
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
                className={`px-6 py-2 text-xs tracking-widest transition-all ${
                  filter === 'lady'
                    ? 'bg-[#c9a96e] text-[#0a0806]'
                    : 'border border-[#c9a96e]/30 text-[#c9a96e]/60 hover:border-[#c9a96e] hover:text-[#c9a96e]'
                }`}
              >
                LADIES
              </button>
            </div>

            <input
              type="text"
              placeholder="SEARCH..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              className="px-6 py-2 text-xs tracking-widest border border-[#c9a96e]/30 bg-[#0a0806] text-[#c9a96e] placeholder:text-[#c9a96e]/30 focus:outline-none focus:border-[#c9a96e] w-full sm:w-64 pointer-events-auto"
            />
          </div>
        </div>
      </motion.div>

      {/* Gallery - Masonry-style scattered layout */}
      <div className="pt-56 pb-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {/* Responsive grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
              {displayedPunks.map((punk, i) => {
                const punkId = punk.split('_').slice(0, 2).join(' #').replace('_', ' ');
                const status = imageStatus[punk] ?? 'loading';
                const imageSrc = imageSources[punk] ?? `/punks-display/${punk}.png`;
                const isLoaded = status === 'loaded';
                const isError = status === 'error';

                return (
                  <motion.div
                    key={punk}
                    initial={{ opacity: 0, scale: 0.8, rotate: Math.random() * 4 - 2 }}
                    animate={{
                      opacity: 1,
                      scale: 1,
                      rotate: 0
                    }}
                    transition={{
                      duration: 0.5,
                      delay: Math.min(i * 0.01, 0.6),
                      type: "spring",
                      stiffness: 100
                    }}
                    className="group relative"
                    onMouseEnter={() => {
                      setHoveredPunk(punk);
                      setIsHovering(true);
                    }}
                    onMouseLeave={() => {
                      setHoveredPunk(null);
                      setIsHovering(false);
                    }}
                  >
                    <motion.div
                      className="aspect-square relative overflow-hidden border border-[#c9a96e]/20 cursor-pointer group"
                      style={{
                        backgroundColor: '#0a0806'
                      }}
                      whileHover={{
                        scale: 1.05,
                        borderColor: 'rgba(201, 169, 110, 0.6)',
                        zIndex: 50
                      }}
                      transition={{ duration: 0.2 }}
                    >
                      {/* Loading & error placeholder */}
                      {!isLoaded && (
                        <div className="absolute inset-0 z-10 flex items-center justify-center bg-[#0a0806]">
                          {isError ? (
                            <div className="text-[10px] tracking-widest text-[#c9a96e]/50 text-center leading-tight px-2">
                              PREVIEW
                              <br />
                              UNAVAILABLE
                            </div>
                          ) : (
                            <div className="w-2 h-2 bg-[#c9a96e]/20 rounded-full animate-pulse" />
                          )}
                        </div>
                      )}

                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        ref={(el) => {
                          imageRefs.current[punk] = el;
                          if (el && el.complete && el.naturalWidth > 0 && !isLoaded) {
                            handleImageLoad(punk);
                          }
                        }}
                        src={imageSrc}
                        alt={punkId}
                        className={`w-full h-full object-cover transition-opacity duration-500 ${
                          isLoaded ? 'opacity-100' : 'opacity-0'
                        }`}
                        style={{
                          imageRendering: 'pixelated',
                          display: isError ? 'none' : 'block'
                        }}
                        loading={i < 30 ? 'eager' : 'lazy'}
                        onLoad={() => handleImageLoad(punk)}
                        onError={() => handleImageError(punk)}
                      />

                      {/* Hover overlay with info */}
                      <div className="absolute inset-0 bg-gradient-to-t from-[#0a0806] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div className="absolute bottom-0 left-0 right-0 p-3">
                          <p className="text-xs tracking-widest text-[#c9a96e] font-medium">
                            {punkId.toUpperCase()}
                          </p>
                        </div>
                      </div>

                      {/* Glow effect on hover */}
                      {hoveredPunk === punk && (
                        <motion.div
                          className="absolute inset-0 pointer-events-none"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          style={{
                            boxShadow: '0 0 40px rgba(201, 169, 110, 0.4), inset 0 0 40px rgba(201, 169, 110, 0.1)'
                          }}
                        />
                      )}
                    </motion.div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Infinite scroll trigger */}
          {displayedPunks.length < filteredPunks.length && (
            <div ref={observerTarget} className="mt-16 text-center py-8">
              <motion.p
                className="text-xs tracking-widest text-[#c9a96e]/40"
                animate={{ opacity: [0.4, 0.8, 0.4] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                LOADING MORE...
              </motion.p>
            </div>
          )}
        </div>
      </div>

      {/* Ambient particles */}
      <div className="fixed inset-0 pointer-events-none z-0">
        {particles.map((particle, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-[#c9a96e]/10 rounded-full"
            style={{
              left: `${particle.left}%`,
              top: `${particle.top}%`,
            }}
            animate={{
              y: [0, -40, 0],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: particle.duration,
              repeat: Infinity,
              delay: particle.delay,
            }}
          />
        ))}
      </div>
    </div>
  );
}
