import { Patch as PatchType } from "../types/rc600";
import { Patch } from "../models";

/**
 * Get the latest bank (A or B) by reading the count from the last line
 */
export async function getLatestBank(
  directoryHandle: FileSystemDirectoryHandle,
  slot: number
): Promise<{ bank: "A" | "B"; count: number } | null> {
  //console.log (`[RC600 Parser] Checking latest bank for slot ${slot}...`);

  const banks = ["A", "B"] as const;
  const counts: { bank: "A" | "B"; count: number }[] = [];

  for (const bank of banks) {
    const fileName = `MEMORY${slot.toString().padStart(3, "0")}${bank}.RC0`;

    try {
      const fileHandle = await directoryHandle.getFileHandle(fileName);
      const file = await fileHandle.getFile();
      const content = await file.text();

      // Get the last line which contains the count
      const lines = content.split("\n");
      const lastLine = lines[lines.length - 1].trim();

      const countMatch = lastLine.match(/^<count>([\w]+)<\/count>/);
      if (countMatch) {
        const hexCount = countMatch[1];
        const count = parseInt(hexCount, 16);
        counts.push({ bank, count });
        //console.log (`[RC600 Parser] Bank ${bank} count: ${count} (0x${hexCount})`);
      }
    } catch (error) {
      //console.log (`[RC600 Parser] File ${fileName} not found or error reading:`, error);
    }
  }

  if (counts.length === 0) {
    console.warn(`[RC600 Parser] No valid banks found for slot ${slot}`);
    return null;
  }

  // Return the bank with the highest count
  const latest = counts.reduce((prev, current) =>
    current.count > prev.count ? current : prev
  );

  //console.log (`[RC600 Parser] Latest bank for slot ${slot}: ${latest.bank} (count: ${latest.count})`);
  return latest;
}

/**
 * Parse RC-600 XML and extract patch data
 */
export function parseRC600Patch(
  xmlContent: string,
  slot: number,
  bank: "A" | "B",
  count: number
): PatchType | null {
  //console.log (`[RC600 Parser] Parsing patch for slot ${slot}, bank ${bank}...`);

  // Use the Patch model to deserialize from XML
  const countHex = count.toString(16).toUpperCase();
  const patch = Patch.fromXMLString(xmlContent, slot, bank, countHex);

  if (patch) {
    //console.log ('[RC600 Parser] Successfully parsed patch:', patch.toPatchType());
    return patch.toPatchType();
  }

  return null;
}

/**
 * Load a patch from the file system
 */
export async function loadPatch(
  directoryHandle: FileSystemDirectoryHandle,
  slot: number
): Promise<PatchType | null> {
  //console.log (`[RC600 Parser] Loading patch ${slot}...`);

  // Get the latest bank
  const latest = await getLatestBank(directoryHandle, slot);
  if (!latest) {
    return null;
  }

  // Read the file
  const fileName = `MEMORY${slot.toString().padStart(3, "0")}${
    latest.bank
  }.RC0`;
  //console.log (`[RC600 Parser] Reading file: ${fileName}`);

  try {
    const fileHandle = await directoryHandle.getFileHandle(fileName);
    const file = await fileHandle.getFile();
    const content = await file.text();

    //console.log (`[RC600 Parser] File size: ${content.length} bytes`);

    // Parse the patch
    return parseRC600Patch(content, slot, latest.bank, latest.count);
  } catch (error) {
    console.error(`[RC600 Parser] Error loading patch ${slot}:`, error);
    return null;
  }
}
