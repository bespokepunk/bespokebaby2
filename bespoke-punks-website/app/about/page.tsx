'use client';

import { motion } from 'framer-motion';

export default function AboutPage() {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl sm:text-6xl font-bold mb-6 gradient-text">
            The Story
          </h1>
          <p className="text-xl text-gray-400">
            From hackathon winner to 200+ pixel art punks and cutting-edge AI
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="space-y-12">
          {[
            {
              year: '2021',
              title: 'The Beginning',
              description: 'Won the Chainlink hackathon. Created my first self-portrait punk, then one for a friend from the hackathon team. It proliferated organically. By year end, 9 original punks existed.',
            },
            {
              year: 'January 2024',
              title: 'The Revival',
              description: 'Attended the ZO House memecoin summit. Returned with renewed vision and energy. Decided to take Bespoke Punks seriously and push the boundaries of what\'s possible.',
            },
            {
              year: '2024',
              title: 'The Build',
              description: 'Created 200+ handcrafted pixel art pieces. Built a complete ML/AI pipeline for generative pixel art (extremely difficult). Developed advanced trait analysis system with 35+ hierarchical categories. Trained Stable Diffusion LoRA models on RunPod. Achieved pixel-perfect generation.',
            },
            {
              year: 'Now',
              title: 'The Launch',
              description: 'Ready to share Bespoke Punks with the world. Production-ready AI generation system. World-class website. Building on Abstract for the next generation of consumer crypto.',
            },
          ].map((milestone, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: i * 0.2 }}
              className="flex gap-6"
            >
              <div className="flex-shrink-0">
                <div className="w-20 h-20 glass rounded-lg flex items-center justify-center text-punk-gold font-bold">
                  {milestone.year}
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold mb-3">{milestone.title}</h3>
                <p className="text-gray-400 leading-relaxed">
                  {milestone.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* About the Creator */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-20 glass rounded-xl p-8"
        >
          <h2 className="text-3xl font-bold mb-6 gradient-text">About the Creator</h2>

          <div className="space-y-4 text-gray-400 leading-relaxed">
            <p>
              I'm Ilyssa Evans - artist, engineer, and builder at the intersection of creativity and technology.
            </p>

            <p>
              <span className="text-white font-semibold">Education:</span> Chemical Engineering from UC Berkeley.
              MIT Micromasters in Machine Learning and Data Science (DSML). Self-taught programmer who now vibes code with AI.
            </p>

            <p>
              <span className="text-white font-semibold">Professional:</span> COO/CTO at Curable Labs.
              Previously at Genentech (formatics & application development), Deloitte, Dassault Systèmes, Benchling.
            </p>

            <p>
              <span className="text-white font-semibold">Web3:</span> Abstract Angel and Gigachad.
              Won Chainlink and Scroll hackathons. Educator for the first DEX on Ethereum.
              Started in Web3 learning about DeFi and never looked back.
            </p>

            <p>
              <span className="text-white font-semibold">Art:</span> Started as a graffiti and cupcake artist.
              Photographer. Industrial artist working with wood and glass.
              Bespoke Punks combines my love for pixel art, programming, and personalized creation.
            </p>
          </div>
        </motion.div>

        {/* The Vision */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-12 glass rounded-xl p-8"
        >
          <h2 className="text-3xl font-bold mb-6 gradient-text">The Vision</h2>

          <div className="space-y-4 text-gray-400 leading-relaxed">
            <p>
              Bespoke Punks is more than just NFTs. It's about identity - a digital passport that represents
              who you are, perfectly crafted to your vision.
            </p>

            <p>
              <span className="text-white font-semibold">Phase 1:</span> The Honorary Collection (200+ handcrafted originals)
            </p>

            <p>
              <span className="text-white font-semibold">Phase 2:</span> Community Generation -
              Anyone can use our AI to generate their perfect punk (off-chain or minted on-chain)
            </p>

            <p>
              <span className="text-white font-semibold">Phase 3:</span> The Trait Engine -
              Cross-pollination of traits from honoraries and community punks, creating infinite unique combinations
            </p>

            <p>
              <span className="text-white font-semibold">Phase 4:</span> The Game -
              Play as your NFT character. Bringing punks to life in an interactive world.
            </p>

            <p>
              <span className="text-white font-semibold">Beyond:</span> IRL integration with glass art creation,
              live punk generation events, auctions, and community experiences.
            </p>
          </div>
        </motion.div>

        {/* Technical Achievements */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-12 glass rounded-xl p-8"
        >
          <h2 className="text-3xl font-bold mb-6 gradient-text">Technical Innovation</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                title: 'Pixel-Perfect ML',
                description: 'Successfully trained diffusion models on 24×24 pixel art - an extremely difficult problem most ML models struggle with.',
              },
              {
                title: 'Advanced Trait System',
                description: '35+ hierarchical trait categories with pixel-perfect layering. Epic color naming system. Context-aware trait detection.',
              },
              {
                title: 'Professional MLOps',
                description: 'Production-grade experiment tracking, automated validation, statistical analysis, and root cause diagnosis.',
              },
              {
                title: 'Caption Engineering',
                description: 'Ultra-detailed captions with 12+ hex codes per image. 100% manually validated across all 203 training images.',
              },
            ].map((achievement, i) => (
              <div key={i} className="p-4 bg-white/5 rounded-lg">
                <h3 className="font-bold text-lg mb-2 text-punk-gold">{achievement.title}</h3>
                <p className="text-sm text-gray-400">{achievement.description}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-12 text-center"
        >
          <h3 className="text-2xl font-bold mb-4">Ready to Join the Journey?</h3>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/generate">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-punk-gold text-black font-bold rounded-lg hover:bg-punk-gold/90 transition-all"
              >
                Generate Your Punk
              </motion.button>
            </a>
            <a href="/gallery">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 glass font-semibold rounded-lg hover:bg-white/10 transition-all"
              >
                View Gallery
              </motion.button>
            </a>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
