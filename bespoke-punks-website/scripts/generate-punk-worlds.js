#!/usr/bin/env node

/**
 * Freepik AI Image Generator - Punk Worlds Batch Generator
 *
 * This script reads FREEPIK_PROMPTS.md and generates all 194 punk world images
 * using the Freepik API with Flux Pro 1.1 model.
 *
 * Setup:
 * 1. API key is already in .env file
 * 2. npm install node-fetch@2 dotenv
 * 3. Run: node scripts/generate-punk-worlds.js
 */

const fs = require('fs').promises;
const path = require('path');
require('dotenv').config();

const API_KEY = process.env.FREEPIK_API_KEY;
const API_ENDPOINT = 'https://api.freepik.com/v1/ai/text-to-image/flux-pro-v1-1';
const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS.md');
const OUTPUT_DIR = path.join(__dirname, '../public/punk-worlds');
const STATUS_FILE = path.join(__dirname, '../.generation-status.json');

// Rate limiting
const DELAY_BETWEEN_REQUESTS = 2000; // 2 seconds between requests
const MAX_RETRIES = 3;

if (!API_KEY) {
  console.error('❌ Error: FREEPIK_API_KEY environment variable not set');
  console.error('Set it with: export FREEPIK_API_KEY="your-key-here"');
  process.exit(1);
}

/**
 * Parse FREEPIK_PROMPTS.md to extract all prompts
 */
async function parsePrompts() {
  const content = await fs.readFile(PROMPTS_FILE, 'utf-8');
  const prompts = [];

  const lines = content.split('\n');
  let currentPunk = null;
  let currentStyle = null;
  let currentPrompt = '';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Match punk name: ### lad_001_carbon or ### lady_099_vq
    const punkMatch = line.match(/^### (lad|lady)_(\d+)_([a-z0-9]+)$/i);
    if (punkMatch) {
      // Save previous punk if exists
      if (currentPunk && currentPrompt) {
        prompts.push({
          name: currentPunk,
          style: currentStyle,
          prompt: currentPrompt.trim()
        });
      }

      currentPunk = punkMatch[0].replace('### ', '');
      currentPrompt = '';
      currentStyle = null;
      continue;
    }

    // Match style: **Style: Miniature diorama stop-motion**
    const styleMatch = line.match(/^\*\*Style: (.+)\*\*$/);
    if (styleMatch) {
      currentStyle = styleMatch[1];
      continue;
    }

    // Collect prompt text (lines after style, before next ### or ---)
    if (currentPunk && currentStyle && line && !line.startsWith('##') && !line.startsWith('---') && !line.startsWith('*All')) {
      currentPrompt += line + ' ';
    }
  }

  // Save last punk
  if (currentPunk && currentPrompt) {
    prompts.push({
      name: currentPunk,
      style: currentStyle,
      prompt: currentPrompt.trim()
    });
  }

  return prompts;
}

/**
 * Load or create generation status tracker
 */
async function loadStatus() {
  try {
    const data = await fs.readFile(STATUS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return { completed: [], failed: [], inProgress: {} };
  }
}

/**
 * Save generation status
 */
async function saveStatus(status) {
  await fs.writeFile(STATUS_FILE, JSON.stringify(status, null, 2));
}

/**
 * Generate image via Freepik API
 */
async function generateImage(punkName, prompt, retries = 0) {
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-freepik-api-key': API_KEY
      },
      body: JSON.stringify({
        prompt: prompt,
        aspect_ratio: 'widescreen_16_9',
        output_format: 'jpeg',
        safety_tolerance: 4 // More lenient for artistic content
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API error: ${response.status} - ${error}`);
    }

    const response_data = await response.json();
    // API returns {data: {task_id, status}} - extract the inner data
    return response_data.data || response_data;
  } catch (error) {
    if (retries < MAX_RETRIES) {
      console.log(`   ⚠️  Retry ${retries + 1}/${MAX_RETRIES} for ${punkName}...`);
      await sleep(5000); // Wait 5 seconds before retry
      return generateImage(punkName, prompt, retries + 1);
    }
    throw error;
  }
}

/**
 * Check task status and download image when ready
 */
async function checkTaskAndDownload(taskId, punkName) {
  const checkEndpoint = `https://api.freepik.com/v1/ai/tasks/${taskId}`;

  let attempts = 0;
  const maxAttempts = 60; // 5 minutes max (5s * 60)

  while (attempts < maxAttempts) {
    try {
      const response = await fetch(checkEndpoint, {
        headers: {
          'x-freepik-api-key': API_KEY
        }
      });

      const responseData = await response.json();
      // API might return {data: {status, result}} or {status, result}
      const data = responseData.data || responseData;

      if (data.status === 'COMPLETED' && data.result && data.result.images && data.result.images.length > 0) {
        // Download the image
        const imageUrl = data.result.images[0].url;
        const imageResponse = await fetch(imageUrl);
        const imageBuffer = await imageResponse.arrayBuffer();

        const outputPath = path.join(OUTPUT_DIR, `${punkName}.jpg`);
        await fs.writeFile(outputPath, Buffer.from(imageBuffer));

        return { success: true, path: outputPath };
      } else if (data.status === 'FAILED') {
        return { success: false, error: 'Task failed' };
      }

      // Still in progress, wait and check again
      await sleep(5000);
      attempts++;
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  return { success: false, error: 'Timeout waiting for image' };
}

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Main execution
 */
async function main() {
  console.log('🎨 Bespoke Punks World Generator\n');
  console.log('Reading prompts from FREEPIK_PROMPTS.md...');

  const prompts = await parsePrompts();
  console.log(`✓ Found ${prompts.length} punk prompts\n`);

  // Ensure output directory exists
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  // Load status
  const status = await loadStatus();

  // Filter out already completed
  const remaining = prompts.filter(p => !status.completed.includes(p.name));

  if (remaining.length === 0) {
    console.log('✨ All images already generated!');
    return;
  }

  console.log(`📊 Status: ${status.completed.length} completed, ${remaining.length} remaining\n`);
  console.log('Starting generation...\n');

  for (let i = 0; i < remaining.length; i++) {
    const punk = remaining[i];
    const progress = `[${i + 1}/${remaining.length}]`;

    console.log(`${progress} 🎭 ${punk.name}`);
    console.log(`   📝 ${punk.style}`);

    try {
      // Generate image
      console.log(`   🚀 Submitting to API...`);
      const taskData = await generateImage(punk.name, punk.prompt);

      if (!taskData.task_id) {
        throw new Error('No task_id in response');
      }

      console.log(`   ⏳ Task ${taskData.task_id} - waiting for completion...`);

      // Wait and download
      const result = await checkTaskAndDownload(taskData.task_id, punk.name);

      if (result.success) {
        console.log(`   ✅ Saved to ${result.path}\n`);
        status.completed.push(punk.name);
        await saveStatus(status);
      } else {
        console.log(`   ❌ Failed: ${result.error}\n`);
        status.failed.push({ name: punk.name, error: result.error });
        await saveStatus(status);
      }

      // Rate limiting delay
      if (i < remaining.length - 1) {
        await sleep(DELAY_BETWEEN_REQUESTS);
      }

    } catch (error) {
      console.log(`   ❌ Error: ${error.message}\n`);
      status.failed.push({ name: punk.name, error: error.message });
      await saveStatus(status);
    }
  }

  console.log('\n✨ Generation complete!');
  console.log(`   ✅ Success: ${status.completed.length}`);
  console.log(`   ❌ Failed: ${status.failed.length}`);

  if (status.failed.length > 0) {
    console.log('\nFailed punks:');
    status.failed.forEach(f => console.log(`   - ${f.name}: ${f.error}`));
  }
}

// Run
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
