import pyaudio
import wave
import cv2
import numpy as np
import pyautogui
import threading
import time
from moviepy.editor import VideoFileClip, AudioFileClip

def record_audio(filename, duration, rate=44100, chunk=1024, channels=2):
    p = pyaudio.PyAudio()
    
    # Assume the BlackHole device is the recording device
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if 'BlackHole' in dev['name']:
            device_index = i
            break

    if device_index is None:
        raise RuntimeError("BlackHole device not found. Ensure it is set up correctly.")

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device_index)

    frames = []

    for _ in range(int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def screen_record(file_name, dur, fps):
    screen_size = pyautogui.size()
    # Use dimensions from the screenshot
    img = pyautogui.screenshot()  # Capture an initial screenshot
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    fps = 1  # Adjust this value according to desired playback rate
    screen_size = (frame.shape[1], frame.shape[0])  # (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")  # Trying a different codec
    out = cv2.VideoWriter(file_name, fourcc, fps, screen_size)
    print(f"Recording started...\nResolution set to: {screen_size} at {fps} FPS")


    print("Recording Started...\n")

    try:
        frame_count = 0
        total_time = 0
        while True:
            start_time = time.time()  # Track time to match the intended FPS
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            print(f'frame.shape is {frame.shape}')
            if frame.shape[1] != screen_size[0] or frame.shape[0] != screen_size[1]:
                print("Resolution mismatch!")
                print(f'screen_size[0] is {screen_size[0]}, frame.shape[0] is {frame.shape[0]}, screen_size[1] is {screen_size[1]}')

            ret = out.write(frame)
            print(f'ret is {ret}')

            # Ensure the loop waits approximately (1/fps) seconds per iteration
            cap_dur = (time.time() - start_time)
            print(f'cap dur is {cap_dur}')
            print(f'except playback dur is {float(1) / fps}')
            if cap_dur < float(1) / fps:
                print(f'time for sleep {1/fps-cap_dur}')
                time.sleep(1/fps)  # Fine-tune sleep for precise sync

            #cv2.imshow("Recording...", frame)
            frame_count = frame_count + 1
            total_time = total_time + 1/fps
            if total_time >= dur:
                break
    finally:
        out.release()
        cv2.destroyAllWindows()

def record_both(audio_filename, video_filename, fps, duration):
    audio_thread = threading.Thread(target=record_audio, args=(audio_filename, duration))
    video_thread = threading.Thread(target=screen_record, args=(video_filename, duration, fps))

    audio_thread.start()
    video_thread.start()

    audio_thread.join()
    video_thread.join()

# Example
audio_file = "system_audio1.wav"
video_file = "screen_video1.avi"
av_file = "video_with_audio_1.avi"
record_both(audio_file, video_file, 1, 20)  # Record for 20 seconds
# Load the video file
video_clip = VideoFileClip(video_file)
# Load the audio file
audio_clip = AudioFileClip(audio_file)
# Set the audio of the video clip
video_with_audio = video_clip.set_audio(audio_clip)
# Write the output to a new AVI file
video_with_audio.write_videofile(av_file, codec='libx264', audio_codec='aac')

# Free resources
video_clip.close()
audio_clip.close()
video_with_audio.close()
