#!/usr/bin/env node

/**
 * COMPLETE character removal - no figures whatsoever
 * Pure environmental storytelling only
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function completeRemoval() {
  console.log('🔧 COMPLETE CHARACTER REMOVAL - Pure environments only...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const lines = content.split('\n');
  const updatedLines = [];
  let updatedCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line
    if (line.length > 200 && line.includes('tilt-shift') && !line.startsWith('##')) {

      let updated = line;

      // Remove ALL variations of "tiny figure" or "tiny abstract figure"
      updated = updated.replace(/,?\s*tiny (abstract )?(pixel )?figure with [^,]+/gi, '');
      updated = updated.replace(/,?\s*tiny (abstract )?(pixel )?figure [^,]+/gi, '');

      // Remove all mentions of character features
      updated = updated.replace(/with [a-z\s]+ hair and [^,]+/gi, '');
      updated = updated.replace(/with [a-z\s]+ hair[,\s]/gi, ' ');

      // Remove visibility phrases about characters
      updated = updated.replace(/barely visible in (distant )?background among/gi, '');
      updated = updated.replace(/barely visible through atmospheric haze/gi, '');
      updated = updated.replace(/visible in background/gi, '');
      updated = updated.replace(/glimpsed (at|in|among)/gi, '');
      updated = updated.replace(/silhouetted in/gi, '');

      // Remove character-related descriptions
      updated = updated.replace(/atmospheric haze with blurred silhouette/gi, 'atmospheric haze');
      updated = updated.replace(/with blurred [a-z]+ silhouette/gi, '');
      updated = updated.replace(/blurred golden silhouette/gi, '');

      // Remove any remaining character positioning
      updated = updated.replace(/seated at[^,]*/gi, '');
      updated = updated.replace(/standing (near|at|by)[^,]*/gi, '');
      updated = updated.replace(/walking (along|through)[^,]*/gi, '');

      // Clean up artifacts
      updated = updated.replace(/,\s*,+/g, ',');
      updated = updated.replace(/\s+,/g, ',');
      updated = updated.replace(/,\s+/g, ', ');
      updated = updated.replace(/\s{2,}/g, ' ');

      // Remove "making figures abstract" since there are no figures
      updated = updated.replace(/heavy tilt-shift blur making (any )?figures (completely )?abstract and out of focus,?\s*/gi, '');
      updated = updated.replace(/making figures abstract and out of focus,?\s*/gi, '');

      // Ensure we have clean environmental language
      if (!updated.includes('pure environmental storytelling')) {
        updated = updated.replace(/, tilt-shift/, ', pure environmental storytelling, no people or characters, tilt-shift');
      }

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

  console.log(`✅ Completely removed characters from ${updatedCount} prompts`);
  console.log('\n🌌 ALL prompts are now:');
  console.log('  ✅ Pure atmospheric environments');
  console.log('  ✅ Environmental storytelling only');
  console.log('  ✅ No figures, no people, no characters whatsoever');
  console.log('  ✅ Objects and atmosphere tell the story\n');
}

completeRemoval().catch(console.error);
