import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('https://bespoke-punks.onrender.com'),
  title: 'Bespoke Punks — Pixel Perfect Identity',
  description: '174 handcrafted pixel souls. Bespoke pixel art portraits that capture your essence. Where craft meets code.',
  keywords: ['pixel art', 'NFT', 'digital identity', 'bespoke', 'AI art', 'machine learning', 'crypto punks'],
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
    apple: '/logo.svg',
  },
  openGraph: {
    title: 'Bespoke Punks — Pixel Perfect Identity',
    description: '174 handcrafted pixel souls. Where craft meets code.',
    url: 'https://bespoke-punks.onrender.com',
    siteName: 'Bespoke Punks',
    images: [
      {
        url: '/banner.svg',
        width: 1200,
        height: 630,
        alt: 'Bespoke Punks - 174 Handcrafted Pixel Souls',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Bespoke Punks — Pixel Perfect Identity',
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
        <nav className="fixed top-0 left-0 right-0 z-50 frosted">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              <a href="/" className="serif text-xl tracking-tight accent-text">
                Bespoke Punks
              </a>
              <div className="hidden md:flex items-center space-x-8 text-sm">
                <a href="/" className="elegant-link hover:accent-text transition-colors">Home</a>
                <a href="/gallery" className="elegant-link hover:accent-text transition-colors">Collection</a>
                <a href="/about" className="elegant-link hover:accent-text transition-colors">Story</a>
                <a href="/generate" className="elegant-link hover:accent-text transition-colors">Create</a>
              </div>
            </div>
          </div>
        </nav>

        <main className="pt-20">
          {children}
        </main>

        <footer className="mt-32 border-t border-stone-200 dark:border-stone-800">
          <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div>
                <h3 className="serif text-lg mb-4 accent-text">Bespoke Punks</h3>
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
                © 2024 Bespoke Punks. Crafted with care on Abstract.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
