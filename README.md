# Velato Interpreter

A Python implementation of the [Velato](https://velato.net) programming language, where code is inscribed as music. Each program is a MIDI file; the sequence of music notes determine the program's commands and logic.

This interpreter is based on the [reference Velato compiler](https://github.com/rottytooth/Velato) written in C# (2009).

## Components

### 1. Velato Interpreter (`velato.py`)

**Usage:**
```bash
python velato.py <midi_file.mid> [-v]
```

**Options:**
- `-v, --verbose`: Print notes as they are processed

**Example:**
```bash
python velato.py Programs/Programs_print_hello_world.mid
# Output: Hello, World!
```

### 2. Velato Converter (`velato_converter.py`)

A tool to convert pseudocode commands into Velato MIDI note sequences.

**Usage:**
```python
from velato_converter import VelatoConverter

converter = VelatoConverter(root_note='C4')

# Get note suggestions for a command
notes = converter.suggest_notes('Print ["H"]')
print(notes)  # e.g., "C4 E4 A4 D5 E5 B5"

# Generate a complete MIDI file
commands = [
    'Print ["H"]',
    'Print ["i"]',
    'While ["!"]'
]
converter.convert_to_midi(commands, 'output.mid')
```

## Example Scripts

### 1. Generate Program from Converter (`examples/generate_from_converter.py`)

Demonstrates how to use `velato_converter` to create a complete "Hello, World!" program.

### 2. Generate Sheet Music (`examples/lilypond_mid_and_pdf.py`)

Uses `music21` to create both MIDI files and sheet music (PDF) from Velato programs.


## Running Tests

The project includes comprehensive tests using pytest:

```bash
pytest
```

## Resources

- [Velato site](http://danieltemkin.com/Esolangs/Velato/)
- [Velato on Esolangs Wiki](https://esolangs.org/wiki/Velato)
- [Original C# Implementation](https://github.com/rottytooth/Velato)
