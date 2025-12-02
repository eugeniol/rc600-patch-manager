import csv
import os
from io import BytesIO
import sys
import xml.etree.ElementTree as ET
import re
import copy


def read_last_line(filename):
    with open(filename, 'rb') as f:
        f.seek(-2, 2)  # Go to the second last byte
        while f.read(1) != b'\n':
            f.seek(-2, 1)
        return f.readline().decode()


def get_latest(path, memslot):
    letters = 'AB'
    counts = []
    for mem_sec in letters:
        xml_path = f'{path}/MEMORY{memslot:03}{mem_sec}.RC0'
        line = read_last_line(xml_path)
        if line.strip():
            t = re.search(r"^<count>(\w+)</count>", line)
            if not t:
                continue
            count = t.group(1)
            count = int(count, 16)
            counts.append(count)

    m = max(*counts)
    max_index = counts.index(m)
    return letters[max_index], m


def from_rc600_xml(line):
    if re.search(r"<(/?)(\d+)>", line):
        line = re.sub(r"<(/?)(\d+)>", r"<\1NUM_\2>", line)
    elif re.search(r"<(/?)#>", line):
        line = re.sub(r"<(/?)#>", r"<\1HASH>", line)
    elif re.search(r"^<count>(\w+)</count>", line):
        count = re.search(r"^<count>(\w+)</count>", line).group(1)
        count = int(count, 16)
        line = ''

    return line


def to_rc600_xml(line):
    if re.search(r"<(/?)(NUM_\d+)>", line):
        line = re.sub(r"<(/?)NUM_(\d+)>", r"<\1\2>", line)
    elif re.search(r"<(/?)HASH>", line):
        line = re.sub(r"<(/?)HASH>", r"<\1#>", line)

    return line


def parse_rc600_tree(xml_path):
    with open(xml_path, encoding="utf-8") as f:
        xml_content = ''
        for line in f.readlines():
            xml_content += from_rc600_xml(line)

        root = ET.fromstring(xml_content)
        tree = ET.ElementTree(root)
        return tree


def save_xml_to_rc600(tree, memslot, mem_sec, count, volume_path='.'):
    buffer = BytesIO()
    tree.write(buffer, encoding='utf-8', xml_declaration=False)
    # Get string and fix the tag names
    new_mem_sec = 'A' if mem_sec == 'B' else 'B'
    output_xml = f'MEMORY{memslot:03}{new_mem_sec}.RC0'
    output_xml_path = os.path.join(volume_path, output_xml)
    lines = buffer.getvalue().decode('utf-8').split('\n')
    with open(output_xml_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        for line in lines:
            # print(line)
            f.write(to_rc600_xml(line)+'\n')
        count += 1
        f.write('<count>{:04X}</count>'.format(count))

    print(f'Saved to: {output_xml_path}')


def get_mem_file(cwd, memslot):
    (mem_sec, count) = get_latest(cwd, memslot)
    return f'{cwd}/MEMORY{memslot:03}{mem_sec}.RC0', mem_sec, count


class Track:
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return self.node.tag

    @property
    def input_setup(self):
        num = int(self.node.find('Q').text, 10)
        result = {}
        keys = ('rythm',
                'inst2r',
                'inst2l',
                'inst1r',
                'inst1l',
                'mic2',
                'mic1')
        for i, bit in enumerate((bin(num)[2:].zfill(7))):
            result[keys[i]] = bit
        return result

    def update_setup(self, rythm=None, inst2r=None, inst2l=None, inst1r=None, inst1l=None, mic2=None, mic1=None):
        input_setup = self.input_setup
        keys = ('rythm',
                'inst2r',
                'inst2l',
                'inst1r',
                'inst1l',
                'mic2',
                'mic1')
        args = [rythm, inst2r, inst2l, inst1r, inst1l, mic2, mic1]
        num = sum([int(arg if arg is not None else input_setup[keys[i]]) << (6 - i) for i, arg in enumerate(args)])
        self.node.find('Q').text = str(num)

        return num


class Memory:
    cwd = '.'

    def __init__(self, slot, cwd=None):
        self.slot = slot
        if cwd:
            self.cwd = cwd

        self._name = None
        self.root = self.read()

    def read(self):
        (xml_path, seq, count) = get_mem_file(self.cwd, self.slot)
        print("Opening: ", xml_path)
        self.xml_path = xml_path
        self.seq = seq
        self.count = count
        return parse_rc600_tree(self.xml_path)

    def save(self, to_dir=None, slot=None):
        if not to_dir:
            to_dir = self.cwd

        if slot:
            self.slot = slot

        save_xml_to_rc600(self.root, self.slot, self.seq, self.count, to_dir)

    @property
    def name(self):
        if not self._name:
            mem = self.root.find('mem')
            name_element = mem.find('NAME')
            self._name = ''.join([chr(int(child.text)) for child in name_element]).strip()
        return self._name

    @property
    def tracks(self):
        mem = self.root.find('mem')
        return [Track(mem.find(f'TRACK{n}')) for n in range(1, 7)]

    @property
    def bpm(self):
        """Get BPM from MASTER/A node, divided by 10 for exact value"""
        try:
            mem = self.root.find('mem')
            if mem is not None:
                master = mem.find('MASTER')
                if master is not None:
                    a_element = master.find('A')
                    if a_element is not None and a_element.text:
                        bpm_raw = int(a_element.text)
                        return bpm_raw / 10.0
        except (ValueError, AttributeError):
            pass
        return None

    @name.setter
    def name(self, value):
        mem = self.root.find('mem')
        value = f'{value}            '
        name_element = mem.find('NAME')
        for index, child in enumerate(name_element):
            child.text = str(ord(value[index]))

        self._name = None

    def copy_to(self, target, path):
        assert path, "No path specified"

        parts = path.split('/')
        assert parts[0] == '.', f"Invalid path: {path}, it should start with '.'"
        assert len(parts) > 1, f"Invalid path: {path}, it should have at least two parts"

        source = self.root.find(path)
        assert source is not None, f"Couldn't find source node: {path}"

        old_node = target.root.find(path)
        assert old_node is not None, f"Couldn't find target node: {path}"

        parts.pop()
        parent = target.root.find('/'.join(parts))
        assert parent is not None, f"Couldn't find parent node: {path}"

        new_node = copy.deepcopy(source)
        for key in new_node.keys():
            new_node.set(key, old_node.get(key))

        for i, child in enumerate(list(parent)):
            if child is old_node:
                parent.remove(child)
                cp = copy.deepcopy(new_node)
                parent.insert(i, cp)
                return cp

    def __str__(self):
        return f"Patch: '{self.name}',{self.slot} {self.seq}"


COPY_EFFECTS = False
COPY_ASSIGNS = range(1, 17)
MEMORY_SOURCE = 38
# MEMORY_TARGETS = range(30, 38)
MEMORY_TARGETS = range(10, 31)


def do_copy():
    # if len(sys.argv) > 1:
    #     memslot = int(sys.argv[1])
    # else:
    #     raise Exception("No memslot specified")

    # cwd = './DATA'
    cwd = PROJECT_PATH
    for i in range(30, 40):
        m = Memory(i)
        print(i, m.seq, m.count, m.name)

    source = Memory(MEMORY_SOURCE)
    for mem in MEMORY_TARGETS:
        dest = Memory(mem)
        nodes_to_copy = []

        for i in COPY_ASSIGNS:
            nodes_to_copy.append(f'./mem/ASSIGN{i}')

        if COPY_EFFECTS:
            nodes_to_copy.append('./ifx')
            nodes_to_copy.append('./tfx')

        for n in nodes_to_copy:
            source.copy_to(dest, n)

        dest.save(cwd)


def do_test():
    pass


def update_names(source='./lista.csv'):
    """
    given a csv file, updates the names in the memory
    """
    with open(source, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(int(row['Banco']))
            mem = Memory(int(row['Banco']))
            print(mem, row['ShortName'])
            mem.name = row['ShortName']
            mem.save()
            # mem.name = row['ShortName']


def update_inputs():
    """
        set mic inputs muted for record but only tracks 5 and 6 mic2 on
    """
    for ix in range(17, 55):
        mem = Memory(ix)
        for track in mem.tracks:
            track.update_setup(mic1=0)
            track.update_setup(mic2=0)
        mem.tracks[4].update_setup(mic2=1)
        mem.tracks[5].update_setup(mic2=1)
        mem.save()


def armar_set():
    file = './2025-11-13-Recital.csv'
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        slot = 1
        for row in reader:
            # print(int(row['Banco']))
            mem = Memory(int(row['Banco']))
            mem.name = row['ShortName']
            print(f'Saved {slot}: {mem.name}')
            mem.save(slot=slot)
            slot += 1


def get_data_path():
    """
    Prompt user for DATA path with intelligent defaults
    """
    default_paths = [
        '/Volumes/RC-600/ROLAND/DATA',
        './DATA'
    ]

    print("\n=== RC-600 Patch Manager ===\n")
    print("Available DATA paths:")

    available = []
    for i, path in enumerate(default_paths, 1):
        if os.path.exists(path):
            print(f"  {i}. {path} [EXISTS]")
            available.append(path)
        else:
            print(f"  {i}. {path} [not found]")

    print(f"  {len(default_paths) + 1}. Enter custom path")

    while True:
        choice = input(f"\nSelect path (1-{len(default_paths) + 1}): ").strip()

        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(default_paths):
                selected_path = default_paths[choice_num - 1]
                if os.path.exists(selected_path):
                    return selected_path
                else:
                    confirm = input(f"Path '{selected_path}' does not exist. Use anyway? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return selected_path
            elif choice_num == len(default_paths) + 1:
                custom_path = input("Enter custom path: ").strip()
                if os.path.exists(custom_path):
                    return custom_path
                else:
                    confirm = input(f"Path '{custom_path}' does not exist. Use anyway? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return custom_path

        print("Invalid choice. Please try again.")


def show_menu():
    """
    Display main menu and handle user selection
    """
    menu_options = {
        '1': ('Update patch names from CSV', update_names),
        '2': ('Configure track inputs (mic settings)', update_inputs),
        '3': ('Create setlist from CSV', armar_set),
        '4': ('List memory slots (30-39)', lambda: list_memories(30, 40)),
        '5': ('Exit', None)
    }

    while True:
        print("\n" + "="*40)
        print("RC-600 Patch Manager - Main Menu")
        print("="*40)
        for key, (description, _) in menu_options.items():
            print(f"  {key}. {description}")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == '5':
            print("Goodbye!")
            break

        if choice in menu_options and choice != '5':
            _, func = menu_options[choice]
            try:
                print()
                if choice == '1':
                    csv_file = input("Enter CSV filename (default: ./lista.csv): ").strip()
                    if not csv_file:
                        csv_file = './lista.csv'
                    func(csv_file)
                elif choice == '3':
                    csv_file = input("Enter setlist CSV filename (default: ./2025-11-13-Recital.csv): ").strip()
                    if not csv_file:
                        csv_file = './2025-11-13-Recital.csv'
                    # Update armar_set to accept parameter
                    armar_set_with_file(csv_file)
                else:
                    func()
                print("\nOperation completed!")
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Invalid choice. Please try again.")


def list_memories(start, end):
    """
    List memory slots with their details
    """
    for i in range(start, end):
        try:
            m = Memory(i)
            print(f"{i:3d} | Bank: {m.seq} | Count: {m.count:04X} | Name: {m.name}")
        except Exception as e:
            print(f"{i:3d} | Error: {e}")


def armar_set_with_file(csv_file=None):
    """
    Create setlist from CSV file
    """
    if not csv_file:
        csv_file = './2025-11-13-Recital.csv'

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        slot = 1
        for row in reader:
            mem = Memory(int(row['Banco']))
            mem.name = row['ShortName']
            print(f'Saved {slot}: {mem.name}')
            mem.save(slot=slot)
            slot += 1


if __name__ == '__main__':
    PROJECT_PATH = get_data_path()
    Memory.cwd = PROJECT_PATH
    print(f"\nUsing DATA path: {PROJECT_PATH}\n")

    show_menu()
