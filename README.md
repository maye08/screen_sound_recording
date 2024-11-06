# screen_sound_recording
python screen and sound recording tool

The python script use record_both(audio_file, video_file, fps, duration) to do screen and sound recording.

- audio_file: Audio file path.
- video_file: Video file path.
- fps: FPS of video, better set start from 1, because some device running python video write quite slowly, which may be the bottle neck of the recorded video's fps.
- duration: Duration of seconds.
