import { Serializable, getElementInt, createElement } from "./base";
import { Track as TrackType } from "../types/rc600";
import {
  TRACK_ELEMENT_MAP,
  TrackRawData,
  InputSetup,
  decodeInputSetup,
  encodeInputSetup,
} from "./TrackElementMap";

/**
 * Track - Represents a single track in an RC-600 patch
 *
 * Handles serialization/deserialization of track settings using the
 * A-Y element structure used by the RC-600.
 *
 * Element mapping (from Python implementation):
 * A: reverse, B: oneShot, C: balance, D: playLevel
 * E: playbackFX, F: trackType, G: tempoSync, H: playbackMode
 * I: startMode, J: stopMode, K: overdubMode
 * L: fx1, M: fx2, N: fx3
 * O: rhythmSync, P: quantize
 * Q: input setup bitmask (mic1, mic2, inst1L, inst1R, inst2L, inst2R, rhythm)
 * R-Y: unknown/unmapped
 */
export class Track implements Serializable {
  private trackNumber: number;
  private rawData: TrackRawData;
  private data: Partial<TrackType>;

  constructor(trackNumber: number) {
    this.trackNumber = trackNumber;
    this.rawData = {};
    this.data = {
      number: trackNumber,
    };
  }

  /**
   * Get the track data
   */
  getData(): TrackType {
    // Sync from raw data to typed data
    this.syncFromRaw();
    return { number: this.trackNumber, ...this.data } as TrackType;
  }

  /**
   * Update track data
   */
  setData(data: Partial<TrackType>): void {
    this.data = { ...this.data, ...data };
    // Sync to raw data
    this.syncToRaw();
  }

  /**
   * Get raw track data (A-Y elements)
   */
  getRawData(): TrackRawData {
    return { ...this.rawData };
  }

  /**
   * Set raw track data (A-Y elements)
   */
  setRawData(rawData: Partial<TrackRawData>): void {
    this.rawData = { ...this.rawData, ...rawData };
    this.syncFromRaw();
  }

  /**
   * Get input setup (decoded from element Q bitmask)
   */
  getInputSetup(): InputSetup {
    const qValue = this.rawData.Q ?? 0;
    return decodeInputSetup(qValue);
  }

  /**
   * Set input setup (encodes to element Q bitmask)
   */
  setInputSetup(setup: Partial<InputSetup>): void {
    const currentQ = this.rawData.Q ?? 0;
    this.rawData.Q = encodeInputSetup(setup, currentQ);
    this.syncFromRaw();
  }

  /**
   * Sync typed data from raw data based on element mapping
   */
  private syncFromRaw(): void {
    for (const mapping of TRACK_ELEMENT_MAP) {
      if (!mapping.property) continue;

      const element = mapping.element as keyof TrackRawData;
      const value = this.rawData[element];

      if (value === undefined) continue;

      switch (mapping.type) {
        case "boolean":
          this.data[mapping.property] = (value === 1) as any;
          break;
        case "number":
          this.data[mapping.property] = value as any;
          break;
        case "enum":
          // Store enums as strings (convert number to string)
          this.data[mapping.property] = value.toString() as any;
          break;
      }
    }

    // Decode input setup from element Q
    if (this.rawData.Q !== undefined) {
      const inputs = decodeInputSetup(this.rawData.Q);
      this.data.mic1 = inputs.mic1;
      this.data.mic2 = inputs.mic2;
      this.data.inst1L = inputs.inst1L;
      this.data.inst1R = inputs.inst1R;
      this.data.inst2L = inputs.inst2L;
      this.data.inst2R = inputs.inst2R;
      this.data.rhythm = inputs.rhythm;
    }
  }

  /**
   * Sync raw data from typed data based on element mapping
   */
  private syncToRaw(): void {
    for (const mapping of TRACK_ELEMENT_MAP) {
      if (!mapping.property) continue;

      const value = this.data[mapping.property];
      if (value === undefined) continue;

      const element = mapping.element as keyof TrackRawData;

      switch (mapping.type) {
        case "boolean":
          this.rawData[element] = value ? 1 : 0;
          break;
        case "number":
          this.rawData[element] = value as number;
          break;
        case "enum":
          // Convert string back to number if needed
          const numValue = typeof value === "string" ? parseInt(value, 10) : value;
          this.rawData[element] = numValue as number;
          break;
      }
    }

    // Encode input setup to element Q
    const inputSetup: Partial<InputSetup> = {};
    if (this.data.mic1 !== undefined) inputSetup.mic1 = this.data.mic1;
    if (this.data.mic2 !== undefined) inputSetup.mic2 = this.data.mic2;
    if (this.data.inst1L !== undefined) inputSetup.inst1L = this.data.inst1L;
    if (this.data.inst1R !== undefined) inputSetup.inst1R = this.data.inst1R;
    if (this.data.inst2L !== undefined) inputSetup.inst2L = this.data.inst2L;
    if (this.data.inst2R !== undefined) inputSetup.inst2R = this.data.inst2R;
    if (this.data.rhythm !== undefined) inputSetup.rhythm = this.data.rhythm;

    if (Object.keys(inputSetup).length > 0) {
      const currentQ = this.rawData.Q ?? 0;
      this.rawData.Q = encodeInputSetup(inputSetup, currentQ);
    }
  }

  /**
   * Serialize to XML TRACK element
   */
  serialize(doc: Document): Element {
    const trackElement = doc.createElement(`TRACK${this.trackNumber}`);

    // Ensure raw data is up to date
    this.syncToRaw();

    // Serialize all A-Y elements
    const elements = "ABCDEFGHIJKLMNOPQRSTUVWXY".split("");
    for (const elem of elements) {
      const value = this.rawData[elem as keyof TrackRawData];
      if (value !== undefined) {
        trackElement.appendChild(
          createElement(doc, elem, value.toString())
        );
      }
    }

    return trackElement;
  }

  /**
   * Deserialize from XML TRACK element
   */
  deserialize(element: Element): void {
    this.rawData = {};

    // Deserialize all A-Y elements
    const elements = "ABCDEFGHIJKLMNOPQRSTUVWXY".split("");
    for (const elem of elements) {
      const value = getElementInt(element, elem);
      if (value !== null) {
        this.rawData[elem as keyof TrackRawData] = value;
      }
    }

    // Sync to typed data
    this.syncFromRaw();
  }
}
