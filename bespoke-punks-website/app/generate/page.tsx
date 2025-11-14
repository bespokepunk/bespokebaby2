'use client';

import { motion, useMotionValue, useSpring } from 'framer-motion';
import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function GeneratePage() {
  const [isHovering, setIsHovering] = useState(false);

  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);

  const springConfig = { damping: 30, stiffness: 200 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [cursorX, cursorY]);

  return (
    <div
      className="min-h-screen cursor-none relative overflow-hidden flex items-center justify-center"
      style={{
        background: 'linear-gradient(180deg, #000000 0%, #0a0806 50%, #140f0a 100%)',
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

      {/* Coming Soon Content */}
      <div className="relative z-10 text-center max-w-4xl px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, type: 'spring', damping: 20 }}
          className="relative"
        >
          {/* Pixel frame */}
          <div className="absolute -inset-16 pointer-events-none">
            <div className="absolute top-0 left-0 w-12 h-12 border-l-4 border-t-4 border-[#c9a96e]" />
            <div className="absolute top-0 right-0 w-12 h-12 border-r-4 border-t-4 border-[#c9a96e]" />
            <div className="absolute bottom-0 left-0 w-12 h-12 border-l-4 border-b-4 border-[#c9a96e]" />
            <div className="absolute bottom-0 right-0 w-12 h-12 border-r-4 border-b-4 border-[#c9a96e]" />
          </div>

          <p className="font-mono text-xs tracking-[0.3em] uppercase text-[#c9a96e]/60 mb-8">
            PHASE_02 • STATUS: IN_DEVELOPMENT
          </p>

          <h1
            className="serif text-8xl md:text-9xl mb-8 leading-none"
            style={{
              background: 'linear-gradient(135deg, #c9a96e 0%, #ffd700 50%, #c9a96e 100%)',
              backgroundSize: '200% auto',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              animation: 'shimmer 6s linear infinite',
              textShadow: '0 0 40px rgba(201, 169, 110, 0.3)',
            }}
          >
            Coming Soon
          </h1>

          <div className="space-y-6 text-lg text-stone-400 max-w-2xl mx-auto mb-12">
            <p className="text-2xl text-[#c9a96e]">
              Upload your photo. AI generates your punk. Mint it on-chain.
            </p>
            <p>
              The neural network is trained. The interface is being crafted.
              Soon you'll transform yourself into 576 pixels of pure digital soul.
            </p>
          </div>

          {/* Status bars */}
          <div className="space-y-4 max-w-xl mx-auto mb-12">
            <div className="text-left">
              <div className="flex justify-between text-xs font-mono text-[#c9a96e]/60 mb-2">
                <span>AI_MODEL_TRAINING</span>
                <span>[COMPLETE]</span>
              </div>
              <div className="h-2 bg-[#c9a96e]/10 relative overflow-hidden">
                <div className="absolute inset-0 w-full bg-[#c9a96e]" />
              </div>
            </div>

            <div className="text-left">
              <div className="flex justify-between text-xs font-mono text-[#c9a96e]/60 mb-2">
                <span>INTERFACE_DESIGN</span>
                <span className="animate-pulse">[IN_PROGRESS]</span>
              </div>
              <div className="h-2 bg-[#c9a96e]/10 relative overflow-hidden">
                <motion.div
                  className="absolute inset-0 w-3/4 bg-[#c9a96e]"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>
            </div>

            <div className="text-left">
              <div className="flex justify-between text-xs font-mono text-[#c9a96e]/60 mb-2">
                <span>WEB3_INTEGRATION</span>
                <span>[QUEUED]</span>
              </div>
              <div className="h-2 bg-[#c9a96e]/10 relative overflow-hidden">
                <div className="absolute inset-0 w-1/4 bg-[#c9a96e]/40" />
              </div>
            </div>
          </div>

          {/* CTA */}
          <Link href="/gallery">
            <motion.div
              className="group relative inline-block"
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
              <button className="px-12 py-5 bg-transparent border-4 border-[#c9a96e] text-[#c9a96e] group-hover:bg-[#c9a96e] group-hover:text-[#0a0806] font-bold tracking-[0.3em] text-sm transition-all">
                EXPLORE COLLECTION
              </button>
            </motion.div>
          </Link>
        </motion.div>
      </div>

      {/* Floating pixels */}
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

/*
 * COMMENTED OUT - Previous Generate Page Content
 * Will be implemented in Phase 2
 *
'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';

export default function GeneratePage() {
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);

  const features = [
    { id: 'crown', name: 'Crown', emoji: '👑' },
    { id: 'tiara', name: 'Tiara', emoji: '💎' },
    { id: 'flower_crown', name: 'Flower Crown', emoji: '🌸' },
    { id: 'wings', name: 'Wings', emoji: '🪽' },
    { id: 'bow', name: 'Bow', emoji: '🎀' },
    { id: 'hat', name: 'Hat', emoji: '🎩' },
    { id: 'glasses', name: 'Glasses', emoji: '🕶️' },
    { id: 'earrings', name: 'Earrings', emoji: '💍' },
  ];
  // ... rest of the original code
}
*/
