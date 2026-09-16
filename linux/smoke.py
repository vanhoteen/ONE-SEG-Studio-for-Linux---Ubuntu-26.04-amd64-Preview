"""Prepare three seconds of bars and audio in a temporary folder; never transmit."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory(prefix='oneseg-linux-test-') as temporary:
        data = Path(temporary)
        env = dict(os.environ, ONESEG_DATA=temporary)
        def run(args):
            return subprocess.run(args, env=env, check=True, capture_output=True, text=True).stdout
        video = data/'bars.mp4'
        run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'smptebars=size=320x240:rate=15',
             '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=24000', '-t', '3',
             '-c:v', 'libx264', '-c:a', 'aac', str(video)])
        print(run([sys.executable, str(ROOT/'prepare.py'), str(video), '20', '0', '80', '0']))
        output = data/'outputs'
        streams = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json',
                                  str(output/'layer_a_si_prueba.ts')]))['streams']
        assert any(s['codec_name'] == 'h264' and s['width'] == 320 and s['height'] == 240 for s in streams)
        assert any(s['codec_name'] == 'aac' for s in streams)
        template = (output/'studio_tx.py').read_text()
        compile(template, 'studio_tx.py', 'exec')
        assert "'AMP', False" in template
        for name in ('layer_a_si_prueba.ts', 'layer_b_si_prueba.ts'):
            raw = (output/name).read_bytes()
            assert raw and len(raw) % 188 == 0
            assert all(raw[i] == 0x47 for i in range(0, len(raw), 188))
        print('PASS: video, audio and packet alignment. No transmitter constructed; no RF.')

if __name__ == '__main__':
    main()
