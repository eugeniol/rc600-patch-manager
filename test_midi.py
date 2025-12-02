import mido

# List available MIDI input ports
print("Available MIDI Input Ports:")
for i, name in enumerate(mido.get_input_names()):
    print(f"{i}: {name}")

# Automatically find the RC-600 port
rc600_port = next((name for name in mido.get_input_names() if "RC-600" in name), None)

if not rc600_port:
    print("RC-600 not found. Is it connected via USB?")
    exit(1)

print(f"\nListening to: {rc600_port}\nPress Ctrl+C to stop.\n")

# Open MIDI input and ignore only 'clock' messages
with mido.open_input(rc600_port) as inport:
    for msg in inport:
        if msg.type != 'clock':
            print(msg)
