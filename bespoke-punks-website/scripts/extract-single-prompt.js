#!/usr/bin/env node

/**
 * Extract a single punk's prompt for easy copying
 * Usage: node scripts/extract-single-prompt.js lady_099_vq
 */

const fs = require('fs');
const path = require('path');

const punkName = process.argv[2];

if (!punkName) {
  console.log('Usage: node scripts/extract-single-prompt.js <punk_name>');
  console.log('Example: node scripts/extract-single-prompt.js lady_099_vq');
  process.exit(1);
}

const promptsFile = path.join(__dirname, '../FREEPIK_PROMPTS.md');
const content = fs.readFileSync(promptsFile, 'utf-8');

const lines = content.split('\n');
let found = false;
let style = '';
let prompt = '';

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  if (line.includes(`### ${punkName}`)) {
    found = true;
    continue;
  }

  if (found && line.startsWith('**Style:')) {
    style = line.replace(/\*\*Style: /, '').replace(/\*\*/, '');
    continue;
  }

  if (found && line && !line.startsWith('##') && !line.startsWith('**') && !line.startsWith('---')) {
    prompt = line.trim();
    break;
  }
}

if (!found || !prompt) {
  console.log(`❌ Punk "${punkName}" not found in FREEPIK_PROMPTS.md`);
  process.exit(1);
}

console.log(`\n🎭 ${punkName}`);
console.log(`📝 Style: ${style}`);
console.log(`\n✂️  COPY THIS PROMPT:\n`);
console.log('─'.repeat(80));
console.log(prompt);
console.log('─'.repeat(80));
console.log(`\n💾 Save as: public/punk-worlds/${punkName}.jpg\n`);
