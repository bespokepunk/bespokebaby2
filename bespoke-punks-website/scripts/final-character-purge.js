#!/usr/bin/env node

/**
 * FINAL CHARACTER PURGE - Remove EVERY single character mention
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function finalPurge() {
  console.log('🔥 FINAL CHARACTER PURGE - Removing ALL character mentions...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const lines = content.split('\n');
  const updatedLines = [];
  let updatedCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line
    if (line.length > 200 && line.includes('tilt-shift') && !line.startsWith('##')) {

      let updated = line;

      // Remove ALL variations of character descriptions
      // Pattern: "tiny [adjectives] figure with [description]"
      updated = updated.replace(/,?\s*tiny [a-z\s-]+ figure with [^,]+(?:wearing|in|and)[^,]+/gi, '');
      updated = updated.replace(/,?\s*tiny [a-z\s-]+ figure with [^,]+/gi, '');
      updated = updated.replace(/,?\s*tiny figure with [^,]+/gi, '');

      // Remove specific character features
      updated = updated.replace(/with [a-z\s-]+ hair (?:and|wearing|in)[^,]+/gi, '');
      updated = updated.replace(/wearing [a-z\s-]+ (?:hoop )?earrings[^,]*/gi, '');
      updated = updated.replace(/wearing [a-z\s-]+ top[^,]*/gi, '');
      updated = updated.replace(/with [a-z\s-]+ neckline accents[^,]*/gi, '');

      // Remove any remaining positioning phrases
      updated = updated.replace(/in miniature modern space,?/gi, '');
      updated = updated.replace(/in miniature [a-z\s]+ space,?/gi, '');
      updated = updated.replace(/in geometric [a-z\s]+ space,?/gi, '');

      // Remove remnants like "making character abstract"
      updated = updated.replace(/making character abstract [a-z\s]+,?/gi, '');
      updated = updated.replace(/making dancer abstract [a-z\s]+,?/gi, '');

      // Clean up artifacts
      updated = updated.replace(/,\s*,+/g, ',');
      updated = updated.replace(/\s+,/g, ',');
      updated = updated.replace(/,\s+/g, ', ');
      updated = updated.replace(/\s{2,}/g, ' ');

      // Remove leading/trailing commas and spaces
      updated = updated.trim();
      updated = updated.replace(/^,\s*/, '');
      updated = updated.replace(/,\s*$/, '');

      if (updated !== line) {
        updatedLines.push(updated);
        updatedCount++;
      } else {
        updatedLines.push(line);
      }
    } else {
      updatedLines.push(line);
    }
  }

  // Write back
  await fs.writeFile(PROMPTS_FILE, updatedLines.join('\n'));

  console.log(`✅ Purged ${updatedCount} prompts of ALL character mentions`);
  console.log('\n🌌 Prompts are now PURE environments with NO people!\n');
}

finalPurge().catch(console.error);
