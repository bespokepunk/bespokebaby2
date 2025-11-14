'use client';

import { motion, useMotionValue, useSpring, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect, useRef, useMemo } from 'react';
import punkNames from '@/public/punk-names.json';

export default function Home() {
  const [selectedPunks, setSelectedPunks] = useState<string[]>([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [hoveredPunk, setHoveredPunk] = useState<string | null>(null);
  const [colorShift, setColorShift] = useState(0);

  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);

  useEffect(() => {
    const shuffled = [...punkNames].sort(() => Math.random() - 0.5);
    setSelectedPunks(shuffled.slice(0, 8));
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
      setMousePosition({ x: e.clientX, y: e.clientY });

      // Color shift based on mouse position
      const hue = (e.clientX / window.innerWidth) * 60 + 20; // 20-80 range (gold to orange)
      setColorShift(hue);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [cursorX, cursorY]);

  // Memoize positions - MORE SPREAD OUT
  const punkPositions = useMemo(() => [
    { left: '8%', top: '18%' },
    { right: '12%', top: '15%' },
    { left: '10%', bottom: '25%' },
    { right: '15%', bottom: '20%' },
    { left: '45%', top: '8%' },
    { right: '42%', bottom: '30%' },
    { left: '20%', top: '65%' },
    { right: '25%', top: '58%' },
  ], []);

  return (
    <div
      className="min-h-screen overflow-hidden cursor-none md:cursor-none touch-auto relative"
      style={{
        background: `radial-gradient(circle at ${mousePosition.x || '50%'}px ${mousePosition.y || '50%'}px, #0f0a06 0%, #000000 50%)`,
      }}
    >
      {/* ELEGANT LUMINOUS CURSOR - hidden on mobile */}
      <motion.div
        className="hidden md:block fixed pointer-events-none z-[100]"
        style={{
          left: cursorX,
          top: cursorY,
          x: '-50%',
          y: '-50%',
        }}
      >
        {/* Soft outer glow */}
        <motion.div
          className="absolute inset-0"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div
            className="w-12 h-12 rounded-full blur-lg"
            style={{
              background: `radial-gradient(circle, hsl(${colorShift}, 70%, 60%) 0%, transparent 70%)`,
            }}
          />
        </motion.div>

        {/* Inner ring */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="w-6 h-6 rounded-full border"
            style={{
              borderColor: `hsl(${colorShift}, 60%, 60%)`,
              boxShadow: `0 0 12px hsl(${colorShift}, 70%, 60%)`,
            }}
            animate={{
              rotate: 360,
            }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          />
        </div>

        {/* Center dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="w-2 h-2 rounded-full"
            style={{
              background: `hsl(${colorShift}, 70%, 70%)`,
              boxShadow: `0 0 8px hsl(${colorShift}, 80%, 60%)`,
            }}
          />
        </div>
      </motion.div>

      {/* REACTIVE GRID OVERLAY - pulses on hover */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `
            repeating-linear-gradient(0deg, transparent, transparent 47px, hsl(${colorShift}, 50%, 50%) 47px, hsl(${colorShift}, 50%, 50%) 48px),
            repeating-linear-gradient(90deg, transparent, transparent 47px, hsl(${colorShift}, 50%, 50%) 47px, hsl(${colorShift}, 50%, 50%) 48px)
          `,
          transition: 'background-image 0.3s ease',
        }}
      />

      {/* FLOATING PUNKS - optimized */}
      <div className="fixed inset-0">
        {selectedPunks.map((punk, i) => {
          const pos = punkPositions[i];
          const isHovered = hoveredPunk === punk;

          return (
            <motion.div
              key={punk}
              className="absolute will-change-transform"
              style={{
                ...pos,
                transform: 'translate(-50%, -50%)',
              }}
              initial={{ opacity: 0, scale: 0, rotate: -180 }}
              animate={{
                opacity: isHovered ? 1 : 0.4,
                scale: isHovered ? 2 : 1,
                rotate: isHovered ? 0 : [0, 360],
              }}
              transition={{
                delay: i * 0.08,
                opacity: { duration: 0.4 },
                scale: { type: 'spring', damping: 20, stiffness: 150 },
                rotate: { duration: isHovered ? 0 : 30, repeat: isHovered ? 0 : Infinity, ease: 'linear' }
              }}
              onMouseEnter={() => setHoveredPunk(punk)}
              onMouseLeave={() => setHoveredPunk(null)}
            >
              <Link href="/gallery">
                <motion.div className="relative">
                  {/* ELEGANT MULTI-LAYER GLOW */}
                  <AnimatePresence>
                    {isHovered && (
                      <>
                        {/* Soft outer aura */}
                        <motion.div
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{
                            opacity: [0, 0.6, 0.4],
                            scale: [0.8, 2, 2.5],
                          }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          transition={{ duration: 1.5, ease: 'easeOut' }}
                          className="absolute inset-0 blur-3xl"
                          style={{
                            zIndex: -1,
                            background: `radial-gradient(circle, hsl(${colorShift}, 70%, 60%) 0%, transparent 70%)`,
                          }}
                        />

                        {/* Warm inner glow */}
                        <motion.div
                          initial={{ opacity: 0, scale: 1 }}
                          animate={{
                            opacity: [0, 0.8, 0.6],
                            scale: [1, 1.5, 1.8],
                          }}
                          exit={{ opacity: 0 }}
                          transition={{ duration: 1, ease: 'easeOut' }}
                          className="absolute inset-0 blur-2xl"
                          style={{
                            zIndex: -1,
                            background: `radial-gradient(circle, #ffd700 0%, transparent 60%)`,
                          }}
                        />

                        {/* Subtle shimmer */}
                        <motion.div
                          className="absolute inset-0"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: [0.1, 0.3, 0.1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          style={{ zIndex: -2 }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-tr from-[#c9a96e] via-transparent to-[#ffd700] blur-xl opacity-20" />
                        </motion.div>
                      </>
                    )}
                  </AnimatePresence>

                  <motion.div
                    animate={{
                      y: isHovered ? 0 : [0, -15, 0],
                    }}
                    transition={{
                      y: {
                        duration: 3 + i * 0.3,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      },
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
                  </motion.div>

                  {/* Name with elegant glow */}
                  {isHovered && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute -bottom-16 left-1/2 -translate-x-1/2 whitespace-nowrap"
                    >
                      <p
                        className="font-mono text-2xl tracking-[0.3em]"
                        style={{
                          color: `hsl(${colorShift}, 70%, 70%)`,
                          textShadow: `0 0 20px hsl(${colorShift}, 80%, 60%), 0 0 40px hsl(${colorShift}, 70%, 50%)`,
                        }}
                      >
                        {punk.replace(/_/g, ' ').split(' ').slice(0, 2).join(' ').toUpperCase()}
                      </p>
                    </motion.div>
                  )}
                </motion.div>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* MASSIVE ELEGANT TEXT WITH COLOR SHIFTING */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
        <motion.div className="relative">
          <motion.h1
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{
              opacity: 1,
              scale: 1,
            }}
            transition={{ duration: 1.5, type: 'spring', damping: 20 }}
            className="font-serif text-[25vw] leading-none select-none relative"
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
                174 HANDCRAFTED
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
          BESPOKE PUNKS
        </p>
      </footer>
    </div>
  );
}
