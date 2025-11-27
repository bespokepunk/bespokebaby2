import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('https://bespoke-punks.onrender.com'),
  title: 'Pixola Studio — Pixel Perfect Identity',
  description: '174 handcrafted pixel souls. Pixola Studio creates pixel art portraits that capture your essence. Where craft meets code.',
  keywords: ['pixel art', 'NFT', 'digital identity', 'bespoke', 'AI art', 'machine learning', 'crypto punks'],
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
    apple: '/logo.svg',
  },
  openGraph: {
    title: 'Pixola Studio — Pixel Perfect Identity',
    description: '174 handcrafted pixel souls. Where craft meets code.',
    url: 'https://bespoke-punks.onrender.com',
    siteName: 'Pixola Studio',
    images: [
      {
        url: '/banner.svg',
        width: 1200,
        height: 630,
        alt: 'Pixola Studio - 174 Handcrafted Pixel Souls',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Pixola Studio — Pixel Perfect Identity',
    description: '174 handcrafted pixel souls. Where craft meets code.',
    images: ['/banner.svg'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <nav className="fixed top-0 left-0 right-0 z-40 pointer-events-none">
          <div className="max-w-7xl mx-auto px-6 lg:px-8 pt-6">
            <div className="flex items-center justify-between">
              <a href="/" className="serif text-lg tracking-tight pointer-events-auto group">
                <span className="bg-gradient-to-r from-[#c9a96e] to-[#d4a574] bg-clip-text text-transparent font-light">
                  Pixola Studio
                </span>
              </a>
              <div className="hidden md:flex items-center space-x-8 text-xs font-light tracking-wider pointer-events-auto">
                <a href="/" className="text-[#c9a96e]/60 hover:text-[#c9a96e] transition-colors duration-300">HOME</a>
                <a href="/gallery" className="text-[#c9a96e]/60 hover:text-[#c9a96e] transition-colors duration-300">COLLECTION</a>
                <a href="/about" className="text-[#c9a96e]/60 hover:text-[#c9a96e] transition-colors duration-300">STORY</a>
                <a href="/generate" className="text-[#c9a96e]/60 hover:text-[#c9a96e] transition-colors duration-300">CREATE</a>
              </div>
            </div>
          </div>
        </nav>

        <main>
          {children}
        </main>

        <footer className="mt-32 border-t border-stone-200 dark:border-stone-800">
          <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div>
                <h3 className="serif text-lg mb-4 accent-text">Pixola Studio</h3>
                <p className="text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                  Pixel perfect digital identity. Handcrafted with care, generated with intelligence.
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium mb-4">Navigate</h4>
                <ul className="space-y-2 text-sm text-stone-600 dark:text-stone-400">
                  <li><a href="/gallery" className="elegant-link">Collection</a></li>
                  <li><a href="/about" className="elegant-link">Story</a></li>
                  <li><a href="/generate" className="elegant-link">Create</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-medium mb-4">Connect</h4>
                <ul className="space-y-2 text-sm text-stone-600 dark:text-stone-400">
                  <li><a href="#" className="elegant-link">Twitter</a></li>
                  <li><a href="#" className="elegant-link">Discord</a></li>
                  <li><a href="#" className="elegant-link">Instagram</a></li>
                </ul>
              </div>
            </div>
            <div className="mt-12 pt-8 border-t border-stone-200 dark:border-stone-800 text-center">
              <p className="text-xs text-stone-500">
                © 2024 Pixola Studio. Crafted with care on Abstract.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
