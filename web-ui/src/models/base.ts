/**
 * Base interface for models that can serialize to/from XML
 */
export interface Serializable {
  /**
   * Serialize the model to XML element
   * @param doc - The XML document to create elements from
   * @returns XML element representing this model
   */
  serialize(doc: Document): Element;

  /**
   * Deserialize from XML element
   * @param element - The XML element to deserialize from
   */
  deserialize(element: Element): void;
}

/**
 * Helper function to get text content of a child element
 */
export function getElementText(parent: Element, tagName: string): string | null {
  const element = parent.querySelector(tagName);
  return element?.textContent || null;
}

/**
 * Helper function to get integer value from a child element
 */
export function getElementInt(parent: Element, tagName: string): number | null {
  const text = getElementText(parent, tagName);
  return text ? parseInt(text, 10) : null;
}

/**
 * Helper function to create element with text content
 */
export function createElement(doc: Document, tagName: string, textContent: string): Element {
  const element = doc.createElement(tagName);
  element.textContent = textContent;
  return element;
}
