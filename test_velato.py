#!/usr/bin/env python3
"""
Tests for the Velato Interpreter
"""

import unittest
import os
import shutil
from velato import VelatoInterpreter
from velato_converter import VelatoConverter


class TestVelatoInterpreter(unittest.TestCase):
    """Test cases for the Velato interpreter."""
    
    @classmethod
    def setUpClass(cls):
        """Create test_output directory before running tests."""
        cls.test_output_dir = 'test_output'
        os.makedirs(cls.test_output_dir, exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test_output directory after all tests."""
        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)

    def test_print_hi(self):
        """Test that Programs_hi.mid outputs 'Hi'"""
        interpreter = VelatoInterpreter(verbose=False)
        interpreter.parse_midi('Programs/Programs_hi.mid')
        output = interpreter.run()
        self.assertEqual(output, 'Hi')

    def test_print_hello_world(self):
        """Test that Programs_print_hello_world.mid outputs 'Hello, World!'"""
        interpreter = VelatoInterpreter(verbose=False)
        interpreter.parse_midi('Programs/Programs_print_hello_world.mid')
        output = interpreter.run()
        self.assertEqual(output, 'Hello, World!')

    def test_while_countdown(self):
        """Test that Programs_while_test.mid outputs countdown from 99 to 1"""
        interpreter = VelatoInterpreter(verbose=False)
        interpreter.parse_midi('Programs/Programs_while_test.mid')
        output = interpreter.run()
        # Should print integers from 99 down to 1
        expected = ''.join(str(i) for i in range(99, 0, -1))
        self.assertEqual(output, expected)

    def test_converter_hello_world(self):
        """Test that converter generates working hello world program"""

        commands = [
            'Starting Note [A4]',
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
        
        # Generate MIDI file
        converter = VelatoConverter()
        output_file = os.path.join(self.test_output_dir, 'test_hello_world_generated.mid')
        
        try:
            converter.convert_to_midi(commands, output_file)
            
            # Run the generated MIDI file
            interpreter = VelatoInterpreter(verbose=False)
            interpreter.parse_midi(output_file)
            output = interpreter.run()
            
            # Verify output
            self.assertEqual(output, 'Hello, World!')
        finally:
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_if_statement(self):
        """Test that IF/ELSE statements work correctly"""
        
        commands = [
            'Starting Note [A4]',
            'Declare [E3, int]',
            'Let [E3, 5]',
            'If [(E3 > 0)]',
            'Print ["Y"]',
            'Else',
            'Print ["N"]',
            'End If'
        ]
        
        # Generate MIDI file
        converter = VelatoConverter()
        output_file = os.path.join(self.test_output_dir, 'test_if_generated.mid')
        
        try:
            converter.convert_to_midi(commands, output_file)
            
            # Run the generated MIDI file
            interpreter = VelatoInterpreter(verbose=False)
            interpreter.parse_midi(output_file)
            output = interpreter.run()
            
            # Verify output - should print 'Y' since 5 > 0 is true
            self.assertEqual(output, 'Y')
        finally:
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_nested_if_statements(self):
        """Test nested IF/ELSE statements"""

        commands = [
            'Starting Note [A4]',
            'Declare [E3, int]',
            'Declare [F3, int]',
            'Let [E3, 10]',
            'Let [F3, 5]',
            'If [(E3 > 0)]',
            'If [(F3 > 0)]',
            'Print ["H"]',
            'Else',
            'Print ["!"]',
            'End If',
            'Else',
            'Print ["!"]',
            'End If'
        ]
        
        # Generate MIDI file
        converter = VelatoConverter()
        output_file = os.path.join(self.test_output_dir, 'test_nested_if_generated.mid')
        
        try:
            converter.convert_to_midi(commands, output_file)
            
            # Run the generated MIDI file
            interpreter = VelatoInterpreter(verbose=False)
            interpreter.parse_midi(output_file)
            output = interpreter.run()
            
            # Verify output - should print 'H' since both 10 > 0 and 5 > 0 are true
            self.assertEqual(output, 'H')
        finally:
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_if_mapping(self):
        """Test that nested IF statements work correctly"""
        # This tests that the interpreter can handle IF commands with proper nesting
        interpreter = VelatoInterpreter(verbose=False)
        
        # Test IF command identification
        if_pattern = interpreter.identify_command([4, 7])
        self.assertEqual(if_pattern, 'IF')
        
        # Test END_IF command identification
        end_if_pattern = interpreter.identify_command([4, 11])
        self.assertEqual(end_if_pattern, 'END_IF')
        
        # Test ELSE command identification
        else_pattern = interpreter.identify_command([4, 9])
        self.assertEqual(else_pattern, 'ELSE')


