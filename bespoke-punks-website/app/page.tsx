'use client';

import { motion, useMotionValue, useSpring, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect, useRef, useMemo } from 'react';
import punkNames from '@/public/punk-names.json';
import PunkWorld from '@/components/PunkWorld';
import ThemeToggle from '@/components/ThemeToggle';
import { getRandomPunks } from '@/lib/utils/random';
import { fourPunkPositions } from '@/lib/layout/positions';
import { WORLD_COUNT, TOTAL_PUNKS } from '@/lib/constants';

export default function Home() {
  const [selectedPunks, setSelectedPunks] = useState<string[]>([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [hoveredPunk, setHoveredPunk] = useState<string | null>(null);
  const [colorShift, setColorShift] = useState(0);
  const [capturedPunk, setCapturedPunk] = useState<string | null>(null);
  const [trailPixels, setTrailPixels] = useState<Array<{ x: number; y: number; size: number; id: number }>>([]);
  const [isMobile, setIsMobile] = useState(false);

  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);
  const pixelIdCounter = useRef(0);

  // Optimize cursor updates with springs for smoother performance
  const smoothCursorX = useSpring(cursorX, { stiffness: 300, damping: 30 });
  const smoothCursorY = useSpring(cursorY, { stiffness: 300, damping: 30 });

  useEffect(() => {
    // Random selection of 4 punks from the 37 with worlds
    const randomPunks = getRandomPunks(4);
    setSelectedPunks(randomPunks);

    // Detect mobile
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    let rafId: number;
    let lastUpdate = 0;
    const throttleMs = 32; // Reduced to ~30fps for better performance

    const handleMouseMove = (e: MouseEvent) => {
      const now = Date.now();

      // Always update cursor position for smooth tracking
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);

      // Throttle other updates
      if (now - lastUpdate < throttleMs) return;
      lastUpdate = now;

      if (rafId) cancelAnimationFrame(rafId);

      rafId = requestAnimationFrame(() => {
        setMousePosition({ x: e.clientX, y: e.clientY });

        // Color shift based on mouse position
        const windowWidth = typeof window !== 'undefined' ? window.innerWidth : 1920;
        const hue = (e.clientX / windowWidth) * 60 + 20; // 20-80 range (gold to orange)
        setColorShift(hue);

        // Add cursor trail pixel (varied sizes) - only on desktop, reduced count
        if (window.innerWidth >= 768) {
          const sizes = [3, 4, 5];
          const randomSize = sizes[Math.floor(Math.random() * sizes.length)];

          pixelIdCounter.current += 1;
          const newPixel = {
            x: e.clientX,
            y: e.clientY,
            size: randomSize,
            id: pixelIdCounter.current,
          };

          setTrailPixels(prev => {
            const updated = [...prev, newPixel];
            // Keep only last 8 pixels for better performance
            return updated.slice(-8);
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

  // Clean up old trail pixels - increased interval for better performance
  useEffect(() => {
    const interval = setInterval(() => {
      setTrailPixels(prev => {
        if (prev.length === 0) return prev;
        return prev.slice(1); // Remove oldest pixel
      });
    }, 80); // Slower cleanup = better performance

    return () => clearInterval(interval);
  }, []);

  // Memoize positions - 4 punks optimized for 16:9 world showcase
  const punkPositions = useMemo(() => fourPunkPositions, []);

  return (
    <div
      className="min-h-screen overflow-hidden cursor-none md:cursor-none touch-auto relative dark:bg-black bg-stone-50 transition-colors duration-500"
      style={{
        background: `radial-gradient(circle at ${mousePosition.x || '50%'}px ${mousePosition.y || '50%'}px, var(--radial-start) 0%, var(--radial-end) 50%)`,
      }}
    >
      <ThemeToggle />
      {/* CURSOR TRAIL PIXELS - Better visibility */}
      <div className="hidden md:block fixed inset-0 pointer-events-none z-[90]">
        {trailPixels.map((pixel, index) => {
          const age = trailPixels.length - index;
          const opacity = Math.max(0, 1 - (age / trailPixels.length));

          return (
            <div
              key={pixel.id}
              className="absolute"
              style={{
                left: pixel.x,
                top: pixel.y,
                width: pixel.size,
                height: pixel.size,
                opacity: opacity * 0.7,
                background: `hsl(${colorShift + index * 3}, 80%, 70%)`,
                boxShadow: `0 0 ${pixel.size * 2}px hsl(${colorShift + index * 3}, 80%, 60%)`,
                borderRadius: '50%',
              }}
            />
          );
        })}
      </div>

      {/* ELEGANT LUMINOUS CURSOR - Simplified for performance */}
      <motion.div
        className="hidden md:block fixed pointer-events-none z-[100] will-change-transform"
        style={{
          left: smoothCursorX,
          top: smoothCursorY,
          x: '-50%',
          y: '-50%',
        }}
      >
        {/* Simple ring cursor */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="w-6 h-6 rounded-full border-2"
            style={{
              borderColor: `hsl(${colorShift}, 60%, 60%)`,
            }}
          />
        </div>

        {/* Center dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="w-2 h-2 rounded-full"
            style={{
              background: `hsl(${colorShift}, 70%, 70%)`,
            }}
          />
        </div>
      </motion.div>

      {/* SUBTLE GRID OVERLAY - Static for better performance */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.02]"
        style={{
          backgroundImage: `
            repeating-linear-gradient(0deg, transparent, transparent 47px, rgba(201, 169, 110, 0.3) 47px, rgba(201, 169, 110, 0.3) 48px),
            repeating-linear-gradient(90deg, transparent, transparent 47px, rgba(201, 169, 110, 0.3) 47px, rgba(201, 169, 110, 0.3) 48px)
          `,
        }}
      />

      {/* FLOATING PUNKS WITH WORLD VISIONS */}
      <div className="fixed inset-0">
        {selectedPunks.map((punk, i) => {
          const basePos = punkPositions[i];
          const isHovered = hoveredPunk === punk;
          const isCaptured = capturedPunk === punk;

          return (
            <motion.div
              key={punk}
              className="absolute will-change-transform cursor-pointer"
              style={{
                ...basePos,
                transform: 'translate(-50%, -50%)',
                pointerEvents: hoveredPunk && !isHovered ? 'none' : 'auto',
              }}
              initial={{ opacity: 0, scale: 0, rotate: -180 }}
              animate={{
                opacity: hoveredPunk && !isHovered ? 0 : (isCaptured ? 1 : (isHovered ? 1 : 0.4)),
                scale: isCaptured ? 2.5 : (isHovered ? 2 : 1),
                rotate: isCaptured ? 0 : (isHovered ? 0 : [0, 360]),
              }}
              transition={{
                delay: i * 0.08,
                opacity: { duration: 0.4 },
                scale: { type: 'spring', damping: 20, stiffness: 150 },
                rotate: { duration: isCaptured || isHovered ? 0 : 30, repeat: isCaptured || isHovered ? 0 : Infinity, ease: 'linear' }
              }}
              onMouseEnter={(e) => {
                if (isMobile) return;
                // Disable hover if we're in the footer/story section (below viewport)
                const scrollY = window.scrollY;
                if (scrollY > 100) return; // Don't show world portal if scrolled down
                setHoveredPunk(punk);
              }}
              onMouseLeave={() => !isMobile && setHoveredPunk(null)}
              onClick={(e) => {
                e.preventDefault();
                if (isMobile) {
                  // Mobile: tap to show world portal
                  if (hoveredPunk === punk) {
                    setHoveredPunk(null);
                  } else {
                    setHoveredPunk(punk);
                  }
                } else {
                  // Desktop: click to capture
                  if (isCaptured) {
                    setCapturedPunk(null);
                  } else {
                    setCapturedPunk(punk);
                  }
                }
              }}
            >
              <motion.div className="relative">
                  {/* PUNK'S WORLD VISION - Clean fullscreen portal */}
                  <AnimatePresence>
                    {isHovered && (
                      <motion.div
                        className="fixed inset-0 z-[200]"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                      >
                        {/* World background - with top padding to avoid header cutoff */}
                        <div className="absolute inset-0 pt-12">
                          <PunkWorld
                            punkIndex={selectedPunks.indexOf(punk)}
                            punkName={punk}
                            colorShift={colorShift}
                          />
                        </div>

                        {/* Subtle dark gradient overlay at bottom for text readability */}
                        <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-black/80 to-transparent pointer-events-none" />

                        {/* Punk name at bottom */}
                        <motion.div
                          className="absolute bottom-8 left-1/2 -translate-x-1/2 text-center"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p
                            className="font-mono text-4xl md:text-6xl tracking-wider"
                            style={{
                              color: `hsl(${colorShift}, 90%, 85%)`,
                              textShadow: `0 0 30px hsl(${colorShift}, 90%, 60%), 0 2px 8px rgba(0,0,0,0.8)`,
                            }}
                          >
                            {punk.replace(/_/g, ' ').split(' ').slice(0, 2).join(' ').toUpperCase()}
                          </p>
                        </motion.div>

                        {/* Close instruction at top */}
                        <motion.p
                          className="absolute top-6 left-1/2 -translate-x-1/2 font-mono text-xs tracking-widest text-white/60"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.3 }}
                        >
                          {isMobile ? 'TAP TO CLOSE' : 'HOVER AWAY TO CLOSE'}
                        </motion.p>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <div
                    className={hoveredPunk === punk ? '' : 'animate-float'}
                    style={{
                      animationDelay: `${i * 0.3}s`,
                      animationDuration: `${3 + i * 0.3}s`,
                    }}
                  >
                    <Image
                      src={`/punks-display/${punk}.png`}
                      alt={punk}
                      width={200}
                      height={200}
                      className="w-32 h-32 md:w-48 md:h-48 relative z-10"
                      style={{
                        imageRendering: 'pixelated',
                        filter: isHovered
                          ? `drop-shadow(0 0 40px hsl(${colorShift}, 70%, 60%)) saturate(1.8) contrast(1.3) brightness(1.2)`
                          : 'drop-shadow(0 0 10px rgba(201,169,110,0.3))',
                      }}
                      unoptimized
                      priority={i < 4}
                    />
                  </div>
                </motion.div>
            </motion.div>
          );
        })}
      </div>

      {/* MASSIVE ELEGANT TEXT WITH COLOR SHIFTING - Hide when world portal is open */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
        <motion.div className="relative">
          <motion.h1
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{
              opacity: hoveredPunk ? 0 : 1,
              scale: 1,
            }}
            transition={{ duration: hoveredPunk ? 0.2 : 1.5, type: 'spring', damping: 20 }}
            className="font-serif text-[20vw] md:text-[25vw] leading-none select-none relative"
          >
            {/* Soft background glow */}
            <motion.span
              className="absolute inset-0"
              animate={{
                opacity: [0.3, 0.5, 0.3],
              }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                color: 'transparent',
                textShadow: `0 0 120px hsl(${colorShift}, 70%, 50%)`,
              }}
            >
              YOU
            </motion.span>

            {/* Secondary warm glow */}
            <span
              className="absolute inset-0"
              style={{
                color: 'transparent',
                textShadow: `0 0 80px #ffd700`,
                opacity: 0.2,
              }}
            >
              YOU
            </span>

            {/* Main elegant text */}
            <span
              style={{
                color: 'transparent',
                WebkitTextStroke: `2px hsl(${colorShift}, 60%, 60%)`,
                textShadow: `0 0 40px hsl(${colorShift}, 70%, 50%)`,
              }}
            >
              YOU
            </span>
          </motion.h1>
        </motion.div>
      </div>

      {/* CAPTURED PUNK INFO OVERLAY */}
      <AnimatePresence>
        {capturedPunk && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-md z-[60] flex items-center justify-center"
            onClick={() => setCapturedPunk(null)}
          >
            <motion.div
              initial={{ scale: 0.5, rotate: -10 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0.5, rotate: 10 }}
              className="relative max-w-2xl w-full mx-4 p-12 border-4"
              style={{ borderColor: `hsl(${colorShift}, 60%, 60%)` }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Corner pixels */}
              <div className="absolute top-0 left-0 w-4 h-4 bg-[#c9a96e]" />
              <div className="absolute top-0 right-0 w-4 h-4 bg-[#c9a96e]" />
              <div className="absolute bottom-0 left-0 w-4 h-4 bg-[#c9a96e]" />
              <div className="absolute bottom-0 right-0 w-4 h-4 bg-[#c9a96e]" />

              <div className="text-center space-y-8">
                <motion.div
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 4, repeat: Infinity }}
                >
                  <Image
                    src={`/punks-display/${capturedPunk}.png`}
                    alt={capturedPunk}
                    width={300}
                    height={300}
                    className="w-64 h-64 mx-auto pixel-perfect"
                    style={{
                      filter: `drop-shadow(0 0 60px hsl(${colorShift}, 70%, 60%))`,
                    }}
                    unoptimized
                  />
                </motion.div>

                <div>
                  <p className="font-mono text-xs tracking-[0.5em] text-[#c9a96e]/60 mb-4">
                    CAPTURED
                  </p>
                  <h2
                    className="font-serif text-5xl mb-6"
                    style={{ color: `hsl(${colorShift}, 70%, 70%)` }}
                  >
                    {capturedPunk.replace(/_/g, ' ').split(' ').slice(0, 2).join(' ').toUpperCase()}
                  </h2>
                  <p className="font-mono text-sm text-[#c9a96e]/80 mb-8">
                    One of {TOTAL_PUNKS} Punks
                  </p>

                  <Link href="/gallery">
                    <button
                      className="px-12 py-4 border-2 font-mono text-sm tracking-[0.5em] transition-all hover:scale-105"
                      style={{
                        borderColor: `hsl(${colorShift}, 60%, 60%)`,
                        color: `hsl(${colorShift}, 70%, 70%)`,
                      }}
                    >
                      VIEW COLLECTION
                    </button>
                  </Link>
                </div>

                <p className="font-mono text-xs text-[#c9a96e]/40 tracking-widest">
                  CLICK ANYWHERE TO RELEASE
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* BOTTOM UI - MOBILE FRIENDLY */}
      <div className="fixed bottom-0 left-0 right-0 pb-6 md:pb-12 pointer-events-none z-50">
        <div className="max-w-7xl mx-auto px-4 md:px-6">
          {/* Mobile: Stack vertically */}
          <div className="flex flex-col md:flex-row items-center md:items-end justify-center md:justify-between gap-6 md:gap-0">
            {/* Left: Animated info - hidden on mobile */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1 }}
              className="hidden md:block space-y-2"
            >
              <motion.p
                className="font-mono text-xs tracking-[0.5em]"
                style={{
                  color: `hsl(${colorShift}, 60%, 60%)`,
                }}
                animate={{ opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {TOTAL_PUNKS} PUNKS
              </motion.p>
              <p className="font-mono text-[10px] tracking-[0.3em] text-[#c9a96e]/30">
                PIXEL PERFECT
              </p>
            </motion.div>

            {/* Center: ENTER button - responsive sizing */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 }}
              className="pointer-events-auto"
            >
              <Link href="/gallery">
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative group overflow-hidden"
                >
                  {/* Animated border glow */}
                  <motion.div
                    className="absolute -inset-4 md:-inset-6 blur-xl md:blur-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                    animate={{
                      background: [
                        `radial-gradient(circle, hsl(${colorShift}, 80%, 50%) 0%, transparent 70%)`,
                        `radial-gradient(circle, hsl(${colorShift + 20}, 80%, 50%) 0%, transparent 70%)`,
                        `radial-gradient(circle, hsl(${colorShift}, 80%, 50%) 0%, transparent 70%)`,
                      ],
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />

                  {/* Button body */}
                  <div
                    className="relative px-12 py-4 md:px-20 md:py-7 bg-black border-2 md:border-4 transition-all duration-300"
                    style={{
                      borderColor: `hsl(${colorShift}, 60%, 60%)`,
                    }}
                  >
                    {/* Sweep effect */}
                    <motion.div
                      className="absolute inset-0"
                      style={{
                        background: `linear-gradient(90deg, transparent, hsl(${colorShift}, 60%, 60%), transparent)`,
                      }}
                      initial={{ x: '-100%' }}
                      whileHover={{ x: '100%' }}
                      transition={{ duration: 0.5 }}
                    />

                    <span
                      className="relative font-mono text-xs md:text-sm tracking-[0.5em] md:tracking-[0.6em] font-bold z-10"
                      style={{
                        color: `hsl(${colorShift}, 60%, 60%)`,
                      }}
                    >
                      ENTER
                    </span>
                  </div>
                </motion.button>
              </Link>
            </motion.div>

            {/* Right: Nav - horizontal on mobile */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1 }}
              className="flex md:flex-col gap-4 md:gap-3 md:text-right pointer-events-auto"
            >
              <Link
                href="/generate"
                className="font-mono text-[10px] md:text-xs tracking-[0.3em] text-[#c9a96e]/40 hover:text-[#c9a96e] transition-colors relative group"
              >
                <span className="relative z-10">CREATE</span>
                <motion.span
                  className="absolute right-0 md:right-0 left-0 md:left-auto bottom-0 md:bottom-auto md:top-1/2 md:-translate-y-1/2 h-px w-0 group-hover:w-full transition-all duration-300"
                  style={{ backgroundColor: `hsl(${colorShift}, 60%, 60%)` }}
                />
              </Link>
              <button
                onClick={() => {
                  document.getElementById('story')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="font-mono text-[10px] md:text-xs tracking-[0.3em] text-[#c9a96e]/40 hover:text-[#c9a96e] transition-colors relative group"
              >
                <span className="relative z-10">STORY</span>
                <motion.span
                  className="absolute right-0 md:right-0 left-0 md:left-auto bottom-0 md:bottom-auto md:top-1/2 md:-translate-y-1/2 h-px w-0 group-hover:w-full transition-all duration-300"
                  style={{ backgroundColor: `hsl(${colorShift}, 60%, 60%)` }}
                />
              </button>
            </motion.div>
          </div>
        </div>
      </div>

      {/* STORY SECTION - optimized */}
      <div id="story" className="relative min-h-screen mt-[100vh]" style={{ background: '#000' }}>
        <div className="max-w-6xl mx-auto px-6 py-32">
          <div className="space-y-48">
            {[
              { year: '2021', title: 'One pixel portrait.', body: 'Then another. By year\'s end, nine. Each one handcrafted. Pixel by pixel.' },
              { year: '2024', title: 'SF. Something clicked.', body: 'What if this could scale? Not mass production. Democratized craft.' },
              { year: '250+', title: 'Portraits later.', body: '174 survived. The Honoraries. Friends, builders, artists, legends.' },
              { year: 'AI', title: 'The impossible.', body: '10,000 experiments. Pixel-perfect captions. Neural network trained.' },
              { year: 'NOW', title: 'Your turn.', body: '576 pixels. Your essence. Your soul.' },
            ].map((section, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 100 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-100px' }}
                transition={{ duration: 0.8 }}
                className={`relative ${i % 2 === 0 ? 'ml-0' : 'ml-auto max-w-2xl'}`}
              >
                <div
                  className="relative p-12 border-l-8 transition-colors duration-500"
                  style={{
                    borderColor: `hsl(${40 + i * 10}, 50%, 40%)`,
                  }}
                >
                  <p className="font-mono text-xs tracking-[0.5em] text-[#c9a96e]/30 mb-6">
                    {section.year}
                  </p>
                  <h2
                    className="font-serif text-6xl md:text-7xl mb-6 leading-none"
                    style={{
                      color: `hsl(${40 + i * 10}, 60%, 60%)`,
                    }}
                  >
                    {section.title}
                  </h2>
                  <p className="font-mono text-lg text-[#c9a96e]/60 leading-relaxed max-w-xl">
                    {section.body}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Final CTA */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="mt-48 text-center"
          >
            <Link href="/gallery">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="inline-block px-24 py-8 border-8 border-[#c9a96e]/30 hover:border-[#c9a96e] transition-all duration-500"
              >
                <span className="font-mono text-xl tracking-[0.7em] text-[#c9a96e]">
                  COLLECTION
                </span>
              </motion.div>
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative py-8 border-t border-[#c9a96e]/10" style={{ background: '#000' }}>
        <p className="text-center font-mono text-[8px] tracking-[0.5em] text-[#c9a96e]/20">
          PIXOLA STUDIO
        </p>
      </footer>
    </div>
  );
}
