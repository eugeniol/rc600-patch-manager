/**
 * Track Element Mapping
 *
 * Maps RC-600 XML track elements (A-Y) to Track properties.
 * Based on the Python implementation in rc600_patch_manager.py
 *
 * Element Q is special - it's a 7-bit bitmask containing all input configurations:
 * Bit 6 (MSB): rhythm
 * Bit 5: inst2R
 * Bit 4: inst2L
 * Bit 3: inst1R
 * Bit 2: inst1L
 * Bit 1: mic2
 * Bit 0 (LSB): mic1
 */

export interface ElementMapping {
  element: string;
  property?: keyof import("../types/rc600").Track;
  type: "number" | "boolean" | "enum" | "bitmask" | "unknown";
  description: string;
}

/**
 * Track element mappings (A-Y = 25 elements)
 */
export const TRACK_ELEMENT_MAP: ElementMapping[] = [
  { element: "A", property: "reverse", type: "boolean", description: "Reverse playback (0=OFF, 1=ON)" },
  { element: "B", property: "oneShot", type: "boolean", description: "One-shot mode (0=Loop, 1=One Shot)" },
  { element: "C", property: "balance", type: "number", description: "Pan balance (0-100, 50=center)" },
  { element: "D", property: "playLevel", type: "number", description: "Track playback volume (0-100)" },
  { element: "E", property: "playbackFX", type: "enum", description: "FX during playback (0=OFF, 1=ON)" },
  { element: "F", property: "trackType", type: "enum", description: "Track type (0=Multi, 1=Single)" },
  { element: "G", property: "tempoSync", type: "enum", description: "Tempo sync (0=OFF, 1=ON)" },
  { element: "H", property: "playbackMode", type: "enum", description: "Playback mode (0=Multi, 1=Serial)" },
  { element: "I", property: "startMode", type: "enum", description: "Start trigger mode" },
  { element: "J", property: "stopMode", type: "enum", description: "Stop mode" },
  { element: "K", property: "overdubMode", type: "enum", description: "Overdub mode" },
  { element: "L", property: "fx1", type: "enum", description: "FX1 assign (0=None, 1=Enabled)" },
  { element: "M", property: "fx2", type: "enum", description: "FX2 assign (0=None, 1=Enabled)" },
  { element: "N", property: "fx3", type: "enum", description: "FX3 assign (0=None, 1=Enabled)" },
  { element: "O", property: "rhythmSync", type: "enum", description: "Rhythm sync" },
  { element: "P", property: "quantize", type: "enum", description: "Quantize (0=OFF, 1=ON)" },
  { element: "Q", type: "bitmask", description: "Input setup bitmask (mic1, mic2, inst1L, inst1R, inst2L, inst2R, rhythm)" },
  { element: "R", type: "unknown", description: "Unknown" },
  { element: "S", type: "unknown", description: "Unknown (0, 1, 2 observed)" },
  { element: "T", type: "unknown", description: "Unknown (always 0 in samples)" },
  { element: "U", type: "unknown", description: "Unknown numeric (760, 1200 observed)" },
  { element: "V", type: "unknown", description: "Unknown large numeric" },
  { element: "W", type: "unknown", description: "Unknown (0, 1 observed)" },
  { element: "X", type: "unknown", description: "Unknown large numeric" },
  { element: "Y", type: "unknown", description: "Unknown (1, 2 observed)" },
];

/**
 * Get the element name for a track property
 */
export function getElementForProperty(property: keyof import("../types/rc600").Track): string | undefined {
  const mapping = TRACK_ELEMENT_MAP.find(m => m.property === property);
  return mapping?.element;
}

/**
 * Get the property name for a track element
 */
export function getPropertyForElement(element: string): keyof import("../types/rc600").Track | undefined {
  const mapping = TRACK_ELEMENT_MAP.find(m => m.element === element);
  return mapping?.property;
}

/**
 * Track raw data storage (A-Y elements as numbers)
 */
export interface TrackRawData {
  A?: number;
  B?: number;
  C?: number;
  D?: number;
  E?: number;
  F?: number;
  G?: number;
  H?: number;
  I?: number;
  J?: number;
  K?: number;
  L?: number;
  M?: number;
  N?: number;
  O?: number;
  P?: number;
  Q?: number;
  R?: number;
  S?: number;
  T?: number;
  U?: number;
  V?: number;
  W?: number;
  X?: number;
  Y?: number;
}

/**
 * Input setup interface for the 7-bit bitmask in element Q
 */
export interface InputSetup {
  mic1: boolean;
  mic2: boolean;
  inst1L: boolean;
  inst1R: boolean;
  inst2L: boolean;
  inst2R: boolean;
  rhythm: boolean;
}

/**
 * Decode element Q (7-bit bitmask) to input setup object
 * Bit order (MSB to LSB): rhythm, inst2R, inst2L, inst1R, inst1L, mic2, mic1
 */
export function decodeInputSetup(value: number): InputSetup {
  return {
    mic1: (value & (1 << 0)) !== 0,      // Bit 0
    mic2: (value & (1 << 1)) !== 0,      // Bit 1
    inst1L: (value & (1 << 2)) !== 0,    // Bit 2
    inst1R: (value & (1 << 3)) !== 0,    // Bit 3
    inst2L: (value & (1 << 4)) !== 0,    // Bit 4
    inst2R: (value & (1 << 5)) !== 0,    // Bit 5
    rhythm: (value & (1 << 6)) !== 0,    // Bit 6
  };
}

/**
 * Encode input setup object to element Q (7-bit bitmask)
 * Bit order (MSB to LSB): rhythm, inst2R, inst2L, inst1R, inst1L, mic2, mic1
 */
export function encodeInputSetup(setup: Partial<InputSetup>, currentValue: number = 0): number {
  const current = decodeInputSetup(currentValue);
  const merged = { ...current, ...setup };

  return (
    (merged.mic1 ? (1 << 0) : 0) |      // Bit 0
    (merged.mic2 ? (1 << 1) : 0) |      // Bit 1
    (merged.inst1L ? (1 << 2) : 0) |    // Bit 2
    (merged.inst1R ? (1 << 3) : 0) |    // Bit 3
    (merged.inst2L ? (1 << 4) : 0) |    // Bit 4
    (merged.inst2R ? (1 << 5) : 0) |    // Bit 5
    (merged.rhythm ? (1 << 6) : 0)      // Bit 6
  );
}
