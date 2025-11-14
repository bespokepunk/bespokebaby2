'use client';

import { motion } from 'framer-motion';

interface PunkWorldProps {
  punkIndex: number;
  punkName: string;
  colorShift: number;
}

export default function PunkWorld({ punkIndex, punkName, colorShift }: PunkWorldProps) {
  // Assign world type based on punk index
  const worldType = punkIndex % 4;

  const displayName = punkName.replace(/_/g, ' ').split(' ').slice(0, 2).join(' ').toUpperCase();

  return (
    <>
      {/* CYBERPUNK CITY - Horizontal pan */}
      {worldType === 0 && (
        <motion.div
          className="absolute inset-0 overflow-hidden"
          style={{
            background: 'linear-gradient(180deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%)',
          }}
        >
          {/* Panning cityscape */}
          <motion.div
            className="absolute inset-0"
            animate={{ x: ['-20%', '0%'] }}
            transition={{ duration: 10, ease: 'linear', repeat: Infinity, repeatType: 'reverse' }}
          >
            {/* Neon buildings */}
            <div className="absolute bottom-0 left-0 right-0 h-[70%] flex items-end gap-2 px-8" style={{ width: '150%' }}>
              {[...Array(20)].map((_, i) => {
                const height = 30 + Math.random() * 65;
                const hue = colorShift + i * 20;
                return (
                  <div
                    key={i}
                    className="relative"
                    style={{
                      width: `${3 + Math.random() * 4}%`,
                      height: `${height}%`,
                      background: `linear-gradient(180deg, hsl(${hue}, 60%, 25%) 0%, hsl(${hue}, 70%, 15%) 100%)`,
                      boxShadow: `0 0 30px hsl(${hue}, 80%, 50%), inset 0 0 20px rgba(0,0,0,0.5)`,
                    }}
                  >
                    {/* Glowing windows grid */}
                    <div className="grid grid-cols-2 gap-1 p-1">
                      {[...Array(Math.floor(height / 12))].map((_, w) => (
                        <div
                          key={w}
                          className="h-2"
                          style={{
                            background: Math.random() > 0.4 ? `hsl(${hue + 40}, 100%, 70%)` : 'rgba(0,0,0,0.3)',
                            boxShadow: Math.random() > 0.4 ? `0 0 6px hsl(${hue + 40}, 100%, 60%)` : 'none',
                          }}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Floating particles */}
            {[...Array(30)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full bg-cyan-400"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  boxShadow: '0 0 4px cyan',
                }}
                animate={{
                  y: [-20, 20],
                  opacity: [0.2, 0.8, 0.2],
                }}
                transition={{
                  duration: 2 + Math.random() * 2,
                  repeat: Infinity,
                  delay: Math.random() * 2,
                }}
              />
            ))}
          </motion.div>

          {/* Punk name overlay */}
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 text-center z-10">
            <motion.p
              className="font-mono text-5xl tracking-[0.5em] mb-2"
              style={{
                color: `hsl(${colorShift}, 90%, 80%)`,
                textShadow: `0 0 40px hsl(${colorShift}, 90%, 60%), 0 0 80px hsl(${colorShift}, 80%, 50%)`,
              }}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              {displayName}
            </motion.p>
            <motion.p
              className="font-mono text-sm text-white/40 tracking-wider"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              NEON METROPOLIS
            </motion.p>
          </div>
        </motion.div>
      )}

      {/* PIXEL FOREST - Parallax depth */}
      {worldType === 1 && (
        <motion.div
          className="absolute inset-0 overflow-hidden"
          style={{
            background: 'linear-gradient(180deg, #0a4d3c 0%, #1a5e4a 50%, #2a3d2a 100%)',
          }}
        >
          {/* Layer 1: Far trees (slow pan) */}
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-[80%] flex items-end gap-4 opacity-30"
            animate={{ x: ['-10%', '10%'] }}
            transition={{ duration: 20, ease: 'linear', repeat: Infinity, repeatType: 'reverse' }}
            style={{ width: '120%' }}
          >
            {[...Array(15)].map((_, i) => (
              <div
                key={i}
                className="w-8"
                style={{
                  height: `${40 + Math.random() * 40}%`,
                  background: `linear-gradient(180deg, hsl(${colorShift + 120}, 40%, 20%) 0%, hsl(${colorShift + 120}, 50%, 15%) 100%)`,
                  clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)',
                }}
              />
            ))}
          </motion.div>

          {/* Layer 2: Mid trees (medium pan) */}
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-[70%] flex items-end gap-6 opacity-60"
            animate={{ x: ['0%', '-15%'] }}
            transition={{ duration: 15, ease: 'linear', repeat: Infinity, repeatType: 'reverse' }}
            style={{ width: '130%' }}
          >
            {[...Array(12)].map((_, i) => (
              <div
                key={i}
                className="w-12"
                style={{
                  height: `${50 + Math.random() * 40}%`,
                  background: `linear-gradient(180deg, hsl(${colorShift + 100}, 50%, 30%) 0%, hsl(${colorShift + 100}, 60%, 20%) 100%)`,
                  clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)',
                }}
              />
            ))}
          </motion.div>

          {/* Fireflies */}
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${30 + Math.random() * 50}%`,
                background: `hsl(${colorShift + 60}, 100%, 70%)`,
                boxShadow: `0 0 10px hsl(${colorShift + 60}, 100%, 60%)`,
              }}
              animate={{
                x: [-30, 30],
                y: [-20, 20],
                opacity: [0.3, 1, 0.3],
                scale: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 3,
              }}
            />
          ))}

          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 text-center z-10">
            <motion.p
              className="font-mono text-5xl tracking-[0.5em] mb-2"
              style={{
                color: `hsl(${colorShift}, 90%, 80%)`,
                textShadow: `0 0 40px hsl(${colorShift}, 90%, 60%)`,
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              {displayName}
            </motion.p>
            <motion.p
              className="font-mono text-sm text-white/40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              ENCHANTED FOREST
            </motion.p>
          </div>
        </motion.div>
      )}

      {/* SPACE STATION - Rotating view */}
      {worldType === 2 && (
        <motion.div
          className="absolute inset-0 overflow-hidden"
          style={{
            background: 'radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0a0a1a 100%)',
          }}
        >
          {/* Rotating starfield */}
          <motion.div
            className="absolute inset-0"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 30, ease: 'linear', repeat: Infinity }}
          >
            {[...Array(100)].map((_, i) => (
              <div
                key={i}
                className="absolute rounded-full bg-white"
                style={{
                  width: `${1 + Math.random() * 2}px`,
                  height: `${1 + Math.random() * 2}px`,
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  opacity: 0.3 + Math.random() * 0.7,
                }}
              />
            ))}
          </motion.div>

          {/* Floating space structures */}
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute"
              style={{
                left: `${20 + i * 15}%`,
                top: `${20 + i * 10}%`,
                width: '80px',
                height: '80px',
              }}
              animate={{
                y: [-20, 20],
                rotate: [0, 180, 360],
              }}
              transition={{
                duration: 10 + i * 2,
                repeat: Infinity,
                ease: 'linear',
              }}
            >
              <div
                className="w-full h-full"
                style={{
                  background: `linear-gradient(135deg, hsl(${colorShift + i * 30}, 70%, 40%) 0%, hsl(${colorShift + i * 30}, 80%, 20%) 100%)`,
                  boxShadow: `0 0 30px hsl(${colorShift + i * 30}, 80%, 50%)`,
                  clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)',
                }}
              />
            </motion.div>
          ))}

          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 text-center z-10">
            <motion.p
              className="font-mono text-5xl tracking-[0.5em] mb-2"
              style={{
                color: `hsl(${colorShift}, 90%, 80%)`,
                textShadow: `0 0 40px hsl(${colorShift}, 90%, 60%)`,
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {displayName}
            </motion.p>
            <motion.p className="font-mono text-sm text-white/40" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
              COSMIC STATION
            </motion.p>
          </div>
        </motion.div>
      )}

      {/* PIXEL OCEAN - Wave animation */}
      {worldType === 3 && (
        <motion.div
          className="absolute inset-0 overflow-hidden"
          style={{
            background: 'linear-gradient(180deg, #1e3a5f 0%, #2a5a8a 50%, #1a4d6d 100%)',
          }}
        >
          {/* Animated waves */}
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute left-0 right-0"
              style={{
                bottom: `${i * 15}%`,
                height: '20%',
                background: `linear-gradient(180deg, transparent 0%, hsl(${colorShift + 180 + i * 10}, 60%, ${30 + i * 5}%) 100%)`,
                opacity: 0.7 - i * 0.1,
              }}
              animate={{
                x: ['-100%', '100%'],
              }}
              transition={{
                duration: 15 - i * 2,
                ease: 'linear',
                repeat: Infinity,
              }}
            >
              {/* Wave peaks */}
              <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 1200 100">
                <path
                  d={`M0,50 Q150,${30 + i * 5} 300,50 T600,50 T900,50 T1200,50 L1200,100 L0,100 Z`}
                  fill={`hsl(${colorShift + 180 + i * 10}, 70%, ${35 + i * 5}%)`}
                />
              </svg>
            </motion.div>
          ))}

          {/* Bubbles rising */}
          {[...Array(15)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full border-2 border-white/30"
              style={{
                width: `${10 + Math.random() * 20}px`,
                height: `${10 + Math.random() * 20}px`,
                left: `${Math.random() * 100}%`,
                bottom: '0%',
              }}
              animate={{
                y: [0, -window.innerHeight || -1000],
                x: [0, (Math.random() - 0.5) * 100],
                opacity: [0.7, 0],
              }}
              transition={{
                duration: 8 + Math.random() * 4,
                repeat: Infinity,
                delay: Math.random() * 5,
                ease: 'easeOut',
              }}
            />
          ))}

          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 text-center z-10">
            <motion.p
              className="font-mono text-5xl tracking-[0.5em] mb-2"
              style={{
                color: `hsl(${colorShift}, 90%, 80%)`,
                textShadow: `0 0 40px hsl(${colorShift}, 90%, 60%)`,
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {displayName}
            </motion.p>
            <motion.p className="font-mono text-sm text-white/40" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
              DEEP OCEAN
            </motion.p>
          </div>
        </motion.div>
      )}
    </>
  );
}
