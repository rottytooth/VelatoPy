#!/usr/bin/env python3
"""
Velato Interpreter
==================
An interpreter for the Velato programming language.
Velato uses MIDI files as source code - the pattern of notes determines commands.

WARNING: This is mostly vibe-coded; the definitive implementation is still the original C# compiler.
"""

import sys
from typing import List, Tuple, Optional, Dict, Any, Union

from velato_common import (
    VarType, Variable, ExpressionToken, Interval,
    midi_to_note_name, note_name_to_midi,
    interval_semitones, interval_name,
    get_command_map, INTERVAL_TO_DIGIT
)

try:
    import mido
except ImportError:
    print("Error: mido library is required. Install with: pip install mido")
    sys.exit(1)


class VelatoInterpreter:
    """Interpreter for the Velato programming language."""
    
    def __init__(self, verbose: bool = False, max_iterations: int = 10000):
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.notes: List[int] = []
        self.position = 0
        self.command_root = None
        self.last_command = None
        self.variables: Dict[str, Variable] = {}
        self.output_buffer = []
        self.command_map = get_command_map()
        
    def parse_midi(self, filename: str):
        """Parse a MIDI file and extract the note sequence."""
        mid = mido.MidiFile(filename)
        
        # Extract all note_on events from the first track
        notes = []
        for i, track in enumerate(mid.tracks):
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append(msg.note)
        
        if not notes:
            raise ValueError("No notes found in MIDI file")
        
        self.notes = notes
        self.command_root = notes[0]

    def current_note(self) -> Optional[int]:
        """Get the current note without advancing."""
        if self.position < len(self.notes):
            return self.notes[self.position]
        return None

    def peek_note(self, offset: int = 1) -> Optional[int]:
        """Peek at a note ahead without advancing."""
        pos = self.position + offset
        if pos < len(self.notes):
            return self.notes[pos]
        return None
    
    def advance(self) -> Optional[int]:
        """Get the current note and advance position."""
        note = self.current_note()
        if note is not None:
            self.position += 1
        return note
    
    def match_command(self) -> Optional[Tuple[str, List[int]]]:
        """Match the current position to a command pattern."""
        if self.current_note() is None:
            return None
        
        # Check if this starts a command by looking at the interval from command root
        start_note = self.current_note()
        start_interval = interval_semitones(self.command_root, start_note)
        
        # Unison (same as root) can be a command start OR just a placeholder
        # Try to match as a command first
        if start_interval == Interval.UNISON:
            # Could be start of a new command with explicit root, or just a placeholder
            # Advance and check next interval
            saved_position = self.position
            self.advance()
            if self.current_note() is None:
                return None
            
            command_notes = [start_note]
            intervals = []
            
            # Read notes and calculate intervals
            while self.current_note() is not None:
                note = self.advance()
                command_notes.append(note)
                interval = interval_semitones(self.command_root, note)
                intervals.append(interval)
                
                # Try to match known command patterns
                command = self.identify_command(intervals)
                if command:
                    return (command, command_notes)
                
                # Stop if we hit the command root again
                if interval == 0 and len(intervals) > 1:
                    break
            
            # If no command matched, this was just a placeholder root note
            # Reset position to after the root note and return None
            self.position = saved_position + 1
            return None
        
        # Not starting with root - try to match command directly from current position
        command_notes = []
        intervals = []
        
        # Read notes and calculate intervals until we can identify a command
        while self.current_note() is not None:
            note = self.advance()
            command_notes.append(note)
            interval = interval_semitones(self.command_root, note)
            intervals.append(interval)
            
            # Try to match known command patterns
            command = self.identify_command(intervals)
            if command:
                return (command, command_notes)
            
            # Stop if we've read too many notes without matching
            if len(intervals) > 4:
                # Put notes back and return None
                self.position -= len(intervals)
                return None
        
        return None
    
    def identify_command(self, intervals: List[Interval]) -> Optional[str]:
        """Identify a command from its interval pattern."""
        if len(intervals) == 0:
            return None
        
        # Use the command map for identification
        return self.command_map.identify_command(intervals)
    
    def parse_expression(self) -> Any:
        """Parse an expression (variable, literal, or operation) using JSON patterns."""
        if self.current_note() is None:
            return None
        
        note = self.current_note()
        interval = interval_semitones(self.command_root, note)
        
        # Try to match expression patterns by looking ahead
        # We need to peek at the next interval(s) to determine the expression type
        next_note = self.peek_note()
        if next_note is None:
            return None
        
        next_interval = interval_semitones(self.command_root, next_note)
        
        # Try to identify expression type with 2 intervals (most common)
        expr_type = self.command_map.identify_expression_type([interval, next_interval])
        
        # If no match with 2, try with 3 (for parentheses)
        if expr_type is None:
            third_note = self.peek_note(2)
            if third_note:
                third_interval = interval_semitones(self.command_root, third_note)
                expr_type = self.command_map.identify_expression_type([interval, next_interval, third_interval])
        
        # If no expression type matched, return None
        if expr_type is None:
            return None
        
        # Get expression metadata from JSON
        expr_info = self.command_map.get_expression_info(expr_type)
        handler = expr_info.get('handler')
        
        # Handle based on handler type
        if handler == 'paren':
            # Parentheses: consume pattern length
            pattern_length = len(expr_info['pattern'])
            for _ in range(pattern_length):
                self.advance()
            return ExpressionToken(value='(' if expr_type == 'opening_paren' else ')', expr_type=VarType.INT)
        
        elif handler == 'variable':
            # Variable reference: advance twice, then get variable note
            self.advance()  # consume 3rd
            self.advance()  # consume 2nd
            var_note = self.advance()  # get variable note
            if var_note:
                var_name = midi_to_note_name(var_note)
                var_type = VarType.INT
                if var_name in self.variables:
                    var_type = self.variables[var_name].type
                return ExpressionToken(value=var_name, expr_type=var_type, is_variable=True)
            return ExpressionToken(value=0, expr_type=VarType.INT)
        
        if handler == 'integer_literal':
            # Integer literal: advance twice, parse digits, apply type and negation
            self.advance()  # consume first interval (3rd)
            self.advance()  # consume second interval (varies)
            value = self.parse_integer_literal(self.current_note())
            
            # Apply negation if specified
            if expr_info.get('negate', False):
                value = -value
            
            # Get type from JSON
            var_type = VarType[expr_info['type']]
            return ExpressionToken(value=value, expr_type=var_type)
        
        elif handler == 'double_literal':
            # Double literal: advance twice, parse two digit sequences
            self.advance()  # consume 3rd
            self.advance()  # consume 6th or 7th
            int_part = self.parse_integer_literal(self.current_note())
            decimal_part = self.parse_integer_literal(self.current_note())
            value = float(f"{int_part}.{decimal_part}")
            
            # Apply negation if specified
            if expr_info.get('negate', False):
                value = -value
            
            return ExpressionToken(value=value, expr_type=VarType.DOUBLE)
        
        # Unknown handler
        return None
    
    def parse_expression_block(self, implied_opening=False) -> List[Any]:
        """Parse a block of expressions using JSON-based operator identification."""
        expressions = []
        opening_brackets = 1 if implied_opening else 0
        
        # Use do-while pattern: always parse at least one expression
        while True:
            if self.current_note() is None:
                break
            
            note = self.current_note()
            interval = interval_semitones(self.command_root, note)
            
            # Try to parse comparison operators
            if self.command_map.is_comparison_start(interval):
                saved_pos = self.position
                # Collect intervals for comparison pattern
                intervals = [interval]
                self.advance()
                
                # Get pattern length and collect remaining intervals
                pattern_length = self.command_map.get_comparison_pattern_length()
                for _ in range(pattern_length - 1):
                    next_note = self.current_note()
                    if next_note:
                        intervals.append(interval_semitones(self.command_root, next_note))
                        self.advance()
                    else:
                        break
                
                # Try to identify the operator
                operator = self.command_map.identify_comparison_operator(intervals)
                if operator:
                    expressions.append(ExpressionToken(value=operator, expr_type=VarType.INT))
                    continue
                
                # Backtrack if not a comparison operator
                self.position = saved_pos
            
            # Try to parse arithmetic operators
            if self.command_map.is_arithmetic_start(interval):
                saved_pos = self.position
                # Collect intervals for arithmetic pattern
                intervals = [interval]
                self.advance()
                
                # Get pattern length and collect remaining intervals
                pattern_length = self.command_map.get_arithmetic_pattern_length()
                for _ in range(pattern_length - 1):
                    next_note = self.current_note()
                    if next_note:
                        intervals.append(interval_semitones(self.command_root, next_note))
                        self.advance()
                    else:
                        break
                
                # Try to identify the operator
                operator = self.command_map.identify_arithmetic_operator(intervals)
                if operator:
                    expressions.append(ExpressionToken(value=operator, expr_type=VarType.INT))
                    continue
                
                # Backtrack if not an arithmetic operator
                self.position = saved_pos
            
            # Parse value or other expression
            expr = self.parse_expression()
            
            if expr is not None:
                if expr.value == '(':
                    opening_brackets += 1
                    expressions.append(expr)
                elif expr.value == ')':
                    opening_brackets -= 1
                    expressions.append(expr)
                else:
                    expressions.append(expr)
            else:
                # If we can't parse anything, we're done
                break
            
            # Check if we should continue (matching C# do-while logic)
            if opening_brackets <= 0:
                break
        
        return expressions
    
    def evaluate_expression(self, expressions: List[ExpressionToken]) -> Tuple[Any, VarType]:
        """Evaluate a list of expression tokens.
        
        Returns:
            Tuple of (value, type) where type is the resulting expression type.
        """
        if not expressions:
            return 0, VarType.INT
        
        # Helper to get value and type (resolve variables)
        def get_value_and_type(expr_token: ExpressionToken) -> Tuple[Any, VarType]:
            if expr_token.is_variable:
                # It's a variable reference
                var_name = expr_token.value
                if var_name in self.variables:
                    return self.variables[var_name].value, self.variables[var_name].type
                return 0, VarType.INT
            else:
                # It's a literal value
                return expr_token.value, expr_token.expr_type
        
        # Filter out parentheses for now (simple evaluation)
        filtered = [e for e in expressions if e.value not in ['(', ')']]
        
        if not filtered:
            return 0, VarType.INT
        
        if len(filtered) == 1:
            return get_value_and_type(filtered[0])
        
        # Simple left-to-right evaluation
        result, result_type = get_value_and_type(filtered[0])
        i = 1
        
        while i < len(filtered):
            if i + 1 >= len(filtered):
                break
            
            operator = filtered[i].value
            if operator not in ['+', '-', '*', '/', '>', '<', '==']:
                i += 1
                continue
            
            operand, operand_type = get_value_and_type(filtered[i + 1])
            
            # Arithmetic operations preserve type (usually INT)
            if operator == '+':
                result = result + operand
            elif operator == '-':
                result = result - operand
            elif operator == '*':
                result = result * operand
            elif operator == '/':
                result = result / operand if operand != 0 else 0
            # Comparison operations always return INT (boolean)
            elif operator == '>':
                result = 1 if result > operand else 0
                result_type = VarType.INT
            elif operator == '<':
                result = 1 if result < operand else 0
                result_type = VarType.INT
            elif operator == '==':
                result = 1 if result == operand else 0
                result_type = VarType.INT
            
            i += 2
        
        return result, result_type
    
    def parse_type_declaration(self, first_interval: Interval) -> Tuple[VarType, Any]:
        """Parse a type declaration (3rd + 4th) followed by value using JSON configuration."""
        self.advance()
        
        # Get type from JSON based on interval
        var_type = self.command_map.get_type_from_interval(first_interval)
        if var_type is None:
            var_type = VarType.INT  # Default fallback
        
        # Parse the value
        value = self.parse_literal_value(var_type)
        
        return (var_type, value)
    
    def parse_literal_value(self, var_type: VarType) -> Any:
        """Parse a literal value of the specified type."""
        if var_type == VarType.INT or var_type == VarType.CHAR:
            return self.parse_integer_literal(self.current_note())
        elif var_type == VarType.DOUBLE:
            return float(self.parse_integer_literal(self.current_note()))
        else:
            return ""
    
    def parse_integer_literal(self, start_note: Optional[int]) -> int:
        """Parse an integer literal (sequence of digits ending with perfect 5th)."""
        if start_note is None:
            return 0
        
        # Process notes to build the number
        digits = []
        
        while self.current_note() is not None:
            note = self.current_note()
            interval = interval_semitones(self.command_root, note)
            
            # Perfect 5th ends the number
            if interval == Interval.PERFECT_FIFTH:
                self.advance()
                break
            
            # Map interval to digit using common mapping
            digit = INTERVAL_TO_DIGIT.get(interval.value, 0)
            
            digits.append(str(digit))
            self.advance()
        
        if not digits:
            return 0
        
        return int(''.join(digits))
    
    def execute_command(self, command: str, notes: List[int]):
        """Execute a parsed command."""
        if command == 'PRINT':
            # PRINT: Major 6th + Perfect 5th, then expression block
            # Parse the expression to print
            expr_start = self.position
            expr_list = self.parse_expression_block()
            printed_value = None
            
            # Evaluate the expression to get the value and type
            value, expr_type = self.evaluate_expression(expr_list)
            expr_notes = self.notes[expr_start:self.position]
            
            # Print based on the expression type
            if expr_type == VarType.CHAR and isinstance(value, int) and 32 <= value <= 127:
                # CHAR type: print as character
                char = chr(value)
                self.output_buffer.append(char)
            else:
                self.output_buffer.append(str(value))
                printed_value = value
            
            if self.verbose:
                print(f"\nCommand: {command}")
                print(f"  Command notes: {[midi_to_note_name(n) for n in notes]}")
                print(f"  Expression: {[e.value for e in expr_list]}")
                print(f"  Expression type: {expr_type.name}")
                print(f"  Expression notes: {[midi_to_note_name(n) for n in expr_notes]}")
                if not printed_value is None:
                    print(f"  Action: print({printed_value})")
        
        elif command == 'CHANGE_ROOT':
            # Current note (already positioned by match_command) becomes the new command root
            expr_start = self.position
            new_root = self.current_note()
            if new_root is not None:
                self.advance()  # consume the new root note
                expr_notes = self.notes[expr_start:self.position]
                self.command_root = new_root
                if self.verbose:
                    print(f"\nCommand: {command}")
                    print(f"  Command notes: {[midi_to_note_name(n) for n in notes]}")
                    print(f"  Expression: new_root_note({midi_to_note_name(self.command_root)})")
                    print(f"  Expression notes: {[midi_to_note_name(n) for n in expr_notes]}")
                    print(f"  Action: change_root({midi_to_note_name(self.command_root)})")
        
        elif command == 'ASSIGNMENT':
            # Parse: type declaration, then value, then variable name
            note = self.current_note()
            if note is not None:
                interval = interval_semitones(self.command_root, note)
                next_note = self.peek_note()
                
                if next_note is not None:
                    next_interval = interval_semitones(self.command_root, next_note)
                    
                    # Check if this is a type declaration pattern (3rd + 4th)
                    if next_interval == Interval.PERFECT_FOURTH:
                        expr_start = self.position
                        # Get type from JSON based on the first interval (3rd)
                        var_type = self.command_map.get_type_from_interval(interval)
                        if var_type is None:
                            var_type = VarType.INT  # Default fallback
                        
                        self.advance()  # consume 3rd
                        self.advance()  # consume 4th
                        
                        # Parse value
                        value = self.parse_integer_literal(self.current_note())
                        
                        # Parse variable name
                        var_note = self.advance()
                        if var_note is not None:
                            expr_notes = self.notes[expr_start:self.position]
                            var_name = midi_to_note_name(var_note)
                            self.variables[var_name] = Variable(var_name, var_type, value)
                            if self.verbose:
                                print(f"\nCommand: {command}")
                                print(f"  Command notes: {[midi_to_note_name(n) for n in notes]}")
                                print(f"  Expression notes: {[midi_to_note_name(n) for n in expr_notes]}")
                                print(f"  Action: assign {var_name} = {value}")
        
        elif command == 'DECLARE':
            # DECLARE: Minor 6th, then variable note, then type interval
            # match_command already consumed the Minor 6th, we're now at the variable note
            var_note = self.current_note()
            if var_note is not None:
                var_name = midi_to_note_name(var_note)
                self.advance()  # move to type note
                type_note = self.current_note()
                if type_note is not None:
                    self.advance()
                    type_interval = interval_semitones(self.command_root, type_note)
                    
                    # Get type from JSON configuration
                    var_type = self.command_map.get_type_from_interval(type_interval)
                    if var_type is None:
                        var_type = VarType.INT  # Default fallback
                    
                    # Initialize with default value
                    self.variables[var_name] = Variable(var_name, var_type, 0)
                    if self.verbose:
                        print(f"\nCommand: {command}")
                        print(f"  Command notes: {[midi_to_note_name(n) for n in notes]}")
                        print(f"  Action: declare {var_name} {var_type.name}")
        
        elif command == 'LET':
            # LET: Minor 3rd, then variable, then expression
            # match_command already consumed the Minor 3rd, we're now at the variable note
            var_note = self.current_note()
            if var_note is not None:
                var_name = midi_to_note_name(var_note)
                self.advance()  # move past variable note to expression
                
                # Parse the value expression
                expr_start = self.position
                value_exprs = self.parse_expression_block()
                expr_notes = self.notes[expr_start:self.position]
                value, _ = self.evaluate_expression(value_exprs)
                
                # Assign to variable
                if var_name in self.variables:
                    self.variables[var_name].value = value
                else:
                    # Create as INT if not declared
                    self.variables[var_name] = Variable(var_name, VarType.INT, value)
                
                if self.verbose:
                    print(f"\nCommand: {command}")
                    print(f"  Command notes: {[midi_to_note_name(n) for n in notes]}")
                    print(f"  Variable note: {var_name}")
                    # Show raw expression tokens, filtering out parentheses
                    expr_str = ' '.join(str(e.value) if hasattr(e, 'value') else str(e) 
                                       for e in value_exprs if not (hasattr(e, 'value') and e.value in ['(', ')']))
                    print(f"  Expression: {expr_str}")
                    print(f"  Expression notes: {[midi_to_note_name(n) for n in expr_notes]}")
                    print(f"  Action: let {var_name} = {expr_str}")
        
        elif command == 'WHILE':
            # Parse the condition expression (with implied opening bracket)
            condition_exprs = self.parse_expression_block(implied_opening=True)
            
            if self.verbose:
                print(f"  Condition expression: {condition_exprs}")
            
            # Mark start of loop body
            loop_body_start = self.position
            
            # We need to find END_WHILE pattern to mark end of loop
            # But we can't use match_command because it advances position
            loop_end = len(self.notes)  # Default to end of file
            depth = 1
            scan_pos = self.position
            
            while scan_pos < len(self.notes) - 1 and depth > 0:
                interval1 = interval_semitones(self.command_root, self.notes[scan_pos])
                interval2 = interval_semitones(self.command_root, self.notes[scan_pos + 1])
                
                if [interval1, interval2] == self.command_map.get_command_intervals('WHILE'):
                    # add to the stack
                    depth += 1
                    scan_pos += 2
                elif [interval1, interval2] == self.command_map.get_command_intervals('END_WHILE'):
                    # pop from the stack
                    depth -= 1
                    if depth == 0:
                        loop_end = scan_pos
                        break
                    scan_pos += 2
                else:
                    scan_pos += 1
            
            # Restore position to start of loop body (position unchanged from search)
            self.position = loop_body_start
            
            if self.verbose:
                print(f"  Loop body: positions {loop_body_start} to {loop_end}")
                if loop_body_start < len(self.notes):
                    print(f"  First note of loop body: {midi_to_note_name(self.notes[loop_body_start])}")
                if loop_end < len(self.notes):
                    print(f"  Note at loop_end: {midi_to_note_name(self.notes[loop_end])}")
            
            # Execute while loop
            iteration = 0
            saved_command_root = self.command_root  # Save original command root
            
            while iteration < self.max_iterations:
                # Re-evaluate condition each iteration
                condition_value, _ = self.evaluate_expression(condition_exprs)
                
                if self.verbose:
                    # Show variable values for debugging
                    var_values = {k: v.value for k, v in self.variables.items()}
                    print(f"  Iteration {iteration}: condition = {condition_exprs}, vars = {var_values}, result = {condition_value}")
                
                if not condition_value or condition_value == 0:
                    break
                
                # Execute loop body - reset to start and execute commands
                # Also restore command root to its value before the loop
                self.command_root = saved_command_root
                self.position = loop_body_start
                while self.position < loop_end:
                    result = self.match_command()
                    if result:
                        cmd, cmd_notes = result
                        if cmd == 'END_WHILE':
                            break
                        self.execute_command(cmd, cmd_notes)
                    else:
                        self.advance()
                
                iteration += 1
            
            if self.verbose and iteration > 0:
                print(f"\nCommand: WHILE")
                print(f"  Loop executed {iteration} times")
        
        elif command == 'END_WHILE':
            # END_WHILE is handled by the WHILE loop itself
            pass
        
        elif command == 'IF':
            # Parse condition (expression includes explicit parentheses from converter)
            condition_exprs = self.parse_expression_block(implied_opening=False)
            condition_value, _ = self.evaluate_expression(condition_exprs)
            
            if self.verbose:
                print(f"  Condition: {[e.value for e in condition_exprs]}, result = {condition_value}")
            
            # Mark start of IF body
            if_body_start = self.position
            
            # Find ELSE and END_IF positions
            else_pos = None
            end_if_pos = None
            depth = 1
            scan_pos = self.position
            
            # Get command intervals from JSON
            if_intervals = self.command_map.get_command_intervals('IF')
            else_intervals = self.command_map.get_command_intervals('ELSE')
            end_if_intervals = self.command_map.get_command_intervals('END_IF')
            
            while scan_pos < len(self.notes) - 1 and depth > 0:
                interval1 = interval_semitones(self.command_root, self.notes[scan_pos])
                interval2 = interval_semitones(self.command_root, self.notes[scan_pos + 1])
                
                # Check for nested IF
                if [interval1, interval2] == if_intervals:
                    depth += 1
                    scan_pos += 2
                # Check for ELSE at our level
                elif [interval1, interval2] == else_intervals and depth == 1 and else_pos is None:
                    else_pos = scan_pos
                    scan_pos += 2
                # Check for END_IF
                elif [interval1, interval2] == end_if_intervals:
                    depth -= 1
                    if depth == 0:
                        end_if_pos = scan_pos
                        break
                    scan_pos += 2
                else:
                    scan_pos += 1
            
            if end_if_pos is None:
                end_if_pos = len(self.notes)
            
            # Execute appropriate branch
            if condition_value and condition_value != 0:
                # Execute IF body
                self.position = if_body_start
                end_pos = else_pos if else_pos else end_if_pos
                
                while self.position < end_pos:
                    result = self.match_command()
                    if result:
                        cmd, cmd_notes = result
                        if cmd in ['ELSE', 'END_IF']:
                            break
                        self.execute_command(cmd, cmd_notes)
                    else:
                        self.advance()
                
                # Skip to after END_IF
                self.position = end_if_pos + 2 if end_if_pos < len(self.notes) else end_if_pos
            else:
                # Execute ELSE body if it exists, otherwise skip to END_IF
                if else_pos:
                    self.position = else_pos + 2  # Skip past ELSE command
                    
                    while self.position < end_if_pos:
                        result = self.match_command()
                        if result:
                            cmd, cmd_notes = result
                            if cmd == 'END_IF':
                                break
                            self.execute_command(cmd, cmd_notes)
                        else:
                            self.advance()
                
                # Skip to after END_IF
                self.position = end_if_pos + 2 if end_if_pos < len(self.notes) else end_if_pos
        
        elif command in ['ELSE', 'END_IF', 'END_WHILE', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            # These commands should only appear in specific contexts
            raise SyntaxError(f"Unexpected {command} command found outside valid context")
        
        # Store last command for detecting repeated commands
        self.last_command = command
    
    def run(self):
        """Execute the Velato program."""
        self.position = 0
        self.command_root = self.notes[0] if self.notes else None
        
        while self.position < len(self.notes):
            result = self.match_command()
            
            if result:
                command, notes = result
                self.execute_command(command, notes)
            else:
                # Skip this note (it's part of an expression or invalid)
                self.advance()
        
        # Output the result
        return ''.join(self.output_buffer)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Velato Interpreter - Execute MIDI files as code')
    parser.add_argument('midi_file', help='Path to the Velato MIDI file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show note sequence, commands, and expression processing')
    
    args = parser.parse_args()
    
    try:
        interpreter = VelatoInterpreter(verbose=args.verbose)
        
        print(f"Loading MIDI file: {args.midi_file}")
        interpreter.parse_midi(args.midi_file)
        
        if args.verbose:
            print("\nNote sequence:")
            for i, note in enumerate(interpreter.notes):
                print(f"  {i}: {midi_to_note_name(note)} (MIDI {note})")
            print()
        
        print("Executing program...")
        output = interpreter.run()
        
        print("\n--- Output ---")
        print(output)
        
    except FileNotFoundError:
        print(f"Error: File not found: {args.midi_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()