"""Authoring tool: synthetic script -> one-voice short TTS smoke audio.
Not a real meeting, a five-minute exercise, or a Whisper-generated transcript.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import edge_tts

BASE=Path(__file__).resolve().parent
async def main():
    folder=BASE/'start/audio';folder.mkdir(exist_ok=True)
    path=folder/'meeting-smoke.mp3'
    if path.exists():raise ValueError('기존 음원을 보존합니다.')
    lines=(BASE/'start/meeting-script.md').read_text(encoding='utf-8').splitlines()
    text='\n'.join(line.split(': ',1)[-1] for line in lines if ': ' in line)
    await edge_tts.Communicate(text,'ko-KR-InJoonNeural',rate='+0%').save(str(path))
    metadata={'source':'../meeting-script.md','voice':'ko-KR-InJoonNeural','tool':'edge-tts==7.2.8',
              'data_origin':'synthetic-tts','purpose':'short-smoke','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'speaker_count':1,'not_real_meeting':True,'full_five_minute_pack':'planned'}
    (folder/'manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Synthetic short audio created: {path.stat().st_size} bytes')
asyncio.run(main())
