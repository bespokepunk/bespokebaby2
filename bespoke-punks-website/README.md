# Bespoke Punks

**174 handcrafted pixel souls. Where craft meets code.**

A paradigm-shifting pixel art collection showcasing bespoke digital identities. Built with Next.js 16, featuring revolutionary asymmetric layouts and elegant animations.

## Features

- ✨ Revolutionary asymmetric layout design
- 🎨 Dynamic color-shifting effects based on mouse interaction
- 📱 Fully responsive mobile-first design
- 🖼️ 174 unique handcrafted pixel art portraits
- ⚡ Optimized performance with Next.js 16 and Turbopack
- 🎭 Smooth Framer Motion animations
- 🎯 Custom pixel-perfect cursor
- 🌟 Elegant gold/honey color palette

## Tech Stack

- **Framework**: Next.js 16.0.3 with Turbopack
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Deployment**: Render

## Getting Started

### Prerequisites

- Node.js 20.11.0 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### Build for Production

```bash
# Create optimized production build
npm run build

# Start production server
npm start
```

## Deployment on Render

This project is configured for seamless deployment on Render.

### Deploy Steps

1. Push your code to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" and select "Web Service"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` configuration
6. Click "Create Web Service"

The `render.yaml` file contains all necessary configuration:
- Build command: `npm install && npm run build`
- Start command: `npm start`
- Node version: 20.11.0
- Environment: Production

### Environment Variables

No environment variables are required for basic deployment. The site runs entirely on the client side with static assets.

## Project Structure

```
bespoke-punks-website/
├── app/
│   ├── page.tsx           # Homepage with revolutionary design
│   ├── gallery/page.tsx   # Full collection gallery
│   ├── about/page.tsx     # Artist bio and story
│   ├── generate/page.tsx  # Coming soon page
│   ├── layout.tsx         # Root layout with metadata
│   └── globals.css        # Global styles and animations
├── public/
│   ├── punks-display/     # 174 punk PNG files
│   ├── logo.svg           # Brand logo
│   ├── banner.svg         # Social media banner
│   ├── favicon.svg        # Favicon
│   └── punk-names.json    # Punk metadata
├── render.yaml            # Render deployment config
└── package.json
```

## Design Philosophy

Bespoke Punks breaks away from traditional grid layouts with:

- **Asymmetric positioning**: Punks scattered organically across the canvas
- **Dynamic interaction**: Color shifts based on mouse movement
- **Elegant minimalism**: Japanese-inspired aesthetic without explicit cultural symbols
- **Pixel perfection**: Crisp rendering with `image-rendering: pixelated`
- **Sophisticated palette**: Gold, honey, and warm tones (no harsh reds)

## Performance Optimizations

- React.useMemo for position calculations
- Priority loading for above-the-fold images
- Lazy loading for gallery images
- CSS `will-change` for animated elements
- Unoptimized images to preserve pixel art quality

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

All rights reserved © 2024 Bespoke Punks

## Contact

For inquiries about the collection or custom commissions, reach out through the website.

---

**Built with care. Crafted with code.**
