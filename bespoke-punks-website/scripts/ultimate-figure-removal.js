#!/usr/bin/env node

/**
 * ULTIMATE FIGURE REMOVAL - Remove EVERY single figure/character mention
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function ultimateRemoval() {
  console.log('🔥 ULTIMATE FIGURE REMOVAL - Removing ALL figure/character mentions...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const lines = content.split('\n');
  const updatedLines = [];
  let updatedCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line (long lines with tilt-shift)
    if (line.length > 200 && line.includes('tilt-shift') && !line.startsWith('##')) {

      let updated = line;
      const original = line;

      // Remove ALL figure variations
      updated = updated.replace(/,?\s*tiny [a-z\s-]+ figure[^,]*/gi, '');
      updated = updated.replace(/,?\s*tiny figure[^,]*/gi, '');

      // Remove specific descriptive patterns
      updated = updated.replace(/,?\s*tiny [a-z\s-]+ wearing [^,]+/gi, '');
      updated = updated.replace(/,?\s*wearing [^,]+ in [a-z\s-]+ (?:stance|pose|space)[^,]*/gi, '');
      updated = updated.replace(/,?\s*wearing [^,]+ surrounded by [^,]+/gi, '');
      updated = updated.replace(/,?\s*examining [^,]+/gi, '');
      updated = updated.replace(/,?\s*surrounded by clay [^,]+/gi, '');

      // Remove character positioning
      updated = updated.replace(/in [0-9]-bit [a-z\s-]+ (?:stance|pose)[^,]*/gi, '');
      updated = updated.replace(/in 8-bit [a-z\s-]+ (?:stance|pose)[^,]*/gi, '');
      updated = updated.replace(/in clay [a-z\s-]+ space[^,]*/gi, '');
      updated = updated.replace(/in [a-z\s-]+ miniature [a-z\s-]+[^,]*/gi, '');
      updated = updated.replace(/in cozy miniature room[^,]*/gi, '');
      updated = updated.replace(/in gentle clay space[^,]*/gi, '');
      updated = updated.replace(/in urban space[^,]*/gi, '');
      updated = updated.replace(/in miniature [a-z\s-]+ (?:room|space)[^,]*/gi, '');

      // Remove skin/appearance descriptions
      updated = updated.replace(/,?\s*tiny (?:pale|peachy|tan|deep orange coral brown-skinned|dusty rose mauve-skinned|peachy-tan) [^,]*/gi, '');

      // Remove clothing items appearing alone
      updated = updated.replace(/wearing [a-z\s-]+ (?:clothing|garments|hood)[^,]*/gi, '');
      updated = updated.replace(/featuring [^,]+/gi, '');

      // Remove gothic/pose descriptions
      updated = updated.replace(/in gothic pose[^,]*/gi, '');
      updated = updated.replace(/in futuristic pose[^,]*/gi, '');
      updated = updated.replace(/in [a-z\s-]+ stance[^,]*/gi, '');
      updated = updated.replace(/in [a-z\s-]+ pose[^,]*/gi, '');

      // Clean up artifacts
      updated = updated.replace(/,\s*,+/g, ',');
      updated = updated.replace(/\s+,/g, ',');
      updated = updated.replace(/,\s+/g, ', ');
      updated = updated.replace(/\s{2,}/g, ' ');

      // Remove leading/trailing commas and spaces
      updated = updated.trim();
      updated = updated.replace(/^,\s*/, '');
      updated = updated.replace(/,\s*$/, '');

      if (updated !== original) {
        updatedLines.push(updated);
        updatedCount++;
        console.log(`✓ Cleaned: ${line.substring(0, 80)}...`);
      } else {
        updatedLines.push(line);
      }
    } else {
      updatedLines.push(line);
    }
  }

  // Write back
  await fs.writeFile(PROMPTS_FILE, updatedLines.join('\n'));

  console.log(`\n✅ Removed figures from ${updatedCount} prompts`);
  console.log('🌌 All prompts are now PURE environments!\n');

  // Verify
  const finalContent = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const remainingFigures = (finalContent.match(/tiny.*figure/gi) || []).length;
  console.log(`🔍 Verification: ${remainingFigures} "tiny figure" mentions remaining\n`);
}

ultimateRemoval().catch(console.error);
