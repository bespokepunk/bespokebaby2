import { PUNKS_WITH_WORLDS } from '@/lib/constants';

/**
 * Fisher-Yates shuffle algorithm for true randomness
 * Time complexity: O(n)
 * @param array - Array to shuffle
 * @returns New shuffled array (immutable)
 */
export function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/**
 * Get random selection of punks with worlds
 * @param count - Number of punks to select (default: 4)
 * @returns Array of randomly selected punk names
 */
export function getRandomPunks(count: number = 4): string[] {
  if (count > PUNKS_WITH_WORLDS.length) {
    count = PUNKS_WITH_WORLDS.length;
  }
  return shuffleArray([...PUNKS_WITH_WORLDS]).slice(0, count);
}
