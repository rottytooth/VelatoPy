from music21 import stream, note, chord
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

# # Add chord with specific MIDI order: E4 first, then C4, then G4
# add_chord_with_order(s_midi, s_pdf, ['E4', 'C4', 'G4'], quarterLength=2.0)

# # Add a rest
# for s in [s_midi, s_pdf]:
#     s.append(note.Rest(quarterLength=1.0))

# Create output directory if it doesn't exist
os.makedirs('out', exist_ok=True)

# Generate outputs from separate streams
s_midi.write('midi', fp='out/output.mid')
s_pdf.write('lily.pdf', fp='out/output')  # Requires LilyPond installed

