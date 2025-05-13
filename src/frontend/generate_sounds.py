# Simple program to generate sound effect WAV files for the Gomoku game
import os
from scipy.io.wavfile import write
import numpy as np

# Create resources directory if it doesn't exist
resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
if not os.path.exists(resources_dir):
    os.makedirs(resources_dir)
    print(f"Created resources directory: {resources_dir}")

# Function to generate a simple tone with fade in/out
def generate_tone(frequency, duration, fade=0.1, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * 2 * np.pi * t) * volume
    
    # Apply fade in/out
    fade_samples = int(fade * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    tone[:fade_samples] *= fade_in
    tone[-fade_samples:] *= fade_out
    
    # Convert to int16 range
    return (tone * 32767).astype(np.int16)

# Generate player move sound - higher pitch click
player_move = generate_tone(800, 0.15, fade=0.05, volume=0.3)
write(os.path.join(resources_dir, "player_move.wav"), 44100, player_move)
print(f"Created sound effect: {os.path.join(resources_dir, 'player_move.wav')}")

# Generate AI move sound - lower pitch click
ai_move = generate_tone(400, 0.2, fade=0.05, volume=0.3)  
write(os.path.join(resources_dir, "ai_move.wav"), 44100, ai_move)
print(f"Created sound effect: {os.path.join(resources_dir, 'ai_move.wav')}")

# Generate win sound - happy ascending tones
t = np.linspace(0, 1.0, 44100, False)
win = np.zeros(44100, dtype=np.float64)
for f in [400, 500, 600, 800, 1000]:
    win += np.sin(f * 2 * np.pi * t) * 0.1
    
# Apply fade in/out
fade_samples = int(0.1 * 44100)
fade_in = np.linspace(0, 1, fade_samples)
fade_out = np.linspace(1, 0, fade_samples)
win[:fade_samples] *= fade_in
win[-fade_samples:] *= fade_out

write(os.path.join(resources_dir, "win.wav"), 44100, (win * 32767).astype(np.int16))
print(f"Created sound effect: {os.path.join(resources_dir, 'win.wav')}")

# Generate lose sound - descending tones
t = np.linspace(0, 1.0, 44100, False)
lose = np.zeros(44100, dtype=np.float64)
for f in [600, 500, 400, 300, 200]:
    lose += np.sin(f * 2 * np.pi * t) * 0.1
    
# Apply fade in/out
lose[:fade_samples] *= fade_in
lose[-fade_samples:] *= fade_out

write(os.path.join(resources_dir, "lose.wav"), 44100, (lose * 32767).astype(np.int16))
print(f"Created sound effect: {os.path.join(resources_dir, 'lose.wav')}")

print("Sound files generated successfully in the resources directory!")
