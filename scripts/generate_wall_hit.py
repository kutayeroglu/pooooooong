"""Script to generate wall hit sound file"""
import wave
import math
import os
import struct

def generate_tone(filename, frequency, duration, sample_rate=22050, volume=0.3):
    """Generate a simple tone and save as WAV file"""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        # Generate a sine wave
        value = int(32767 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)
    
    # Convert samples to bytes (little-endian 16-bit)
    frames = b''.join([struct.pack('<h', int(s)) for s in samples])
    
    # Write WAV file
    wav_file = wave.open(filename, 'wb')
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(frames)
    wav_file.close()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (pooooooong)
project_dir = os.path.dirname(script_dir)

# Create assets directory if it doesn't exist
assets_dir = os.path.join(project_dir, 'assets')
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)

# Generate wall hit sound (higher pitch, shorter)
generate_tone(
    os.path.join(assets_dir, 'wall_hit.wav'),
    frequency=800,  # Higher pitch
    duration=0.1,   # Short duration
    volume=0.4
)

print("Wall hit sound file generated successfully!")

