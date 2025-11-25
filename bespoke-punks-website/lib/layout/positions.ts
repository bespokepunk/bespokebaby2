export interface PunkPosition {
  left?: string;
  right?: string;
  top?: string;
  bottom?: string;
}

/**
 * Optimized 4-punk layout for 16:9 world showcase
 *
 * Design Rationale:
 * - 4 corner positions maximize world showcase space in center
 * - Asymmetric placement creates dynamic, organic feel vs rigid grid
 * - Clear center allows "YOU" hero text and world portals to shine
 * - Varied vertical positioning adds visual interest and motion
 * - Horizontal spread prevents clustering and maintains balance
 * - 16:9 optimization: full world images displayed without cropping center content
 * - Top buffer ensures punks never overlap with header (48px header + additional buffer)
 */
export const fourPunkPositions: PunkPosition[] = [
  // Top-left: Safe distance from header
  { left: '6%', top: '100px' },

  // Top-right: Safe distance from header with slight variation
  { right: '8%', top: '120px' },

  // Bottom-left: Deep placement for depth
  { left: '12%', bottom: '18%' },

  // Bottom-right: Strategic positioning
  { right: '10%', bottom: '15%' },
];
