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

  const toggleFeature = (id: string) => {
    setSelectedFeatures(prev =>
      prev.includes(id)
        ? prev.filter(f => f !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl sm:text-6xl font-bold mb-6 gradient-text">
            Generate Your Punk
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Upload your photo and let our AI create a bespoke pixel art punk that's 100% you.
          </p>
        </motion.div>

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold mb-8 text-center">How It Works</h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: '1',
                title: 'Upload Photo',
                description: 'Upload a clear photo of yourself',
                icon: '📸',
              },
              {
                step: '2',
                title: 'AI Analysis',
                description: 'Our ML model detects your features',
                icon: '🤖',
              },
              {
                step: '3',
                title: 'Customize',
                description: 'Choose additional traits and accessories',
                icon: '🎨',
              },
              {
                step: '4',
                title: 'Generate',
                description: 'Create your pixel-perfect punk',
                icon: '✨',
              },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="glass rounded-xl p-6 text-center"
              >
                <div className="text-4xl mb-4">{item.icon}</div>
                <div className="text-punk-gold font-bold mb-2">Step {item.step}</div>
                <h3 className="font-bold text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Generator Interface */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="glass rounded-xl p-8 mb-12"
        >
          <h2 className="text-2xl font-bold mb-6 text-center">Create Your Punk</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div>
              <h3 className="font-semibold mb-4">Upload Your Photo</h3>
              <div className="border-2 border-dashed border-white/20 rounded-lg p-12 text-center hover:border-punk-gold/50 transition-colors cursor-pointer">
                <div className="text-5xl mb-4">📤</div>
                <p className="text-gray-400 mb-2">Click to upload or drag and drop</p>
                <p className="text-sm text-gray-500">PNG, JPG up to 10MB</p>
              </div>

              {/* Feature Detection Preview */}
              <div className="mt-6 glass rounded-lg p-4">
                <h4 className="font-semibold mb-3 text-sm">AI-Detected Features</h4>
                <div className="space-y-2 text-sm text-gray-400">
                  <div className="flex justify-between">
                    <span>Hair Color</span>
                    <span className="text-punk-gold">Auto-detected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Eye Color</span>
                    <span className="text-punk-gold">Auto-detected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Skin Tone</span>
                    <span className="text-punk-gold">Auto-detected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Eyewear</span>
                    <span className="text-punk-gold">80.6% accuracy</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Earrings</span>
                    <span className="text-punk-gold">100% accuracy</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Customization Section */}
            <div>
              <h3 className="font-semibold mb-4">À La Carte Traits</h3>
              <p className="text-sm text-gray-400 mb-4">
                Add custom traits to make your punk truly yours
              </p>

              <div className="grid grid-cols-2 gap-3">
                {features.map((feature) => (
                  <motion.button
                    key={feature.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => toggleFeature(feature.id)}
                    className={`p-4 rounded-lg text-center transition-all ${
                      selectedFeatures.includes(feature.id)
                        ? 'bg-punk-gold text-black'
                        : 'glass hover:bg-white/10'
                    }`}
                  >
                    <div className="text-3xl mb-1">{feature.emoji}</div>
                    <div className="text-sm font-semibold">{feature.name}</div>
                  </motion.button>
                ))}
              </div>

              {/* Generate Button */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full mt-6 px-6 py-4 bg-punk-gold text-black font-bold rounded-lg text-lg hover:bg-punk-gold/90 transition-all shadow-lg hover:shadow-punk-gold/50"
              >
                Generate My Punk
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Pricing & Options */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold mb-8 text-center">Pricing Options</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div
              whileHover={{ y: -5 }}
              className="glass rounded-xl p-8"
            >
              <h3 className="text-2xl font-bold mb-4">Generate Off-Chain</h3>
              <div className="text-4xl font-bold text-punk-gold mb-4">Coming Soon</div>
              <p className="text-gray-400 mb-6">
                Create your punk and download the image. Perfect for testing and previews.
              </p>
              <ul className="space-y-3 mb-6">
                {[
                  'AI-powered generation',
                  'Custom trait selection',
                  'High-resolution download',
                  'Instant delivery',
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <span className="text-punk-gold">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>

            <motion.div
              whileHover={{ y: -5 }}
              className="glass rounded-xl p-8 border-2 border-punk-gold/50"
            >
              <div className="text-xs font-bold text-punk-gold mb-2">RECOMMENDED</div>
              <h3 className="text-2xl font-bold mb-4">Mint On-Chain</h3>
              <div className="text-4xl font-bold text-punk-gold mb-4">Coming Soon</div>
              <p className="text-gray-400 mb-6">
                Mint your punk as an NFT on Abstract. Included in the official collection.
              </p>
              <ul className="space-y-3 mb-6">
                {[
                  'Everything in Off-Chain',
                  'Minted on Abstract blockchain',
                  'Part of official collection',
                  'Future game access',
                  'Trait engine eligibility',
                  'Royalties & rights',
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <span className="text-punk-gold">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </motion.div>

        {/* Technical Details */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="glass rounded-xl p-8"
        >
          <h2 className="text-2xl font-bold mb-6">The Technology</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-semibold text-punk-gold mb-3">Machine Learning</h3>
              <ul className="space-y-2 text-gray-400">
                <li>• Stable Diffusion 1.5 with custom LoRA</li>
                <li>• Trained on 200+ handcrafted punks</li>
                <li>• 24×24 pixel-perfect generation</li>
                <li>• Reproducible with seed management</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-punk-gold mb-3">Feature Detection</h3>
              <ul className="space-y-2 text-gray-400">
                <li>• 100% earring detection accuracy</li>
                <li>• 86.4% earring type classification</li>
                <li>• 80.6% eyewear detection</li>
                <li>• Advanced color palette extraction</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-punk-gold mb-3">Trait System</h3>
              <ul className="space-y-2 text-gray-400">
                <li>• 35+ hierarchical trait categories</li>
                <li>• Epic color naming system</li>
                <li>• Context-aware trait composition</li>
                <li>• Pixel-perfect layering</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-punk-gold mb-3">Quality Assurance</h3>
              <ul className="space-y-2 text-gray-400">
                <li>• Professional MLOps pipeline</li>
                <li>• Automated validation testing</li>
                <li>• Statistical quality metrics</li>
                <li>• Production-ready Epoch 8 model</li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Coming Soon Notice */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-12 text-center"
        >
          <div className="inline-block glass rounded-xl px-8 py-6">
            <h3 className="text-xl font-bold mb-2">Generation Utility Coming Soon</h3>
            <p className="text-gray-400 mb-4">
              We're putting the finishing touches on the generation interface.
            </p>
            <p className="text-sm text-punk-gold">
              Want early access? Join our community to stay updated.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
