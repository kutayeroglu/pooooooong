"""Script to generate goal scored sound file"""
import wave
import math
import os
import struct

def generate_goal_sound(filename, sample_rate=22050, volume=0.5):
    """Generate a celebratory goal sound (ascending tone sequence)"""
    duration = 0.5  # Longer than other sounds
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        # Create an ascending tone sequence (more celebratory)
        t = i / sample_rate
        
        # Start with a lower frequency and ascend
        if t < 0.2:
            frequency = 300 + (t / 0.2) * 200  # 300 to 500 Hz
        elif t < 0.35:
            frequency = 500 + ((t - 0.2) / 0.15) * 300  # 500 to 800 Hz
        else:
            frequency = 800 + ((t - 0.35) / 0.15) * 200  # 800 to 1000 Hz
        
        # Generate a sine wave with some fade out
        fade = 1.0 - (t / duration) * 0.5  # Fade out in second half
        value = int(32767 * volume * fade * math.sin(2 * math.pi * frequency * t))
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

# Generate goal scored sound
generate_goal_sound(
    os.path.join(assets_dir, 'goal_scored.wav')
)

print("Goal scored sound file generated successfully!")

