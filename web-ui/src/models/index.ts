/**
 * RC-600 Model Classes
 *
 * This module provides model classes for serializing/deserializing
 * RC-600 patch data to/from XML format.
 */

export type { Serializable } from "./base";
export { getElementText, getElementInt, createElement } from "./base";
export { MemoryName } from "./MemoryName";
export { Track } from "./Track";
export { Patch } from "./Patch";
export {
  TRACK_ELEMENT_MAP,
  decodeInputSetup,
  encodeInputSetup,
  type TrackRawData,
  type ElementMapping,
  type InputSetup,
} from "./TrackElementMap";
