#!/usr/bin/env python3
"""
Velato Suggestion Tool - Convert pseudocode to a simple series of Velato MIDI notes

Based on PseudoToVelato.cs from https://github.com/rottytooth/Velato
"""

import re
from typing import List, Tuple
from mido import Message, MidiFile, MidiTrack

from velato_common import Interval, get_command_map, DIGIT_TO_INTERVAL, NOTE_NAMES


class VelatoNoteSuggestionTool:
    """Converts pseudocode commands to Velato note suggestions"""
    
    def __init__(self, root_note: str = 'C4'):
        """Initialize converter with a root note (e.g., 'C4', 'D#3')"""
        self.root_note = root_note
        self.root_pitch = self._parse_note(root_note)
        self.command_map = get_command_map()
    
    def _parse_note(self, note: str) -> int:
        """Convert note name to MIDI pitch number"""
        # Extract note name and octave
        match = re.match(r'([A-G][#&]?)(\d+)', note)
        if not match:
            raise ValueError(f"Invalid note format: {note}")
        
        note_name = match.group(1)
        octave = int(match.group(2))
        
        # Handle flats
        if '&' in note_name:
            note_name = NOTE_NAMES[(NOTE_NAMES.index(note_name[0]) - 1) % 12]
        
        # Calculate MIDI pitch
        note_index = NOTE_NAMES.index(note_name)
        return (octave + 1) * 12 + note_index
    
    def _get_note_by_interval(self, interval: Interval, include_octave: bool = False) -> str:
        """Get note at specified interval from root note"""
        new_pitch = self.root_pitch + interval
        note_index = new_pitch % 12
        if include_octave:
            octave = (new_pitch // 12) - 1
            return f"{NOTE_NAMES[note_index]}{octave}"
        return NOTE_NAMES[note_index]
    
    def _get_intervals_for_int(self, val: int) -> List[str]:
        """Convert an integer to a sequence of interval notes, ending with Perfect Fifth"""
        if val == 0:
            return [self._get_note_by_interval(Interval.PERFECT_FIFTH)]
        
        # Extract digits (this gives them in reverse order - least significant first)
        digits = []
        num = abs(val)
        while num > 0:
            digits.append(num % 10)
            num = num // 10
        
        # Reverse to get most significant digit first
        digits.reverse()
        
        intervals = []
        for digit in digits:
            # PERFECT_FIFTH (7) is reserved for terminator
            interval_name = DIGIT_TO_INTERVAL.get(digit, 'MAJOR_SIXTH')  # fallback for invalid digit 6
            interval = Interval[interval_name]
            intervals.append(self._get_note_by_interval(interval, include_octave=False))
        
        # Always end with Perfect Fifth
        intervals.append(self._get_note_by_interval(Interval.PERFECT_FIFTH, include_octave=False))
        return intervals
    
    def suggest_notes(self, command: str) -> List[str]:
        """
        Suggest Velato notes for a pseudocode command.
        
        Examples:
            suggest_notes("Starting Note [C4]")
            suggest_notes("Declare [E3, int]")
            suggest_notes("Let [E3, 99]")
            suggest_notes("Print ['H']")
            suggest_notes("Print [E3]")
            suggest_notes("While [E3 > 0]")
            suggest_notes("End While")
        """
        notes = []
        
        # Parse command name and arguments
        command_name = command.split('[')[0].strip().lower()
        args = []
        
        if '[' in command:
            args_str = command.split('[')[1].split(']')[0]
            # Split on commas not in quotes (handle both single and double quotes)
            args = [arg.strip() for arg in re.split(r',\s*(?![^\'\"]*[\'\"])', args_str)]
        
        if command_name == "starting note":
            if not args:
                raise ValueError("No starting note provided")
            self.root_note = args[0]
            self.root_pitch = self._parse_note(args[0])
            notes.append(args[0])
            return notes
        
        elif command_name == "change root note":
            intervals = self.command_map.get_command_intervals('CHANGE_ROOT')
            for interval in intervals:
                notes.append(self._get_note_by_interval(interval))
            if not args:
                raise ValueError("No new root note provided")
            self.root_note = args[0]
            self.root_pitch = self._parse_note(args[0])
            notes.append(args[0])
            return notes
        
        elif command_name == "declare":
            intervals = self.command_map.get_command_intervals('DECLARE')
            for interval in intervals:
                notes.append(self._get_note_by_interval(interval))
            if not args:
                raise ValueError("No variable provided")
            notes.append(args[0])
            
            if len(args) < 2:
                raise ValueError("No type provided")
            
            # Get type interval from JSON
            var_type = args[1].lower()
            type_config = self.command_map.config['type_declarations'].get(var_type)
            if type_config:
                type_interval_name = type_config['type_interval']
                type_intervals = self.command_map._expand_interval_group(type_interval_name)
                notes.append(self._get_note_by_interval(type_intervals[0]))
            return notes
        
        # Commands that take a variable and an expression
        elif command_name == "let":
            intervals = self.command_map.get_command_intervals('LET')
            for interval in intervals:
                notes.append(self._get_note_by_interval(interval))
            if not args:
                raise ValueError("No variable provided")
            notes.append(args[0])
            if len(args) < 2:
                raise ValueError("No expression provided")
            notes.extend(self._parse_expression(args[1]))
            return notes
        
        # Commands that take only an expression
        elif command_name in ["print", "while", "if"]:
            cmd_map = {"print": "PRINT", "while": "WHILE", "if": "IF"}
            intervals = self.command_map.get_command_intervals(cmd_map[command_name])
            for interval in intervals:
                include_octave = command_name != "print"
                notes.append(self._get_note_by_interval(interval, include_octave=include_octave))
            if not args:
                raise ValueError("No expression provided")
            notes.extend(self._parse_expression(args[0]))
            return notes
        
        # Commands with no arguments
        elif command_name in ["end while", "else", "end if"]:
            cmd_map = {"end while": "END_WHILE", "else": "ELSE", "end if": "END_IF"}
            intervals = self.command_map.get_command_intervals(cmd_map[command_name])
            for interval in intervals:
                notes.append(self._get_note_by_interval(interval))
            return notes
        
        else:
            raise ValueError(f"Unknown command: {command_name}")
    
    def _parse_expression(self, expr: str) -> List[str]:
        """Parse an expression and return note suggestions"""
        notes = []
        
        # Don't replace quotes, just handle both
        # Don't split on whitespace - handle the whole expression as-is
        expr = expr.strip()
        
        # Character literal (single character in quotes)
        if (expr.startswith("'") and expr.endswith("'")) or \
           (expr.startswith('"') and expr.endswith('"')):
            if len(expr) != 3:
                raise ValueError(f"Character can only have one symbol, got: {expr}")
            
            char_code = ord(expr[1])
            # Get char expression pattern from JSON
            char_pattern = self.command_map.get_expression_pattern('char')
            for interval_name in char_pattern:
                intervals = self.command_map._expand_interval_group(interval_name)
                notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
            # Digits for ASCII value - no octave
            notes.extend(self._get_intervals_for_int(char_code))
            return notes
        
        # For complex expressions, split on whitespace
        pieces = expr.split()
        
        for piece in pieces:
            # Strip parentheses from piece for pattern matching
            stripped_piece = piece.strip('()')
            leading_parens = len(piece) - len(piece.lstrip('('))
            trailing_parens = len(piece) - len(piece.rstrip(')'))
            
            # Add leading parentheses
            for _ in range(leading_parens):
                paren_pattern = self.command_map.get_expression_pattern('opening_paren')
                for interval_name in paren_pattern:
                    intervals = self.command_map._expand_interval_group(interval_name)
                    notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
            
            # Character literal
            if (stripped_piece.startswith("'") and stripped_piece.endswith("'")) or \
               (stripped_piece.startswith('"') and stripped_piece.endswith('"')):
                if len(stripped_piece) != 3:
                    raise ValueError("Character can only have one symbol")
                
                char_code = ord(stripped_piece[1])
                # Get char expression pattern from JSON
                char_pattern = self.command_map.get_expression_pattern('char')
                for interval_name in char_pattern:
                    intervals = self.command_map._expand_interval_group(interval_name)
                    notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
                # Digits for ASCII value - no octave
                notes.extend(self._get_intervals_for_int(char_code))
            
            # Variable (note name like E3, C4, etc.) - INCLUDES octave
            elif re.match(r'^[A-G][#&]?\d+$', stripped_piece, re.IGNORECASE):
                # Get variable expression pattern from JSON
                var_pattern = self.command_map.get_expression_pattern('variable')
                for interval_name in var_pattern:
                    intervals = self.command_map._expand_interval_group(interval_name)
                    notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
                # Variable note - INCLUDES octave
                notes.append(stripped_piece)
            
            # Positive integer
            elif re.match(r'^\d+$', stripped_piece):
                # Get positive_int expression pattern from JSON
                int_pattern = self.command_map.get_expression_pattern('positive_int')
                for interval_name in int_pattern:
                    intervals = self.command_map._expand_interval_group(interval_name)
                    notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
                # Digits - no octave
                notes.extend(self._get_intervals_for_int(int(stripped_piece)))
            
            # Negative integer
            elif re.match(r'^-\d+$', stripped_piece):
                # Get negative_int expression pattern from JSON
                neg_int_pattern = self.command_map.get_expression_pattern('negative_int')
                for interval_name in neg_int_pattern:
                    intervals = self.command_map._expand_interval_group(interval_name)
                    notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
                # Digits (absolute value) - no octave
                notes.extend(self._get_intervals_for_int(int(stripped_piece)))
            
            # Arithmetic operators - get from JSON
            elif stripped_piece in ['+', '-', '*', '/']:
                arithmetic_map = {'+': 'plus', '-': 'minus', '*': 'multiply', '/': 'divide'}
                op_name = arithmetic_map[stripped_piece]
                op_config = self.command_map.config['operators']['arithmetic'].get(op_name)
                if op_config:
                    pattern = op_config['pattern']
                    for interval_name in pattern:
                        intervals = self.command_map._expand_interval_group(interval_name)
                        notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
            
            # Comparison operators - get from JSON
            elif stripped_piece in ['>', '<', '==']:
                comparison_map = {'>': 'greater_than', '<': 'less_than', '==': 'equal'}
                op_name = comparison_map[stripped_piece]
                op_config = self.command_map.config['operators']['comparison'].get(op_name)
                if op_config:
                    pattern = op_config['pattern']
                    for interval_name in pattern:
                        intervals = self.command_map._expand_interval_group(interval_name)
                        notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
            
            # Add trailing parentheses
            for _ in range(trailing_parens):
                paren_pattern = self.command_map.get_expression_pattern('closing_paren')
                for interval_name in paren_pattern:
                    intervals = self.command_map._expand_interval_group(interval_name)
                    notes.append(self._get_note_by_interval(intervals[0], include_octave=False))
        
        return notes
    
    def convert_to_midi(self, commands: List[str], output_file: str):
        """
        Convert a list of pseudocode commands to a MIDI file.
        
        All intervals are calculated from the current root note.
        The root only changes with CHANGE_ROOT commands.
        Each note is duplicated in the MIDI file (Velato convention).
        
        Args:
            commands: List of pseudocode command strings
            output_file: Path to output MIDI file
        """        
        midi = MidiFile()
        track = MidiTrack()
        midi.tracks.append(track)
        
        # Track the current root note (can be sounded in any octave)
        current_root = self.root_pitch
        
        # Process each command and generate notes
        for command in commands:
            note_suggestions = self.suggest_notes(command)
            
            # Convert each suggested note to MIDI
            for note_str in note_suggestions:
                # Skip operator placeholders
                if note_str.startswith('['):
                    continue
                    
                pitch = self._get_pitch_from_root(note_str, current_root)
                
                # Add note once (each note_on event is read by interpreter)
                track.append(Message('note_on', note=pitch, velocity=64, time=0))
                track.append(Message('note_off', note=pitch, velocity=64, time=480))
                
                # Check if this is a CHANGE_ROOT command by looking at the command
                if 'change' in command.lower() and 'root' in command.lower():
                    # Update root to this note
                    current_root = pitch
        
        midi.save(output_file)
    
    def _get_pitch_from_root(self, note_str: str, root_pitch: int) -> int:
        """
        Get MIDI pitch for a note calculated from the root.
        
        If note has octave (e.g., E3 - a variable), use it directly.
        Otherwise, calculate interval from root and place in nearby octave.
        
        Args:
            note_str: Note name (e.g., 'C#', 'E3', 'G&')
            root_pitch: Current root note MIDI pitch
            
        Returns:
            MIDI pitch number (0-127)
        """
        # If note already has an octave (variable reference), use it directly
        if any(c.isdigit() for c in note_str):
            return self._parse_note(note_str)
        
        # Note without octave - calculate interval from root
        # Get the note class (C, C#, D, etc.)
        note_name = note_str
        if '&' in note_name:
            # Convert flat to sharp
            base_note = note_name[0]
            note_name = NOTE_NAMES[(NOTE_NAMES.index(base_note) - 1) % 12]
        
        # Find the note class in our 12-tone system
        try:
            note_class = NOTE_NAMES.index(note_name)
        except ValueError:
            raise ValueError(f"Invalid note: {note_str}")
        
        # Calculate interval from root (0-11)
        root_class = root_pitch % 12
        interval = (note_class - root_class) % 12
        
        # Place the note in an octave near the root to keep reasonable range
        # Start with the root's octave
        root_octave = root_pitch // 12
        candidate_pitch = root_octave * 12 + note_class
        
        # If the interval suggests going up from root, ensure we go up
        if interval > 0:
            # If candidate is below root, move up an octave
            if candidate_pitch < root_pitch:
                candidate_pitch += 12
        
        # Keep in valid MIDI range
        if candidate_pitch > 127:
            candidate_pitch -= 12
        if candidate_pitch < 0:
            candidate_pitch += 12
            
        return candidate_pitch


def main():
    """Interactive tool for suggesting Velato notes"""
    import sys
    
    if len(sys.argv) > 1:
        # Process command from arguments
        converter = VelatoNoteSuggestionTool()
        command = ' '.join(sys.argv[1:])
        try:
            notes = converter.suggest_notes(command)
            print(f"Command: {command}")
            print(f"Notes: {' -> '.join(notes)}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Interactive mode
        print("Velato Note Suggester")
        print("=" * 50)
        print("Examples:")
        print("  Starting Note [C4]")
        print("  Declare [E3, int]")
        print("  Let [E3, 99]")
        print("  Print ['H']")
        print("  Print [E3]")
        print("  While [E3 > 0]")
        print("  End While")
        print("\nEnter 'quit' to exit\n")
        
        converter = VelatoNoteSuggestionTool()
        
        while True:
            try:
                command = input("Command: ").strip()
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                if not command:
                    continue
                
                notes = converter.suggest_notes(command)
                print(f"Notes: {' -> '.join(notes)}\n")
            except Exception as e:
                print(f"Error: {e}\n")


if __name__ == '__main__':
    main()
