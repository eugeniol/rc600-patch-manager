import { Serializable, getElementInt, createElement } from "./base";
import { Patch as PatchType } from "../types/rc600";
import { MemoryName } from "./MemoryName";
import { Track } from "./Track";

/**
 * Patch - Represents a complete RC-600 memory patch
 *
 * Handles serialization/deserialization of:
 * - Patch metadata (name, slot, bank, count)
 * - Tempo/BPM settings
 * - All 6 tracks with their configurations
 *
 * XML Structure:
 * <database name="RC-600" revision="0">
 *   <mem id="slot">
 *     <NAME>...</NAME>
 *     <TRACK1>...</TRACK1>
 *     ...
 *   </mem>
 * </database>
 */
export class Patch implements Serializable {
  private slot: number;
  private bank: "A" | "B";
  private count: string;
  private memoryName: MemoryName;
  private bpm?: number;
  private tracks: Track[];
  private modified: boolean;

  constructor(slot: number, bank: "A" | "B" = "A", count: string = "0") {
    this.slot = slot;
    this.bank = bank;
    this.count = count;
    this.memoryName = new MemoryName(`Patch ${slot}`);
    this.tracks = Array.from({ length: 6 }, (_, i) => new Track(i + 1));
    this.modified = false;
  }

  /**
   * Get the patch as a PatchType object
   */
  toPatchType(): PatchType {
    return {
      slot: this.slot,
      name: this.memoryName.getName(),
      bank: this.bank,
      count: this.count,
      bpm: this.bpm,
      tracks: this.tracks.map((track) => track.getData()),
      modified: this.modified,
    };
  }

  /**
   * Update patch from PatchType object
   */
  fromPatchType(patchData: PatchType): void {
    this.slot = patchData.slot;
    this.bank = patchData.bank;
    this.count = patchData.count || "0";
    this.memoryName.setName(patchData.name);
    this.bpm = patchData.bpm;
    this.modified = patchData.modified;

    // Update tracks
    patchData.tracks.forEach((trackData, index) => {
      if (index < this.tracks.length) {
        this.tracks[index].setData(trackData);
      }
    });
  }

  /**
   * Get the patch name
   */
  getName(): string {
    return this.memoryName.getName();
  }

  /**
   * Set the patch name
   */
  setName(name: string): void {
    this.memoryName.setName(name);
    this.modified = true;
  }

  /**
   * Get the BPM
   */
  getBPM(): number | undefined {
    return this.bpm;
  }

  /**
   * Set the BPM
   */
  setBPM(bpm: number): void {
    this.bpm = bpm;
    this.modified = true;
  }

  /**
   * Get a track by number (1-6)
   */
  getTrack(trackNumber: number): Track | undefined {
    if (trackNumber < 1 || trackNumber > 6) {
      return undefined;
    }
    return this.tracks[trackNumber - 1];
  }

  /**
   * Mark the patch as modified
   */
  setModified(modified: boolean): void {
    this.modified = modified;
  }

  /**
   * Serialize to XML mem element (without database wrapper)
   */
  serialize(doc: Document): Element {
    const memElement = doc.createElement("mem");
    memElement.setAttribute("id", this.slot.toString());

    // Add NAME element
    memElement.appendChild(this.memoryName.serialize(doc));

    // Add TEMPO element if BPM is set
    if (this.bpm !== undefined) {
      memElement.appendChild(createElement(doc, "TEMPO", this.bpm.toString()));
    }

    // Add all tracks
    this.tracks.forEach((track) => {
      memElement.appendChild(track.serialize(doc));
    });

    return memElement;
  }

  /**
   * Deserialize from XML mem element
   */
  deserialize(element: Element): void {
    // Get slot from id attribute
    const idAttr = element.getAttribute("id");
    if (idAttr) {
      this.slot = parseInt(idAttr, 10);
    }

    // Deserialize NAME
    const nameElement = element.querySelector("NAME");
    if (nameElement) {
      this.memoryName.deserialize(nameElement);
    }

    // Deserialize TEMPO
    const bpm = getElementInt(element, "TEMPO");
    if (bpm !== null) {
      this.bpm = bpm;
    }

    // Deserialize tracks
    this.tracks.forEach((track, index) => {
      const trackNumber = index + 1;
      const trackElement = element.querySelector(`TRACK${trackNumber}`);
      if (trackElement) {
        track.deserialize(trackElement);
      }
    });
  }

  /**
   * Serialize to full XML string with database wrapper
   */
  toXMLString(): string {
    const doc = document.implementation.createDocument(null, null, null);

    // Create database root
    const database = doc.createElement("database");
    database.setAttribute("name", "RC-600");
    database.setAttribute("revision", "0");

    // Add mem element
    const memElement = this.serialize(doc);
    database.appendChild(memElement);

    doc.appendChild(database);

    // Add count element at the end (outside database)
    const countElement = createElement(doc, "count", this.count);
    doc.appendChild(countElement);

    // Serialize to string
    const serializer = new XMLSerializer();
    let xmlString = '<?xml version="1.0" encoding="utf-8"?>\n';
    xmlString += serializer.serializeToString(doc);

    // Post-process: Convert NUM_123 back to 123, HASH back to #
    xmlString = xmlString.replace(/<(\/?)\s*NUM_(\d+)>/g, "<$1$2>");
    xmlString = xmlString.replace(/<(\/?)\s*HASH>/g, "<$1#>");

    return xmlString;
  }

  /**
   * Static method to create a Patch from XML string
   */
  static fromXMLString(
    xmlContent: string,
    slot: number,
    bank: "A" | "B",
    count: string
  ): Patch | null {
    try {
      // Pre-process the XML to handle numeric tags and hash tags
      const processedXML = preprocessRC600XML(xmlContent);

      // Parse XML
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(processedXML, "text/xml");

      // Check for parsing errors
      const parserError = xmlDoc.querySelector("parsererror");
      if (parserError) {
        console.error("XML parsing error:", parserError.textContent);
        return null;
      }

      // Find the mem element (could be root or inside database)
      let memElement = xmlDoc.querySelector("mem");
      if (!memElement) {
        // Maybe the root is the mem element itself
        if (xmlDoc.documentElement.tagName === "mem") {
          memElement = xmlDoc.documentElement;
        }
      }

      if (!memElement) {
        console.error("Could not find <mem> element in XML");
        return null;
      }

      // Create patch and deserialize
      const patch = new Patch(slot, bank, count);
      patch.deserialize(memElement);

      return patch;
    } catch (error) {
      console.error("Error parsing patch:", error);
      return null;
    }
  }
}

/**
 * Pre-process RC-600 XML to fix malformed tags
 * - Convert numeric tags like <123> to <NUM_123>
 * - Convert <#> to <HASH>
 * - Remove the <count> line at the end
 */
function preprocessRC600XML(xmlContent: string): string {
  const lines = xmlContent.split("\n");
  const processedLines: string[] = [];

  for (let line of lines) {
    // Convert numeric tags: <123> -> <NUM_123>, </123> -> </NUM_123>
    if (/<\/?(\d+)>/.test(line)) {
      line = line.replace(/<(\/?)([\d]+)>/g, "<$1NUM_$2>");
    }

    // Convert hash tags: <#> -> <HASH>, </#> -> </HASH>
    if (/<\/?#>/.test(line)) {
      line = line.replace(/<(\/?)(#)>/g, "<$1HASH>");
    }

    // Skip the <count> line (it's at the end of the file)
    if (/^<count>[\w]+<\/count>/.test(line.trim())) {
      continue;
    }

    processedLines.push(line);
  }

  return processedLines.join("\n");
}
