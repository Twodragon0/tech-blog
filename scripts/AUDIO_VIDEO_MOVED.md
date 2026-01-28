# Audio/Video Scripts - Moved to online-course

Audio and video generation scripts have been moved to the `online-course` project for centralized media production.

## New Location

```
~/Desktop/online-course/scripts/audio_video/
```

## Quick Access

```bash
# Navigate to audio/video scripts
cd ~/Desktop/online-course/scripts/audio_video/

# Generate video from tech-blog post
python3 generate_post_to_video.py ~/Desktop/tech-blog/_posts/2026-01-15-Example.md

# Generate audio from tech-blog post
python3 generate_tts_simple.py ~/Desktop/tech-blog/_posts/2026-01-15-Example.md
```

## Moved Scripts (14 scripts)

| Script | Purpose |
|--------|---------|
| `generate_audio_batch.py` | Batch audio generation |
| `generate_audio_from_script.py` | Single script audio |
| `generate_audio_from_improved_scripts.py` | Audio from improved scripts |
| `generate_audio_from_improved_split.py` | Split audio generation |
| `generate_enhanced_audio.py` | Enhanced quality audio |
| `generate_tts_simple.py` | Simple TTS |
| `generate_tts_split.py` | Split TTS |
| `generate_tts_with_voice.py` | TTS with voice selection |
| `generate_post_to_video.py` | Post to video conversion |
| `generate_video_with_remotion.py` | Remotion video generation |
| `generate_segment_images.py` | Video segment images |
| `improve_scripts_for_audio_video.py` | Script improvement |
| `clean_tts_formatting.py` | TTS text cleanup |
| `check_audio_generation_status.py` | Status checking |

## Why Moved?

1. **Centralization**: All media production in one place
2. **Dependencies**: Video/audio dependencies are heavy
3. **Workflow**: Better integration with online-course video pipeline

## See Also

- [online-course/scripts/audio_video/README.md](~/Desktop/online-course/scripts/audio_video/README.md)
- [_archive/](./\_archive/) - Archived copies still available
