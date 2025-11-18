#!/usr/bin/env node

/**
 * Aggressively update ALL prompts to be atmospheric and prevent realistic characters
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function updateAllPrompts() {
  console.log('🔧 Aggressively updating ALL prompts to be atmospheric...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const lines = content.split('\n');
  const updatedLines = [];
  let updatedCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line (long line with tilt-shift)
    if (line.length > 200 && line.includes('tilt-shift') && !line.startsWith('##')) {

      let updated = line;

      // 1. Replace specific character positioning with atmospheric distance
      updated = updated.replace(/tiny figure with ([^,]+) (seated at|visible at|at|near|on|among|in|wearing|examining|gazing|wielding|stretching|doing) /g,
        'atmospheric haze with blurred silhouette barely visible in far distance, tiny abstract figure with $1 ');

      // 2. Remove "visible in background" - make it even more distant
      updated = updated.replace(/visible in background/g, 'barely visible through atmospheric haze in far distance');
      updated = updated.replace(/glimpsed at/g, 'silhouetted in distant');
      updated = updated.replace(/visible near/g, 'barely visible beyond');
      updated = updated.replace(/visible on/g, 'obscured on distant');

      // 3. Add heavy blur emphasis before tilt-shift
      if (!updated.includes('heavy tilt-shift blur') && !updated.includes('heavy blur')) {
        updated = updated.replace(/, tilt-shift/, ', heavy tilt-shift blur making figures abstract and out of focus, tilt-shift');
      }

      // 4. Add "no realistic faces or characters" if not present
      if (!updated.includes('no realistic') && !updated.includes('abstract atmospheric world')) {
        updated = updated.replace(/, tilt-shift ([^,]+), 16:9$/, ', no realistic faces or characters, abstract atmospheric world only, tilt-shift $1, 16:9');
      }

      // 5. Strengthen existing anti-realistic keywords
      updated = updated.replace(/miniature figurine not photorealistic/g, 'no photorealistic figures, abstract shapes only');
      updated = updated.replace(/stylized miniature not photorealistic/g, 'no photorealistic elements, atmospheric abstraction');
      updated = updated.replace(/abstract miniature not realistic/g, 'purely abstract atmospheric world, no realistic characters');
      updated = updated.replace(/stylized not realistic/g, 'heavily stylized abstract only, no realism');

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

  console.log(`✅ Updated ${updatedCount} prompts with aggressive atmospheric language`);
  console.log('\nAdded to ALL prompts:');
  console.log('  • "atmospheric haze with blurred silhouette barely visible in far distance"');
  console.log('  • "heavy tilt-shift blur making figures abstract and out of focus"');
  console.log('  • "no realistic faces or characters"');
  console.log('  • "abstract atmospheric world only"');
  console.log('\nThis should prevent ANY realistic doll/character generation! 🎨\n');
}

updateAllPrompts().catch(console.error);
