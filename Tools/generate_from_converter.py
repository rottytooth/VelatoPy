#!/usr/bin/env python3
"""
Script to generate a complete Hello World program using velato_converter.
Demonstrates how to use the converter to create Velato MIDI programs.
"""

from velato_converter import VelatoConverter


def main():
    """Generate and display suggestions for a complete Hello World program."""
    
    converter = VelatoConverter(root_note='C4')
    
    print("=" * 70)
    print("VELATO HELLO WORLD PROGRAM GENERATOR")
    print("=" * 70)
    print()
    
    # Define the Hello World program
    commands = [
        'Print ["H"]',
        'Print ["e"]',
        'Print ["l"]',
        'Print ["l"]',
        'Print ["o"]',
        'Print [","]',
        'Print [" "]',
        'Print ["W"]',
        'Print ["o"]',
        'Print ["r"]',
        'Print ["l"]',
        'Print ["d"]',
        'Print ["!"]'
    ]
    
    print("PSEUDOCODE COMMANDS:")
    print("-" * 70)
    for i, cmd in enumerate(commands, 1):
        print(f"{i:2}. {cmd}")
    print()
    
    print("VELATO NOTE SUGGESTIONS:")
    print("-" * 70)
    
    # Generate suggestions for each command
    for i, command in enumerate(commands, 1):
        suggestion = converter.suggest_notes(command)
        print(f"\n{i:2}. {command}")
        print(f"    Notes: {suggestion}")
    
    print()
    print("=" * 70)
    print("COMPLETE MIDI FILE GENERATION")
    print("=" * 70)
    print()
    
    # Generate the complete MIDI file
    output_file = 'generated_hello_world.mid'
    converter.convert_to_midi(commands, output_file)
    
    print(f"✓ MIDI file generated: {output_file}")
    print()
    print("To run the program:")
    print(f"  python velato.py {output_file}")
    print()
    print("Expected output:")
    print("  Hello, World!")
    print()


if __name__ == '__main__':
    main()
