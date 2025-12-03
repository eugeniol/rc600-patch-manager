import { z } from 'zod';

// Track configuration schema
export const TrackSchema = z.object({
  number: z.number().min(1).max(6),
  // Playback settings
  reverse: z.boolean().optional(),
  oneShot: z.boolean().optional(),
  playbackFX: z.string().optional(),
  balance: z.number().optional(),
  playLevel: z.number().optional(),
  // Track type & modes
  trackType: z.string().optional(),
  tempoSync: z.string().optional(),
  playbackMode: z.string().optional(),
  startMode: z.string().optional(),
  stopMode: z.string().optional(),
  overdubMode: z.string().optional(),
  // FX assignments
  fx1: z.string().optional(),
  fx2: z.string().optional(),
  fx3: z.string().optional(),
  // Timing settings
  rhythmSync: z.string().optional(),
  quantize: z.string().optional(),
  // Input configurations
  mic1: z.boolean().optional(),
  mic2: z.boolean().optional(),
  inst1L: z.boolean().optional(),
  inst1R: z.boolean().optional(),
  inst2L: z.boolean().optional(),
  inst2R: z.boolean().optional(),
  rhythm: z.boolean().optional(),
});

export type Track = z.infer<typeof TrackSchema>;

// Memory/Patch schema
export const PatchSchema = z.object({
  slot: z.number().min(0).max(199),
  name: z.string().max(16),
  bank: z.enum(['A', 'B']),
  count: z.string().optional(),
  bpm: z.number().optional(),
  tracks: z.array(TrackSchema).length(6),
  modified: z.boolean().default(false),
});

export type Patch = z.infer<typeof PatchSchema>;

// Copy operation schema
export const CopyOperationSchema = z.object({
  sourceSlot: z.number().min(0).max(199),
  targetSlots: z.array(z.number().min(0).max(199)),
  copyEffects: z.boolean().default(true),
  copyAssigns: z.boolean().default(true),
});

export type CopyOperation = z.infer<typeof CopyOperationSchema>;

// Setlist item schema
export const SetlistItemSchema = z.object({
  sourceSlot: z.number(),
  shortName: z.string(),
});

export type SetlistItem = z.infer<typeof SetlistItemSchema>;
