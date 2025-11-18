#!/bin/bash

# Bespoke Punks - Generate All World Images
# This script makes it easy to generate all 194 punk world images

echo "🎨 Bespoke Punks World Image Generator"
echo "======================================"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install node-fetch@2 dotenv
  echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
  echo "❌ Error: .env file not found"
  echo "Please create .env with: FREEPIK_API_KEY=your-key"
  exit 1
fi

# Check if API key is set
if ! grep -q "FREEPIK_API_KEY" .env; then
  echo "❌ Error: FREEPIK_API_KEY not found in .env"
  exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "Starting generation of 194 punk world images..."
echo "This will take approximately 30-60 minutes"
echo ""
echo "💡 Tip: You can stop anytime (Ctrl+C) and restart later"
echo "   The script will resume from where it left off"
echo ""

# Run the generation script
node scripts/generate-punk-worlds.js

echo ""
echo "✨ Generation complete!"
echo "Images saved to: public/punk-worlds/"
