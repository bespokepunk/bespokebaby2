#!/usr/bin/env node

/**
 * Remove ALL character/figure mentions - pure atmospheric worlds only
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function removeAllCharacters() {
  console.log('🔧 Removing ALL character mentions - pure atmospheric worlds only...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const lines = content.split('\n');
  const updatedLines = [];
  let updatedCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line
    if (line.length > 200 && line.includes('tilt-shift') && !line.startsWith('##')) {

      let updated = line;

      // Remove all character/figure mentions entirely
      // Pattern: "atmospheric haze with blurred silhouette..., tiny abstract figure with [description]"
      updated = updated.replace(/atmospheric haze with blurred silhouette barely visible in far distance, tiny abstract figure with [^,]+,?/g, '');
      updated = updated.replace(/atmospheric haze with blurred silhouette barely visible in far distance,/g, '');

      // Remove any remaining "tiny figure" mentions
      updated = updated.replace(/tiny (abstract )?figure with [^,]+,?/g, '');
      updated = updated.replace(/tiny (abstract )?figure [^,]+,?/g, '');

      // Remove "silhouette" mentions
      updated = updated.replace(/blurred golden silhouette barely visible in far distance,?/g, '');
      updated = updated.replace(/with blurred [^,]+ silhouette [^,]+,?/g, '');

      // Remove character positioning phrases
      updated = updated.replace(/barely visible through atmospheric haze in far distance [^,]+,?/g, '');
      updated = updated.replace(/silhouetted in distant [^,]+,?/g, '');
      updated = updated.replace(/barely visible beyond [^,]+,?/g, '');
      updated = updated.replace(/obscured on distant [^,]+,?/g, '');

      // Clean up double commas and spaces
      updated = updated.replace(/,\s*,/g, ',');
      updated = updated.replace(/,\s+/g, ', ');
      updated = updated.replace(/\s+,/g, ',');

      // Make sure we still have the anti-realistic keywords for safety
      if (!updated.includes('no human figures')) {
        updated = updated.replace(/, tilt-shift/, ', no human figures or characters, pure atmospheric environment, tilt-shift');
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

  console.log(`✅ Removed characters from ${updatedCount} prompts`);
  console.log('\nNow generating:');
  console.log('  ✅ Pure atmospheric worlds');
  console.log('  ✅ No figures, no characters, no people');
  console.log('  ✅ Just environments, objects, and atmosphere');
  console.log('\nThe worlds will hint at presence through objects (glasses, clothing, accessories)');
  console.log('but no actual characters will appear! 🌌\n');
}

removeAllCharacters().catch(console.error);
