/**
 * Test script to verify XML parsing with the sample XML
 *
 * This can be run in the browser console or as a test
 */

import { Patch } from "./Patch";

const sampleXML = `<?xml version="1.0" encoding="utf-8"?>
<database name="RC-600" revision="0">
<mem id="35">
<NAME>
    <A>77</A>
    <B>101</B>
    <C>109</C>
    <D>111</D>
    <E>114</E>
    <F>121</F>
    <G>48</G>
    <H>57</H>
    <I>32</I>
    <J>32</J>
    <K>32</K>
    <L>32</L>
</NAME>
<TRACK1>
    <A>0</A>
    <B>0</B>
    <C>50</C>
    <D>100</D>
    <E>0</E>
    <F>0</F>
    <G>0</G>
    <H>1</H>
    <I>1</I>
    <J>9</J>
    <K>0</K>
    <L>1</L>
    <M>1</M>
    <N>1</N>
    <O>1</O>
    <P>0</P>
    <Q>126</Q>
    <R>1</R>
    <S>2</S>
    <T>0</T>
    <U>760</U>
    <V>139263</V>
    <W>1</W>
    <X>278526</X>
    <Y>1</Y>
</TRACK1>
<TRACK2>
    <A>0</A>
    <B>0</B>
    <C>50</C>
    <D>100</D>
    <E>0</E>
    <F>0</F>
    <G>0</G>
    <H>1</H>
    <I>1</I>
    <J>9</J>
    <K>0</K>
    <L>1</L>
    <M>1</M>
    <N>1</N>
    <O>1</O>
    <P>0</P>
    <Q>126</Q>
    <R>1</R>
    <S>2</S>
    <T>0</T>
    <U>760</U>
    <V>139263</V>
    <W>1</W>
    <X>278526</X>
    <Y>1</Y>
</TRACK2>
<TRACK3>
    <A>0</A>
    <B>0</B>
    <C>50</C>
    <D>100</D>
    <E>0</E>
    <F>0</F>
    <G>0</G>
    <H>1</H>
    <I>1</I>
    <J>9</J>
    <K>0</K>
    <L>1</L>
    <M>1</M>
    <N>1</N>
    <O>1</O>
    <P>0</P>
    <Q>126</Q>
    <R>1</R>
    <S>2</S>
    <T>0</T>
    <U>760</U>
    <V>139263</V>
    <W>1</W>
    <X>278526</X>
    <Y>1</Y>
</TRACK3>
<TRACK4>
    <A>0</A>
    <B>0</B>
    <C>50</C>
    <D>100</D>
    <E>0</E>
    <F>0</F>
    <G>0</G>
    <H>0</H>
    <I>1</I>
    <J>8</J>
    <K>0</K>
    <L>1</L>
    <M>1</M>
    <N>1</N>
    <O>1</O>
    <P>0</P>
    <Q>63</Q>
    <R>1</R>
    <S>1</S>
    <T>0</T>
    <U>760</U>
    <V>139263</V>
    <W>1</W>
    <X>139263</X>
    <Y>1</Y>
</TRACK4>
<TRACK5>
    <A>0</A>
    <B>0</B>
    <C>50</C>
    <D>100</D>
    <E>0</E>
    <F>0</F>
    <G>0</G>
    <H>0</H>
    <I>0</I>
    <J>1</J>
    <K>0</K>
    <L>1</L>
    <M>1</M>
    <N>1</N>
    <O>1</O>
    <P>0</P>
    <Q>127</Q>
    <R>1</R>
    <S>0</S>
    <T>0</T>
    <U>1200</U>
    <V>88200</V>
    <W>0</W>
    <X>0</X>
    <Y>2</Y>
</TRACK5>
<TRACK6>
    <A>0</A>
    <B>0</B>
    <C>50</C>
    <D>100</D>
    <E>0</E>
    <F>0</F>
    <G>0</G>
    <H>0</H>
    <I>0</I>
    <J>1</J>
    <K>0</K>
    <L>1</L>
    <M>1</M>
    <N>1</N>
    <O>1</O>
    <P>0</P>
    <Q>127</Q>
    <R>1</R>
    <S>0</S>
    <T>0</T>
    <U>1200</U>
    <V>88200</V>
    <W>0</W>
    <X>0</X>
    <Y>2</Y>
</TRACK6>
</mem>
</database>`;

export function testSampleXML() {
  console.log("=== Testing Sample XML Parsing ===\n");

  // Parse the sample XML
  const patch = Patch.fromXMLString(sampleXML, 35, "A", "0");

  if (!patch) {
    console.error("Failed to parse sample XML");
    return;
  }

  console.log("✓ Successfully parsed XML\n");

  // Test patch data
  const patchData = patch.toPatchType();
  console.log("Patch Info:");
  console.log(`  Slot: ${patchData.slot}`);
  console.log(`  Name: "${patchData.name}"`);
  console.log(`  Bank: ${patchData.bank}`);
  console.log(`  Modified: ${patchData.modified}\n`);

  // Test track data
  console.log("Track Data:");
  patchData.tracks.forEach((track, index) => {
    console.log(`  Track ${index + 1}:`);
    console.log(`    Balance: ${track.balance}`);
    console.log(`    Play Level: ${track.playLevel}`);
    console.log(`    Reverse: ${track.reverse}`);
    console.log(`    One Shot: ${track.oneShot}`);
    console.log(`    Inputs: mic1=${track.mic1}, mic2=${track.mic2}, inst1L=${track.inst1L}, inst1R=${track.inst1R}, inst2L=${track.inst2L}, inst2R=${track.inst2R}, rhythm=${track.rhythm}`);
  });

  // Test serialization
  console.log("\n=== Testing XML Serialization ===\n");
  const serialized = patch.toXMLString();
  console.log("Serialized XML (first 500 chars):");
  console.log(serialized.substring(0, 500) + "...\n");

  // Test round-trip
  const patch2 = Patch.fromXMLString(serialized, 35, "A", "0");
  if (patch2) {
    const patchData2 = patch2.toPatchType();
    console.log("✓ Round-trip successful");
    console.log(`  Name matches: ${patchData2.name === patchData.name}`);
    console.log(`  Track 1 balance matches: ${patchData2.tracks[0].balance === patchData.tracks[0].balance}`);
  } else {
    console.error("✗ Round-trip failed");
  }

  return patch;
}

// Export for use in browser console
if (typeof window !== "undefined") {
  (window as any).testSampleXML = testSampleXML;
}
