#!/usr/bin/env node

/**
 * COMPREHENSIVE BODY PART REMOVAL - Remove ALL character body descriptions
 */

const fs = require('fs').promises;
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');

async function comprehensiveRemoval() {
  console.log('🔥 COMPREHENSIVE BODY PART REMOVAL - Removing ALL character body descriptions...\n');

  let content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const lines = content.split('\n');
  const updatedLines = [];
  let updatedCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a prompt line
    if (line.length > 200 && line.includes('tilt-shift') && !line.startsWith('##')) {

      let updated = line;
      const original = line;

      // Remove eye descriptions
      updated = updated.replace(/,?\s*[a-z\s-]+ eyes?\s+(?:sparkling|glowing|providing|coded|whispered|dressed|grown|burned|tied|aged|sunned|sung|painted|written)[^,]*/gi, '');
      updated = updated.replace(/,?\s*(?:bright teal cyan-green|neon green glowing|pink salmon glowing|glowing|sage green|olive brown green|olive brown-green|dark brown black|purple grey|golden yellow amber|teal turquoise|cyan turquoise|light blue cyan|sage green|dark purple plum|small dark brown black) eyes[^,]*/gi, '');
      updated = updated.replace(/ancient legend (?:coded|whispered|dressed|grown|burned|tied|aged|sunned|sung|painted|written) in [a-z\s-]+ eyes/gi, 'ancient legend');

      // Remove hair descriptions
      updated = updated.replace(/,?\s*(?:with|featuring|and) (?:medium-to-dark brown|orange-red|auburn reddish-brown|dark brown|blonde yellow|pale mint-sage green|multi-colored yellow orange white brown) (?:long )?(?:wavy |straight )?(?:hair|flame hair)[^,]*/gi, '');
      updated = updated.replace(/,?\s*(?:with|and) [a-z\s-]+ hair[^,]*/gi, '');
      updated = updated.replace(/dream-logic scale where (?:hair|flame hair) (?:is|divide is|streak is)[^,]*/gi, 'dream-logic scale where light is');
      updated = updated.replace(/ancient legend (?:burned|coded|tied) in (?:flame hair|white flame hair|hair buns)[^,]*/gi, 'ancient legend');
      updated = updated.replace(/,?\s*dark brown bun pigtails[^,]*/gi, '');
      updated = updated.replace(/,?\s*with gray silver tones[^,]*/gi, '');
      updated = updated.replace(/,?\s*with grey streaks[^,]*/gi, '');

      // Remove other body part references
      updated = updated.replace(/,?\s*with white pixelated blossom highlights[^,]*/gi, '');
      updated = updated.replace(/ethereal ghostly golden eyeshadow glow/gi, 'ethereal ghostly golden glow');
      updated = updated.replace(/liminal space between sight and unseen/gi, 'liminal space between seen and unseen');
      updated = updated.replace(/ancient legend whispered through hidden eyes/gi, 'ancient legend whispered through shadows');
      updated = updated.replace(/ancient legend coded in covered eyes/gi, 'ancient legend coded in mystery');

      // Remove "big hair legend" references
      updated = updated.replace(/folkloric tale of the big hair legend/gi, 'folkloric tale of the rock legend');

      // Remove "where afro is" references
      updated = updated.replace(/dream-logic scale where afro is entire crown/gi, 'dream-logic scale where crown is monument');

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
      } else {
        updatedLines.push(line);
      }
    } else {
      updatedLines.push(line);
    }
  }

  // Write back
  await fs.writeFile(PROMPTS_FILE, updatedLines.join('\n'));

  console.log(`✅ Removed body part descriptions from ${updatedCount} prompts`);
  console.log('🌌 All prompts are now PURE environments!\n');

  // Verify
  const finalContent = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const remainingEyes = (finalContent.match(/\b(?:eyes|hair|skin)\b/gi) || []).filter(match => {
    // Filter out false positives from line numbers
    return !match.match(/^\d+:/);
  }).length;
  console.log(`🔍 Verification: ${remainingEyes} potential body part mentions remaining\n`);
}

comprehensiveRemoval().catch(console.error);
