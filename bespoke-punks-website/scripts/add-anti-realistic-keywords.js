#!/usr/bin/env node

/**
 * Add anti-realistic keywords to all prompts
 * This ensures AI doesn't generate cute realistic figurines
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function updatePrompts() {
  console.log('📝 Adding anti-realistic keywords to all prompts...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  let updatedCount = 0;

  // Keywords to add before "tilt-shift" at the end
  const antiRealisticKeywords = [
    'stylized miniature not photorealistic',
    'abstract miniature not realistic',
    'miniature figurine not photorealistic',
    'stylized not realistic'
  ];

  // Split into lines
  const lines = content.split('\n');
  const updatedLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line (contains "tilt-shift" near the end)
    if (line.includes('tilt-shift') && !line.startsWith('##') && !line.startsWith('**')) {

      // Check if it already has anti-realistic keywords
      const hasKeywords = antiRealisticKeywords.some(keyword => line.includes(keyword));

      if (!hasKeywords) {
        // Randomly pick one of the anti-realistic phrases
        const randomKeyword = antiRealisticKeywords[Math.floor(Math.random() * antiRealisticKeywords.length)];

        // Insert before the final "tilt-shift"
        const updatedLine = line.replace(/, (tilt-shift .+, 16:9)$/, `, ${randomKeyword}, $1`);

        if (updatedLine !== line) {
          updatedLines.push(updatedLine);
          updatedCount++;
        } else {
          updatedLines.push(line);
        }
      } else {
        updatedLines.push(line);
      }
    } else {
      updatedLines.push(line);
    }
  }

  // Write back
  await fs.writeFile(PROMPTS_FILE, updatedLines.join('\n'));

  console.log(`✅ Updated ${updatedCount} prompts with anti-realistic keywords`);
  console.log('   This will help prevent cute realistic figurine generation\n');
}

updatePrompts().catch(console.error);
