"""Prepare an isolated, finite One-Seg file test. Never starts RF."""
from pathlib import Path
import sys, subprocess, shutil, os
root = Path(__file__).resolve().parent/'Payload'
stage = Path(os.environ['ONESEG_DATA'])
work = stage/'work/oneseg'
out = stage/'outputs'
work.mkdir(parents=True, exist_ok=True); out.mkdir(exist_ok=True)
source, channel, gain = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
source = str(Path(source).resolve())
bitrate = int(sys.argv[4]) if len(sys.argv) > 4 else 80
if bitrate not in (80, 100, 200, 300):
    raise ValueError('Bitrate no admitido')
amplifier_arg = sys.argv[5] if len(sys.argv) > 5 else '0'
if amplifier_arg not in ('0', '1'):
    raise ValueError('Amplificador no válido')
amplifier = amplifier_arg == '1'
# Preserve the known-working 80/100 profile; other profiles cap at their target.
peak = max(100, bitrate)
print(f'Vídeo {bitrate} kb/s; máximo {peak} kb/s; audio 48 kb/s', flush=True)
assert 13 <= channel <= 62 and 0 <= gain <= 47
def run(args): subprocess.run(args, cwd=stage, check=True)
for name in ['correct_transport.py','build_si_trial.py','pat.bin','pmt.bin','sdt.bin','sdt.xml','nit.bin']:
    shutil.copy2(root/'work/oneseg'/name, work/name)
shutil.copy2(root/'outputs/layer_b_oneseg.ts',out/'layer_b_oneseg.ts')
freq = 473142857.142857 + (channel-13)*6000000
nit = (root/'work/oneseg/nit.xml').read_text().replace('515142858',str(round(freq)))
(work/'nit.xml').write_text(nit)
run(['tstabcomp','--japan',str(work/'nit.xml'),'-o',str(work/'nit.bin')])
run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-i',source,'-map','0:v:0','-map','0:a:0?',
 '-vf','scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2,setsar=1','-r','15',
 '-c:v','libx264','-profile:v','baseline','-level:v','1.2','-pix_fmt','yuv420p','-b:v',f'{bitrate}k','-maxrate:v',f'{peak}k','-bufsize:v',f'{peak}k',
 '-g','15','-bf','0','-refs','1','-x264-params','repeat-headers=1:aud=1:scenecut=0:force-cfr=1',
 '-c:a','aac','-ar','24000','-ac','2','-b:a','48k','-mpegts_service_id','1544','-mpegts_pmt_start_pid','4096',
 '-streamid','0:256','-streamid','1:257','-muxrate','440563','-f','mpegts',str(work/'base_440563.ts')])
run([sys.executable,str(work/'correct_transport.py')])
run([sys.executable,str(work/'build_si_trial.py')])
template = (root/'studio_tx.py.template').read_text()
for key, value in {'__FREQUENCY__': repr(freq), '__GAIN__': repr(gain), '__AMPLIFIER__': repr(amplifier), '__LAYER_A__': repr(str(out/'layer_a_si_prueba.ts')), '__LAYER_B__': repr(str(out/'layer_b_si_prueba.ts'))}.items():
    template = template.replace(key, value)
compile(template, 'studio_tx.py', 'exec')
(out/'studio_tx.py').write_text(template)
print('Preparación terminada. RF detenida.',flush=True)
