'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';

// Import punk names and randomize selection
import punkNames from '@/public/punk-names.json';

// Select 8 random punks for featured display
const getRandomPunks = () => {
  const shuffled = [...punkNames].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 8);
};

const featuredPunks = getRandomPunks();

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section - Gallery Opening Aesthetic */}
      <section className="min-h-[90vh] flex items-center justify-center px-6 lg:px-8">
        <div className="max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
          >
            <p className="text-sm tracking-wider uppercase mb-6 text-stone-500">
              Est. 2021
            </p>
            <h1 className="serif text-6xl sm:text-7xl md:text-8xl lg:text-9xl mb-8 leading-[0.9]">
              100% You
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-stone-600 dark:text-stone-400 max-w-2xl mx-auto mb-12 leading-relaxed font-light">
              Bespoke pixel art portraits. Handcrafted with obsessive attention to detail.
              Generated with intelligence.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/gallery">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-3 border border-stone-900 dark:border-stone-100 hover:bg-stone-900 hover:text-white dark:hover:bg-stone-100 dark:hover:text-black transition-all text-sm tracking-wide"
                >
                  View Collection
                </motion.button>
              </Link>
              <Link href="/generate">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-3 text-sm tracking-wide elegant-link"
                >
                  Create Yours →
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Featured Punks - Curated Gallery Grid */}
      <section className="py-20 px-6 lg:px-8 border-t border-stone-200 dark:border-stone-800">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16"
          >
            <p className="text-xs tracking-wider uppercase text-stone-500 mb-3">Honoraries</p>
            <h2 className="serif text-4xl md:text-5xl mb-4">The Collection</h2>
            <p className="text-stone-600 dark:text-stone-400 max-w-xl mb-3">
              174 portraits, hand-selected from 250+ variants. Each one represents someone real.
            </p>
            <p className="text-sm text-stone-500 dark:text-stone-500 max-w-xl italic">
              Spot anyone you recognize?
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {featuredPunks.map((punk, i) => (
              <motion.div
                key={punk}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="group"
              >
                <Link href="/gallery">
                  <div className="aspect-square relative overflow-hidden bg-stone-100 dark:bg-stone-900 hover-lift cursor-pointer border border-stone-200 dark:border-stone-800">
                    <Image
                      src={`/punks-display/${punk}.png`}
                      alt={punk.split('_')[2]}
                      width={512}
                      height={512}
                      className="w-full h-full object-cover pixel-perfect group-hover:scale-105 transition-transform duration-500"
                    />
                  </div>
                  <p className="mt-3 text-xs tracking-wide text-stone-600 dark:text-stone-400">
                    {punk.split('_').slice(0, 2).join(' #').replace('_', ' ')}
                  </p>
                </Link>
              </motion.div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Link href="/gallery" className="text-sm elegant-link accent-text">
              Explore All 174 Punks →
            </Link>
          </div>
        </div>
      </section>

      {/* Philosophy - Artist Statement */}
      <section className="py-32 px-6 lg:px-8 border-t border-stone-200 dark:border-stone-800">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <p className="text-xs tracking-wider uppercase text-stone-500 mb-6">Philosophy</p>
            <h2 className="serif text-4xl md:text-5xl mb-8 leading-tight">
              A digital identity that represents you. Completely.
            </h2>
            <div className="space-y-6 text-stone-600 dark:text-stone-400 leading-relaxed">
              <p>
                Bespoke Punks began as an experiment in digital portraiture. What started with a single
                self-portrait in 2021 evolved into 200+ handcrafted pieces, each created with meticulous
                attention to every pixel.
              </p>
              <p>
                This is not generative art for the sake of scale. This is craft meets computation.
                Upper East Side meets California studio. Traditional portraiture meets machine learning.
              </p>
              <p className="italic">
                Your punk is your passport. Your portrait. Your pixel-perfect self.
              </p>
            </div>
            <div className="mt-12">
              <Link href="/about" className="text-sm elegant-link accent-text">
                Read the Full Story →
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* The Process - Subtle Technical */}
      <section className="py-20 px-6 lg:px-8 border-t border-stone-200 dark:border-stone-800">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16"
          >
            <p className="text-xs tracking-wider uppercase text-stone-500 mb-3">The Craft</p>
            <h2 className="serif text-4xl md:text-5xl">How It's Made</h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                number: '01',
                title: 'Handcrafted Foundation',
                description: '203 original portraits. Each pixel placed with intention. Skin tones, expressions, accessories - all carefully considered.',
              },
              {
                number: '02',
                title: 'Trained Intelligence',
                description: 'Custom ML model trained on the original collection. Stable Diffusion with LoRA fine-tuning. Pixel-perfect generation at 24×24.',
              },
              {
                number: '03',
                title: 'Your Portrait',
                description: 'Upload your photo. Our AI analyzes your features. Choose your style. Generate your bespoke punk.',
              },
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.15 }}
              >
                <p className="text-xs tracking-wider mb-4 accent-text">{step.number}</p>
                <h3 className="serif text-2xl mb-4">{step.title}</h3>
                <p className="text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action - Understated */}
      <section className="py-32 px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="serif text-5xl md:text-6xl mb-8">
              Find your pixel self
            </h2>
            <p className="text-lg text-stone-600 dark:text-stone-400 mb-12 max-w-xl mx-auto">
              Join the collection. Create your bespoke punk.
            </p>
            <Link href="/generate">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-10 py-4 border border-stone-900 dark:border-stone-100 hover:bg-stone-900 hover:text-white dark:hover:bg-stone-100 dark:hover:text-black transition-all tracking-wide"
              >
                Begin
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
