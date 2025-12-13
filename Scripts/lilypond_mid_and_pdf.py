from music21 import stream, note, chord, clef, key, layout
import os

def add_chord_with_order(s_midi, s_pdf, notes, quarterLength=2.0):
    """
    Add a chord to both MIDI and PDF streams.
    
    Args:
        s_midi: Stream for MIDI output (preserves note order)
        s_pdf: Stream for PDF output (displays as chord)
        notes: List of note names in the order they should appear in MIDI (e.g., ['E4', 'C4', 'G4'])
        quarterLength: Duration of the chord in quarter notes
    """
    # For MIDI: insert notes at same offset in the specified order
    current_offset = s_midi.highestTime
    for note_name in notes:
        s_midi.insert(current_offset, note.Note(note_name, quarterLength=quarterLength))
    
    # For PDF: use a proper Chord object
    s_pdf.append(chord.Chord(notes, quarterLength=quarterLength))

# Create separate streams for MIDI and PDF
s_midi = stream.Stream()
s_pdf = stream.Stream()

# Create harmony track
harmony_midi = stream.Stream()
harmony_pdf = stream.Stream()

# Create ambient third track (sleepy, sustained harmonies)
ambient_midi = stream.Stream()
ambient_pdf = stream.Stream()

# HELLO WORLD notes
# Starting Note: A4
for s in [s_midi, s_pdf]:
    s.append(note.Note('A4', quarterLength=1.0))
    # Print ["H"]: F#, E, C, D, F#, C, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["e"]: F#, E, C, D, B, A#, B, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('A#4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["l"]: F#, E, C, D, B, A#, G, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('A#4', quarterLength=1.0))
    s.append(note.Note('G4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["l"]: F#, E, C, D, B, A#, G, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('A#4', quarterLength=1.0))
    s.append(note.Note('G4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["o"]: F#, E, C, D, B, B, B, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print [","]: F#, E, C, D, D, D, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print [" "]: F#, E, C, D, C#, C, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('C#4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["W"]: F#, E, C, D, G, F#, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('G4', quarterLength=1.0))
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["o"]: F#, E, C, D, B, B, B, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["r"]: F#, E, C, D, B, B, D, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["l"]: F#, E, C, D, B, A#, G, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('A#4', quarterLength=1.0))
    s.append(note.Note('G4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["d"]: F#, E, C, D, B, A#, A#, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('B4', quarterLength=1.0))
    s.append(note.Note('A#4', quarterLength=1.0))
    s.append(note.Note('A#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    # Print ["!"]: F#, E, C, D, C#, C#, E
    s.append(note.Note('F#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))
    s.append(note.Note('C4', quarterLength=1.0))
    s.append(note.Note('D4', quarterLength=1.0))
    s.append(note.Note('C#4', quarterLength=1.0))
    s.append(note.Note('C#4', quarterLength=1.0))
    s.append(note.Note('E4', quarterLength=1.0))

# Add harmony track with complementary notes
# Using varied rhythms and contrary motion for interest
for h in [harmony_midi, harmony_pdf]:
    # Measure 1 - Opening
    h.append(note.Note('F3', quarterLength=2.0))
    h.append(note.Note('D3', quarterLength=2.0))
    
    # Measure 2 - "H"
    h.append(note.Note('A3', quarterLength=3.0))
    h.append(note.Note('G3', quarterLength=1.0))
    
    # Measure 3 - "e"
    h.append(note.Note('E3', quarterLength=3.0))
    h.append(note.Note('F#3', quarterLength=1.0))
    
    # Measure 4
    h.append(note.Note('D3', quarterLength=4.0))
    
    # From measure 5 onwards - notes align to measure boundaries
    # Measure 5 - "l" (first)
    h.append(note.Note('G3', quarterLength=4.0))
    
    # Measure 6 - "l" (second)
    h.append(note.Note('E3', quarterLength=2.0))
    h.append(note.Note('A3', quarterLength=2.0))
    
    # Measure 7
    h.append(note.Note('F#3', quarterLength=2.0))
    h.append(note.Note('D3', quarterLength=2.0))
    
    # Measure 8 - "o"
    h.append(note.Note('G3', quarterLength=4.0))
    
    # Measure 9
    h.append(note.Note('E3', quarterLength=4.0))
    
    # Measure 10 - ","
    h.append(note.Note('A3', quarterLength=2.0))
    h.append(note.Note('F#3', quarterLength=2.0))
    
    # Measure 11
    h.append(note.Note('G3', quarterLength=4.0))
    
    # Measure 12 - " " (space)
    h.append(note.Note('A3', quarterLength=4.0))
    
    # Measure 13
    h.append(note.Note('E3', quarterLength=4.0))
    
    # Measure 14 - "W"
    h.append(note.Note('D3', quarterLength=2.0))
    h.append(note.Note('A3', quarterLength=2.0))
    
    # Measure 15
    h.append(note.Note('C3', quarterLength=4.0))
    
    # Measure 16 - "o" (second)
    h.append(note.Note('G3', quarterLength=4.0))
    
    # Measure 17
    h.append(note.Note('E3', quarterLength=4.0))
    
    # Measure 18 - "r"
    h.append(note.Note('A3', quarterLength=2.0))
    h.append(note.Note('D3', quarterLength=2.0))
    
    # Measure 19
    h.append(note.Note('G3', quarterLength=4.0))
    
    # Measure 20 - "l" (third)
    h.append(note.Note('F#3', quarterLength=2.0))
    h.append(note.Note('E3', quarterLength=2.0))
    
    # Measure 21
    h.append(note.Note('D3', quarterLength=4.0))
    
    # Measure 22 - "d"
    h.append(note.Note('G3', quarterLength=4.0))
    
    # Measure 23
    h.append(note.Note('E3', quarterLength=4.0))
    
    # Measure 24 - "!"
    h.append(note.Note('A3', quarterLength=2.0))
    h.append(note.Note('E3', quarterLength=2.0))
    
    # Measure 25 - Final measure
    h.append(note.Note('D3', quarterLength=2.0))
    h.append(note.Note('C#3', quarterLength=1.0))
    h.append(note.Note('A2', quarterLength=1.0))

# Add ambient third track with very long, sustained notes for sleepy atmosphere
# Using whole notes and longer values, mostly fifths and octaves for dreamy quality
for amb in [ambient_midi, ambient_pdf]:
    # Opening - A2 drone (2 measures)
    amb.append(note.Note('A2', quarterLength=8.0))
    
    # "H" and "e" - sustained D3 (3 measures)
    amb.append(note.Note('D3', quarterLength=8.0))
    amb.append(note.Note('D3', quarterLength=4.0))
    
    # "l" "l" - shift to E3 for color (2.5 measures)
    amb.append(note.Note('E3', quarterLength=8.0))
    amb.append(note.Note('E3', quarterLength=2.0))
    
    # "o" - back to A2 for grounding (1.5 measures)
    amb.append(note.Note('A2', quarterLength=2.0))
    amb.append(note.Note('A2', quarterLength=2.0))
    amb.append(note.Note('E2', quarterLength=2.0))
    
    # "," and space - G2 for warmth (2 measures)
    amb.append(note.Note('G2', quarterLength=8.0))
    
    # "W" - lift to C3 (1 measure)
    amb.append(note.Note('C3', quarterLength=4.0))
    
    # "o" "r" - D3 and A3 (3 measures)
    amb.append(note.Note('D3', quarterLength=8.0))
    amb.append(note.Note('D3', quarterLength=4.0))
    
    # "l" - E3 gentle lift (1.75 measures)
    amb.append(note.Note('E3', quarterLength=4.0))
    amb.append(note.Note('B2', quarterLength=2.0))
    
    # "d" - G2 deepening (1.5 measures)
    amb.append(note.Note('G2', quarterLength=4.0))
    amb.append(note.Note('D3', quarterLength=2.0))
    
    # "!" - final A2 resolution (6.25 measures)
    amb.append(note.Note('A2', quarterLength=8.0))
    amb.append(note.Note('D2', quarterLength=8.0))
    amb.append(note.Note('E1', quarterLength=8.0))
    amb.append(note.Note('A2', quarterLength=4.0))

# Combine all three tracks for output
combined_midi = stream.Score()
combined_midi.insert(0, s_midi)
combined_midi.insert(0, harmony_midi)
combined_midi.insert(0, ambient_midi)

combined_pdf = stream.Score()

melody_part = stream.Part()
melody_part.insert(0, key.Key('A'))  # Set key signature to A major
for element in s_pdf:
    melody_part.append(element)
harmony_part = stream.Part()
harmony_part.insert(0, clef.BassClef())  # Use bass clef
harmony_part.insert(0, key.Key('A'))  # Set key signature to A major
for element in harmony_pdf:
    harmony_part.append(element)
ambient_part = stream.Part()
ambient_part.insert(0, clef.BassClef())  # Use bass clef
ambient_part.insert(0, key.Key('A'))  # Set key signature to A major
for element in ambient_pdf:
    ambient_part.append(element)
combined_pdf.insert(0, melody_part)
combined_pdf.insert(0, harmony_part)
combined_pdf.insert(0, ambient_part)

# Create output directory if it doesn't exist
os.makedirs('out', exist_ok=True)

# Generate outputs from combined streams
combined_midi.write('midi', fp='out/output.mid')

# Add metadata to control LilyPond layout
from music21 import metadata
combined_pdf.metadata = metadata.Metadata()
combined_pdf.metadata.title = "Hello, World!"

# Write PDF with LilyPond paper size and spacing settings
# Using a5 (5.83" x 8.27") which is smaller than letter (8.5" x 11")
# Set lineWidth to 90mm to force earlier line breaks and prevent overflow
combined_pdf.write('lily.pdf', fp='out/output', 
                   paperSize='a5',
                   staffSize=16,
                   indent=0,
                   lineWidth=90)  # 90mm line width - much narrower to prevent overflow
try:
    combined_pdf.write('lily.svg', fp='out/output', 
                       paperSize='a5',
                       staffSize=16,
                       indent=0,
                       lineWidth=90)  # Also generate SVG image
except Exception as e:
    # SVG generation may complete but music21 throws error finding it
    # Check if SVG files were actually created
    if os.path.exists('out/output.svg'):
        print("SVG generation successful (output.svg)")
    else:
        print(f"SVG generation failed: {e}")

