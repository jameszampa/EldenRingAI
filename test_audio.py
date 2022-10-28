import pyaudio
import wave
import threading
import time
import subprocess
import os


class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self, device):
        self.open = True
        self.rate = 16000
        self.frames_per_buffer = 16000 * 2
        self.channels = 1
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer = self.frames_per_buffer,
                                      input_device_index=0)
        self.audio_frames = []
        self.active = False


    # Audio starts being recorded
    def record(self):
        # self.audio_frames = []
        self.active = True
        self.stream.start_stream()
        data = self.stream.read(self.frames_per_buffer) 
        self.audio_frames.append(data)
        self.stream.stop_stream()
        self.active = False

    def get_audio(self):
        return self.audio_frames

    def close(self):
        self.stream.close()
        self.audio.terminate()

        waveFile = wave.open(self.audio_filename, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.audio.get_sample_size(self.format))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(self.audio_frames))
        waveFile.close()

    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


def main():
    audio_cap = AudioRecorder('/dev/video0')
    audio_cap.start()
    while len(audio_cap.get_audio()) == 0: pass
    print(audio_cap.get_audio()[0])
    audio_cap.close()



if __name__ == "__main__":
    main()
    import pyaudio
    p = pyaudio.PyAudio()
    for ii in range(p.get_device_count()):
        print(p.get_device_info_by_index(ii).get('name'))