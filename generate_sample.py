"""Generate a simple test audio file."""

import numpy as np
import wave

# Parameters
sample_rate = 16000  # 16kHz for Whisper
duration = 3  # 3 seconds
frequency = 440  # A4 note

# Generate sine wave
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * frequency * t)

# Add a second tone
audio_data += 0.5 * np.sin(2 * np.pi * 880 * t)

# Normalize to 16-bit range
audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

# Save as WAV
output_path = "sample.wav"
with wave.open(output_path, 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

print(f"✓ Generated test audio: {output_path}")
print(f"  Duration: {duration}s")
print(f"  Sample rate: {sample_rate} Hz")
print(f"  Format: 16-bit mono WAV")
