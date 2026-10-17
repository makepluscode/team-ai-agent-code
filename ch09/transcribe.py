"""Prepared CPU/int8 Whisper base entry point; no program generation."""
import argparse
import hashlib
import time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from part3 import save,unchanged,read,record  # noqa: E402

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workspace',type=Path,default=Path('work-part03'))
p.add_argument('--audio',type=Path)
a=p.parse_args();work=a.workspace.resolve()
started=time.monotonic()
try:
    unchanged(work)
    audio=(a.audio or work/'input/audio/meeting-smoke.mp3').resolve()
    if not audio.is_file():raise ValueError('음원 파일이 없습니다. 제공 음원 또는 --audio 경로를 확인합니다.')
    if (work/'output/transcript.json').exists():raise ValueError('기존 전사문을 보존합니다.')
    from faster_whisper import WhisperModel
    load_start=time.monotonic()
    model=WhisperModel('base',device='cpu',compute_type='int8')
    load_seconds=time.monotonic()-load_start
    inference_start=time.monotonic()
    prompt=(work/'input/glossary.txt').read_text(encoding='utf-8')
    segments,info=model.transcribe(str(audio),language='ko',beam_size=5,initial_prompt=prompt)
    rows=[dict(start=s.start,end=s.end,text=s.text) for s in segments]
    result={'source':str(audio),'sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),
            'meeting_id':read(work/'input/meeting.json')['id'],'data_origin':'measured-transcription',
            'model':'base','device':'cpu','compute_type':'int8','language':info.language,
            'load_seconds':round(load_seconds,3),'transcription_seconds':round(time.monotonic()-inference_start,3),
            'segments':rows,'speaker_identification':False}
    save(work/'output/transcript.json',result);unchanged(work)
    record(work,'transcribe','ok',time.monotonic()-started)
    print('실제 전사문 저장 완료. 고유명사·날짜·금액은 음원과 대조합니다.')
except Exception as e:
    if (work/'input-hashes.json').exists():record(work,'transcribe','failed',time.monotonic()-started)
    p.exit(1,f'확인 필요: {e}\n')
