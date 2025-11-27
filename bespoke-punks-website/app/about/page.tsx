'use client';

import { motion, useMotionValue, useSpring, useScroll, useTransform } from 'framer-motion';
import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';

export default function AboutPage() {
  const [isHovering, setIsHovering] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);

  const springConfig = { damping: 30, stiffness: 200 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [cursorX, cursorY]);

  useEffect(() => {
    const unsubscribe = scrollYProgress.on('change', (latest) => {
      setScrollProgress(latest);
    });
    return () => unsubscribe();
  }, [scrollYProgress]);

  return (
    <div
      ref={containerRef}
      className="min-h-screen cursor-none relative overflow-x-hidden"
      style={{
        background: 'linear-gradient(180deg, #000000 0%, #0a0806 30%, #140f0a 100%)',
      }}
    >
      {/* Scanline effect */}
      <div
        className="fixed inset-0 pointer-events-none z-[90] opacity-[0.02]"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(201, 169, 110, 0.1) 2px, rgba(201, 169, 110, 0.1) 4px)',
          animation: 'scanline 8s linear infinite',
        }}
      />

      {/* Pixel grid */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.015]"
        style={{
          backgroundImage: `
            linear-gradient(90deg, rgba(201, 169, 110, 0.3) 1px, transparent 1px),
            linear-gradient(0deg, rgba(201, 169, 110, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '24px 24px',
        }}
      />

      {/* Custom pixel cursor */}
      <motion.div
        className="fixed pointer-events-none z-[100]"
        style={{
          left: cursorXSpring,
          top: cursorYSpring,
          x: '-50%',
          y: '-50%',
        }}
      >
        <motion.div
          className="relative"
          animate={{
            scale: isHovering ? 1.5 : 1,
            rotate: isHovering ? 45 : 0,
          }}
          transition={{ type: 'spring', damping: 20, stiffness: 300 }}
        >
          <div className="w-6 h-6 relative">
            <div className="absolute inset-0 border-2 border-[#c9a96e]" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 50%, 50% 50%, 50% 100%, 0 100%)' }} />
            <div className="absolute inset-[4px] bg-[#c9a96e] opacity-20" />
          </div>
        </motion.div>
      </motion.div>

      {/* Progress bar - pixel style */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-[#c9a96e]/10 z-50">
        <motion.div
          className="h-full bg-[#c9a96e] relative"
          style={{ scaleX: scrollYProgress, transformOrigin: '0%' }}
        >
          {/* Pixel notches on progress bar */}
          <div className="absolute right-0 top-0 w-2 h-2 bg-[#c9a96e] transform translate-x-1/2 -translate-y-1/2" />
        </motion.div>
      </div>

      {/* Navigation */}
      <div className="fixed top-8 right-8 z-50">
        <Link
          href="/"
          className="group relative block"
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          <div className="absolute -top-1 -left-1 w-2 h-2 bg-[#c9a96e] group-hover:scale-150 transition-transform" />
          <div className="border-l-2 border-t-2 border-[#c9a96e]/40 group-hover:border-[#c9a96e] pl-4 pt-2 transition-colors">
            <p className="text-[#c9a96e]/60 group-hover:text-[#c9a96e] font-mono text-xs tracking-wider transition-colors">
              ← HOME
            </p>
          </div>
        </Link>
      </div>

      {/* Main content */}
      <div className="relative z-10 py-32 px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Hero section with pixel art title */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, type: 'spring', damping: 20 }}
            className="mb-32 relative"
          >
            {/* Pixel frame decoration */}
            <div className="absolute -inset-8 pointer-events-none opacity-40">
              <div className="absolute top-0 left-0 w-4 h-4 border-l-4 border-t-4 border-[#c9a96e]" />
              <div className="absolute top-0 right-0 w-4 h-4 border-r-4 border-t-4 border-[#c9a96e]" />
            </div>

            <p className="font-mono text-xs tracking-[0.3em] uppercase text-[#c9a96e]/60 mb-6">
              SYSTEM.LOG • ORIGIN_STORY.TXT
            </p>
            <h1
              className="serif text-7xl md:text-8xl lg:text-9xl mb-6 leading-none"
              style={{
                background: 'linear-gradient(135deg, #c9a96e 0%, #ffd700 50%, #c9a96e 100%)',
                backgroundSize: '200% auto',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                animation: 'shimmer 6s linear infinite',
                textShadow: '0 0 40px rgba(201, 169, 110, 0.3)',
              }}
            >
              How It Started
            </h1>
            <div className="flex items-center gap-4 text-[#c9a96e]/40 text-xs font-mono">
              <span className="w-12 h-[2px] bg-[#c9a96e]/40" />
              <span>YEAR: 2021</span>
              <span className="w-2 h-2 bg-[#c9a96e] animate-pulse" />
              <span>STATUS: REVOLUTION</span>
            </div>
          </motion.div>

          {/* Story sections with pixel panels */}
          <div className="space-y-24">
            {/* Section 1: The Beginning */}
            <motion.section
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="relative border-l-4 border-[#c9a96e]/30 pl-8 py-4">
                <div className="absolute -left-[7px] top-0 w-3 h-3 bg-[#c9a96e] rotate-45" />

                <p className="text-2xl md:text-3xl text-[#c9a96e] mb-8 leading-relaxed">
                  One pixel portrait. Then another. By year's end, nine.
                </p>

                <div className="space-y-6 text-lg text-stone-400 leading-relaxed">
                  <p>
                    Each one handcrafted. 24×24 pixels. No shortcuts.
                  </p>
                </div>

                {/* Pixel decoration */}
                <div className="absolute -right-4 top-1/2 w-8 h-8 opacity-20">
                  <div className="w-full h-full grid grid-cols-3 grid-rows-3 gap-1">
                    {[...Array(9)].map((_, i) => (
                      <div key={i} className="bg-[#c9a96e]" />
                    ))}
                  </div>
                </div>
              </div>
            </motion.section>

            {/* Section 2: The Click */}
            <motion.section
              initial={{ opacity: 0, x: 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="relative border-r-4 border-[#c9a96e]/30 pr-8 py-4 text-right ml-auto">
                <div className="absolute -right-[7px] top-0 w-3 h-3 bg-[#c9a96e] rotate-45" />

                <p className="text-2xl md:text-3xl text-[#c9a96e] mb-8 leading-relaxed">
                  January 2024. Something clicked.
                </p>

                <div className="space-y-6 text-lg text-stone-400 leading-relaxed">
                  <p>
                    What if this could scale? Machine learning what humans know.
                  </p>
                </div>
              </div>
            </motion.section>

            {/* Section 3: The Work */}
            <motion.section
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="relative border-4 border-[#c9a96e]/20 p-8 bg-[#c9a96e]/5 backdrop-blur-sm">
                {/* Corner pixels */}
                <div className="absolute top-0 left-0 w-3 h-3 bg-[#c9a96e]" />
                <div className="absolute top-0 right-0 w-3 h-3 bg-[#c9a96e]" />
                <div className="absolute bottom-0 left-0 w-3 h-3 bg-[#c9a96e]" />
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-[#c9a96e]" />

                <div className="space-y-6 text-lg text-stone-300 leading-relaxed">
                  <p>
                    250+ portraits. Friends. Builders. Artists. Legends.
                  </p>

                  <p className="text-[#c9a96e]/80 italic">
                    174 made the final cut. <span className="font-mono not-italic">The Honoraries.</span>
                  </p>
                </div>
              </div>
            </motion.section>

            {/* Section 4: The Impossible */}
            <motion.section
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="relative border-l-4 border-[#c9a96e]/30 pl-8 py-4">
                <div className="absolute -left-[7px] top-0 w-3 h-3 bg-[#c9a96e] rotate-45 animate-pulse" />

                <p className="text-2xl md:text-3xl text-[#c9a96e] mb-8 leading-relaxed">
                  Teaching a neural network to think in pixels.
                </p>

                <div className="space-y-6 text-lg text-stone-400 leading-relaxed">
                  <p>
                    Most models choke on this resolution. Too small. Too precise.
                  </p>

                  <p className="text-xl text-[#c9a96e]">
                    It worked.
                  </p>

                  <p className="text-2xl text-[#ffd700]">
                    Your essence in 576 pixels.
                  </p>
                </div>
              </div>
            </motion.section>

            {/* The Vision - Terminal Style */}
            <motion.section
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1 }}
              className="mt-32 pt-16 border-t-2 border-[#c9a96e]/20"
            >
              <p className="font-mono text-xs tracking-[0.3em] uppercase text-[#c9a96e]/60 mb-8">
                ROADMAP.EXE • LOADING_FUTURE...
              </p>

              <div className="space-y-8 font-mono text-sm">
                <div className="flex items-start gap-4">
                  <span className="text-[#c9a96e] text-xl">■</span>
                  <div>
                    <span className="text-[#c9a96e]">PHASE_01:</span>
                    <span className="text-stone-400 ml-2">The Honoraries.</span>
                    <span className="text-green-500 ml-2">[COMPLETE]</span>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <span className="text-[#c9a96e] text-xl">▓</span>
                  <div>
                    <span className="text-[#c9a96e]">PHASE_02:</span>
                    <span className="text-stone-400 ml-2">Generate your punk.</span>
                    <span className="text-yellow-500 ml-2 animate-pulse">[IN_PROGRESS]</span>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <span className="text-[#c9a96e] text-xl">▒</span>
                  <div>
                    <span className="text-[#c9a96e]">PHASE_03:</span>
                    <span className="text-stone-400 ml-2">Trait engine.</span>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <span className="text-[#c9a96e] text-xl">░</span>
                  <div>
                    <span className="text-[#c9a96e]">PHASE_04:</span>
                    <span className="text-stone-400 ml-2">Play as your punk.</span>
                  </div>
                </div>

                <div className="flex items-start gap-4 pt-4 border-t border-[#c9a96e]/20">
                  <span className="text-[#ffd700] text-xl">◆</span>
                  <div>
                    <span className="text-[#ffd700]">PHASE_∞:</span>
                    <span className="text-stone-400 ml-2">Glass art. Live events. </span>
                    <span className="text-stone-500 ml-2 italic">We'll see.</span>
                  </div>
                </div>
              </div>
            </motion.section>

            {/* About Creator */}
            <motion.section
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1 }}
              className="mt-32 pt-16 border-t-2 border-[#c9a96e]/20"
            >
              <p className="font-mono text-xs tracking-[0.3em] uppercase text-[#c9a96e]/60 mb-8">
                CREATOR.BIO • ACCESS_GRANTED
              </p>

              <h2
                className="serif text-5xl md:text-6xl mb-12"
                style={{
                  background: 'linear-gradient(135deg, #c9a96e 0%, #ffd700 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Pixel Queen
              </h2>

              <div className="space-y-6 text-lg text-stone-400 leading-relaxed">
                <p>
                  Artist. Engineer.
                </p>

                <p>
                  Industrial art meets machine learning. Glass and wood meet neural networks.
                  Physical meets digital.
                </p>

                <p className="text-xl text-[#c9a96e] italic">
                  Pixola Studio is where it all converges.
                </p>
              </div>
            </motion.section>

            {/* CTA Section */}
            <motion.section
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="mt-32 text-center"
            >
              <div className="relative inline-block">
                <div className="absolute -inset-12 pointer-events-none">
                  <div className="absolute top-0 left-0 w-8 h-8 border-l-4 border-t-4 border-[#c9a96e]" />
                  <div className="absolute top-0 right-0 w-8 h-8 border-r-4 border-t-4 border-[#c9a96e]" />
                  <div className="absolute bottom-0 left-0 w-8 h-8 border-l-4 border-b-4 border-[#c9a96e]" />
                  <div className="absolute bottom-0 right-0 w-8 h-8 border-r-4 border-b-4 border-[#c9a96e]" />
                </div>

                <h3 className="serif text-5xl md:text-6xl mb-12 text-[#c9a96e]">
                  Ready?
                </h3>

                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <Link href="/generate">
                    <motion.div
                      className="group relative"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onMouseEnter={() => setIsHovering(true)}
                      onMouseLeave={() => setIsHovering(false)}
                    >
                      <div className="absolute inset-[-4px] pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="absolute top-0 left-0 w-3 h-3 bg-[#c9a96e]" />
                        <div className="absolute top-0 right-0 w-3 h-3 bg-[#c9a96e]" />
                        <div className="absolute bottom-0 left-0 w-3 h-3 bg-[#c9a96e]" />
                        <div className="absolute bottom-0 right-0 w-3 h-3 bg-[#c9a96e]" />
                      </div>
                      <button className="px-12 py-5 bg-[#c9a96e] text-[#0a0806] font-bold tracking-[0.3em] text-sm">
                        CREATE YOURS
                      </button>
                    </motion.div>
                  </Link>

                  <Link href="/gallery">
                    <motion.div
                      className="group relative"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onMouseEnter={() => setIsHovering(true)}
                      onMouseLeave={() => setIsHovering(false)}
                    >
                      <div className="absolute inset-0 border-4 border-[#c9a96e] group-hover:border-[#f4e4c1] transition-colors" />
                      <button className="px-12 py-5 bg-transparent text-[#c9a96e] group-hover:bg-[#c9a96e] group-hover:text-[#0a0806] font-bold tracking-[0.3em] text-sm transition-all">
                        VIEW GALLERY
                      </button>
                    </motion.div>
                  </Link>
                </div>
              </div>
            </motion.section>
          </div>
        </div>
      </div>

      {/* Floating pixels in background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute bg-[#c9a96e]"
            style={{
              width: [1, 2, 3][Math.floor(Math.random() * 3)],
              height: [1, 2, 3][Math.floor(Math.random() * 3)],
              left: `${Math.random() * 100}%`,
              top: `${100 + Math.random() * 20}%`,
            }}
            animate={{
              y: [-1200, -100],
              opacity: [0, 0.3, 0],
            }}
            transition={{
              duration: 15 + Math.random() * 10,
              repeat: Infinity,
              delay: Math.random() * 10,
              ease: 'linear',
            }}
          />
        ))}
      </div>
    </div>
  );
}
