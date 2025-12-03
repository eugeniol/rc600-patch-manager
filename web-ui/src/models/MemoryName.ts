import { Serializable, createElement, getElementInt } from "./base";

/**
 * MemoryName - Handles the NAME tag which stores patch name as character codes
 *
 * The RC-600 stores patch names as 16 character codes (A-P),
 * where each character position has an ASCII code value.
 */
export class MemoryName implements Serializable {
  private static readonly CHAR_POSITIONS = "ABCDEFGHIJKLMNOP".split("");
  private static readonly MAX_LENGTH = 16;

  private name: string;

  constructor(name: string = "") {
    this.name = name.substring(0, MemoryName.MAX_LENGTH);
  }

  /**
   * Get the patch name
   */
  getName(): string {
    return this.name;
  }

  /**
   * Set the patch name (max 16 characters)
   */
  setName(name: string): void {
    this.name = name.substring(0, MemoryName.MAX_LENGTH);
  }

  /**
   * Serialize to XML NAME element
   */
  serialize(doc: Document): Element {
    const nameElement = doc.createElement("NAME");

    // Create character code elements for each position
    MemoryName.CHAR_POSITIONS.forEach((char, index) => {
      const charCode = index < this.name.length
        ? this.name.charCodeAt(index)
        : 0;

      nameElement.appendChild(
        createElement(doc, char, charCode.toString())
      );
    });

    return nameElement;
  }

  /**
   * Deserialize from XML NAME element
   */
  deserialize(element: Element): void {
    const chars: string[] = [];

    for (const char of MemoryName.CHAR_POSITIONS) {
      const charCode = getElementInt(element, char);
      if (charCode && charCode !== 0) {
        chars.push(String.fromCharCode(charCode));
      }
    }

    this.name = chars.join("").trim();
  }
}
