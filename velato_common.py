#!/usr/bin/env python3
"""
Common utilities shared between Velato interpreter and converter
"""

import json
import os
from enum import IntEnum, Enum
from dataclasses import dataclass
from typing import Any, List, Dict, Optional


# Note mapping (MIDI note numbers to note names)
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi_to_note_name(midi_note: int) -> str:
    """Convert MIDI note number to note name with octave."""
    octave = (midi_note // 12) - 1
    note = NOTE_NAMES[midi_note % 12]
    return f"{note}{octave}"


def note_name_to_midi(note_name: str) -> int:
    """Convert note name with octave to MIDI note number."""
    # Handle flats by converting to sharps
    note_name = note_name.replace('D&', 'C#').replace('E&', 'D#').replace('G&', 'F#') \
                        .replace('A&', 'G#').replace('B&', 'A#')

    # Extract note and octave
    if len(note_name) >= 2 and note_name[-2] == '#':
        note = note_name[:-1]
        octave = int(note_name[-1])
    else:
        note = note_name[:-1]
        octave = int(note_name[-1])

    # Find note in NOTE_NAMES
    try:
        note_index = NOTE_NAMES.index(note)
    except ValueError:
        raise ValueError(f"Invalid note: {note}")

    return (octave + 1) * 12 + note_index


def interval_semitones(note1: int, note2: int) -> 'Interval':
    """Calculate the interval in semitones from note1 to note2 (ignoring octave for commands)."""
    from velato_common import Interval
    return Interval((note2 - note1) % 12)


# Velato digit encoding/decoding mappings
# Digit to interval: 0-5 -> 1-6, skip 7th half step from root (reserved), 7-9 -> 9-11
DIGIT_TO_INTERVAL = {
    # Change for 6, minor sixth
    # Begin minor sixth change
    0: 'MINOR_SECOND',      # 1
    1: 'MAJOR_SECOND',      # 2
    2: 'MINOR_THIRD',       # 3
    3: 'MAJOR_THIRD',       # 4
    4: 'PERFECT_FOURTH',    # 5
    5: 'DIMINISHED_FIFTH',  # 6
    6: 'MINOR_SIXTH',       # 8
    7: 'MAJOR_SIXTH',       # 9
    8: 'MINOR_SEVENTH',     # 10
    9: 'MAJOR_SEVENTH',     #11
    # End minor sixth change
}

# Interval to digit: reverse mapping for decoding
INTERVAL_TO_DIGIT = {
    # Change for 6, minor sixth
    # Begin minor sixth change
    1: 0,   # MINOR_SECOND  1 x 1/2 step
    2: 1,   # MAJOR_SECOND  2 x 1/2 steps
    3: 2,   # MINOR_THIRD   3 x 1/2 steps
    4: 3,   # MAJOR_THIRD   4 X 1/2 steps
    5: 4,   # PERFECT_FOURTH  5 x 1/2 steps
    6: 5,   # DIMINISHED_FIFTH  6 x 1/2 steps

    8: 6,    # MINOR_SIXTH   8 x 1/2 steps

    9: 7,   # MAJOR_SIXTH    9 x 1/2 steps
    10: 8,  # MINOR_SEVENTH  10 x 1/2 steps
    11: 9,  # MAJOR_SEVENTH    11 x 1/2 steps
    # End minor sixth change
}

def interval_name(semitones: int) -> str:
    """Get the interval name from semitones."""
    intervals = {
        0: 'Root',
        1: 'Minor 2nd',
        2: 'Major 2nd',
        3: 'Minor 3rd',
        4: 'Major 3rd',
        5: 'Perfect 4th',
        6: 'Diminished 5th',
        7: 'Perfect 5th',
        8: 'Minor 6th',
        9: 'Major 6th',
        10: 'Minor 7th',
        11: 'Major 7th'
    }
    return intervals.get(semitones, 'Unknown')


class Interval(IntEnum):
    """Musical intervals from root note"""
    UNISON = 0
    MINOR_SECOND = 1
    MAJOR_SECOND = 2
    MINOR_THIRD = 3
    MAJOR_THIRD = 4
    PERFECT_FOURTH = 5
    DIMINISHED_FIFTH = 6
    PERFECT_FIFTH = 7
    MINOR_SIXTH = 8
    MAJOR_SIXTH = 9
    MINOR_SEVENTH = 10
    MAJOR_SEVENTH = 11
    OCTAVE = 12


class VarType(Enum):
    """Variable types in Velato."""
    INT = 1
    CHAR = 2
    DOUBLE = 3
    STRING = 4


@dataclass
class Variable:
    """A variable in Velato."""
    name: str  # Note name with octave
    type: 'VarType'
    value: Any


@dataclass
class ExpressionToken:
    """An expression token with type information."""
    value: Any  # The actual value (int, float, string, or variable name)
    expr_type: 'VarType'  # The type of this expression
    is_variable: bool = False  # True if this is a variable reference, not a literal


class VelatoCommandMap:
    """Manages command and expression patterns from velato_commands.json"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to velato_commands.json in the same directory as this file
            config_path = os.path.join(os.path.dirname(__file__), 'velato_commands.json')
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Build lookup tables
        self._command_patterns = {}
        self._build_command_patterns()
    
    def _build_command_patterns(self):
        """Build a lookup table from interval patterns to command names"""
        for command_name, command_info in self.config['commands'].items():
            interval_names = command_info['intervals']
            # Convert interval names to Interval enum values
            interval_pattern = tuple(Interval[name] for name in interval_names)
            self._command_patterns[interval_pattern] = command_name
    
    def identify_command(self, intervals: List[Interval]) -> Optional[str]:
        """Identify a command from its interval pattern"""
        return self._command_patterns.get(tuple(intervals))
    
    def get_command_intervals(self, command_name: str) -> List[Interval]:
        """Get the interval pattern for a command"""
        if command_name not in self.config['commands']:
            raise ValueError(f"Unknown command: {command_name}")
        
        interval_names = self.config['commands'][command_name]['intervals']
        return [Interval[name] for name in interval_names]
    
    def get_digit_for_interval(self, interval: Interval) -> Optional[int]:
        """Get the digit value for an interval, or None if it's a terminator"""
        digit_encoding = self.config['digit_encoding']
        interval_name = interval.name
        
        if interval_name in digit_encoding:
            value = digit_encoding[interval_name]
            return None if value == "terminator" else value
        
        return None
    
    def _expand_interval_group(self, group_name: str) -> List[Interval]:
        """Expand an interval group name to actual Interval values"""
        if group_name in self.config.get('interval_groups', {}):
            return [Interval[name] for name in self.config['interval_groups'][group_name]]
        else:
            # It's a single interval name
            return [Interval[group_name]]
    
    def _matches_pattern(self, intervals: List[Interval], pattern: List[str]) -> bool:
        """Check if a sequence of intervals matches a pattern (with group support)"""
        if len(intervals) != len(pattern):
            return False
        
        for interval, pattern_item in zip(intervals, pattern):
            allowed_intervals = self._expand_interval_group(pattern_item)
            if interval not in allowed_intervals:
                return False
        
        return True
    
    def identify_comparison_operator(self, intervals: List[Interval]) -> Optional[str]:
        """Identify a comparison operator from interval pattern"""
        for op_name, op_info in self.config['operators']['comparison'].items():
            pattern = op_info['pattern']
            if self._matches_pattern(intervals, pattern):
                return op_info['symbol']
        return None
    
    def identify_arithmetic_operator(self, intervals: List[Interval]) -> Optional[str]:
        """Identify an arithmetic operator from interval pattern"""
        for op_name, op_info in self.config['operators']['arithmetic'].items():
            pattern = op_info['pattern']
            if self._matches_pattern(intervals, pattern):
                return op_info['symbol']
        return None
    
    def is_comparison_start(self, interval: Interval) -> bool:
        """Check if an interval could start a comparison operator"""
        for op_info in self.config['operators']['comparison'].values():
            first_pattern = op_info['pattern'][0]
            allowed = self._expand_interval_group(first_pattern)
            if interval in allowed:
                return True
        return False
    
    def is_arithmetic_start(self, interval: Interval) -> bool:
        """Check if an interval could start an arithmetic operator"""
        for op_info in self.config['operators']['arithmetic'].values():
            first_pattern = op_info['pattern'][0]
            allowed = self._expand_interval_group(first_pattern)
            if interval in allowed:
                return True
        return False
    
    def identify_expression_type(self, intervals: List[Interval]) -> Optional[str]:
        """Identify expression type from interval pattern.
        Returns: expression type name (e.g., 'variable', 'positive_int', 'opening_paren')
        """
        for expr_name, expr_info in self.config['expressions'].items():
            pattern = expr_info['pattern']
            if self._matches_pattern(intervals, pattern):
                return expr_name
        return None
    
    def get_expression_pattern(self, expr_type: str) -> List[str]:
        """Get the pattern for an expression type"""
        if expr_type not in self.config['expressions']:
            raise ValueError(f"Unknown expression type: {expr_type}")
        return self.config['expressions'][expr_type]['pattern']
    
    def get_expression_info(self, expr_type: str) -> dict:
        """Get the full info dict for an expression type"""
        if expr_type not in self.config['expressions']:
            raise ValueError(f"Unknown expression type: {expr_type}")
        return self.config['expressions'][expr_type]
    
    def get_comparison_pattern_length(self) -> int:
        """Get the pattern length for comparison operators (they all have the same length)"""
        first_op = next(iter(self.config['operators']['comparison'].values()))
        return len(first_op['pattern'])
    
    def get_arithmetic_pattern_length(self) -> int:
        """Get the pattern length for arithmetic operators (they all have the same length)"""
        first_op = next(iter(self.config['operators']['arithmetic'].values()))
        return len(first_op['pattern'])
    
    def get_type_from_interval(self, interval: Interval) -> Optional[VarType]:
        """Get VarType from a type declaration interval"""
        for type_name, type_info in self.config['type_declarations'].items():
            type_interval_pattern = type_info['type_interval']
            allowed_intervals = self._expand_interval_group(type_interval_pattern)
            if interval in allowed_intervals:
                # Map type name to VarType
                type_map = {
                    'int': VarType.INT,
                    'char': VarType.CHAR,
                    'double': VarType.DOUBLE
                }
                return type_map.get(type_name)
        return None
    
    def get_command_pattern_length(self, command_name: str) -> int:
        """Get the number of intervals in a command pattern"""
        if command_name not in self.config['commands']:
            return 0
        return len(self.config['commands'][command_name]['intervals'])


# Global instance for easy access
_command_map = None

def get_command_map() -> VelatoCommandMap:
    """Get the global VelatoCommandMap instance"""
    global _command_map
    if _command_map is None:
        _command_map = VelatoCommandMap()
    return _command_map