from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter
import subprocess, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs'
WORK = ROOT / 'work/oneseg/si_trial'
WORK.mkdir(exist_ok=True)
rate = 440563.1533659215
start = datetime.now(timezone.utc).replace(microsecond=0)

def compile_table(name, xml):
    path = WORK / (name + '.xml')
    path.write_text('<tsduck>' + xml + '</tsduck>')
    subprocess.run(['tstabcomp', '--japan', str(path), '-o', str(path.with_suffix('.bin'))], check=True)
    raw = path.with_suffix('.bin').read_bytes()
    sections = []
    while raw:
        size = 3 + ((raw[1] & 15) << 8) + raw[2]
        sections.append(raw[:size]); raw = raw[size:]
    return sections

def crc(b):
    value = 0xffffffff
    for x in b:
        value ^= x << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value

cc = Counter()
def packet(pid, section):
    assert len(section) <= 183
    if section[0] != 0x70:
        assert crc(section) == 0
    b = bytes([0x47, 0x40 | (pid >> 8), pid & 255, 0x10 | cc[pid], 0]) + section
    cc[pid] = (cc[pid] + 1) % 16
    return b + b'\xff' * (188-len(b))

def pid(b): return ((b[1] & 31) << 8) | b[2]
raw = (OUT/(sys.argv[1] if len(sys.argv)>1 else 'layer_a_corregida.ts')).read_bytes()
packets = [raw[i:i+188] for i in range(0,len(raw),188)]
# XML time fields are UTC; --japan serializes the Japanese time reference.
eit = compile_table('eit', f'''<EIT type="pf" version="1" current="true" actual="true" service_id="0x0608" transport_stream_id="0x7FF0" original_network_id="0x7FF0" last_table_id="0x4E"><event event_id="1" start_time="{start:%Y-%m-%d %H:%M:%S}" duration="00:05:00" running_status="running" CA_mode="false"><short_event_descriptor language_code="spa"><event_name>Prueba One Seg</event_name><text>Prueba de laboratorio</text></short_event_descriptor></event></EIT>''')
sdt_text = (ROOT/'work/oneseg/sdt.xml').read_text().replace('<tsduck>', '').replace('</tsduck>', '').replace('running_status="running"', 'EIT_present_following="true" running_status="running"').replace('<SDT ', '<SDT version="1" ')
sdt = compile_table('sdt', sdt_text)[0]
next_clock = next_eit = 0
pending = []
inserted = Counter()
positions = {}
for i,b in enumerate(packets):
    t = i*1504/rate
    if pid(b) == 17:
        # Preserve original SDT packet continuity counter.
        replacement = bytearray(packet(17,sdt)); replacement[3] = b[3]
        packets[i] = bytes(replacement)
    if pid(b) != 8191: continue
    if not pending:
        if t >= next_clock:
            now = start + timedelta(seconds=int(t))
            sections = compile_table('clock', f'<TDT UTC_time="{now:%Y-%m-%d %H:%M:%S}"/><TOT UTC_time="{now:%Y-%m-%d %H:%M:%S}"/>')
            pending.extend((20,s) for s in sections)
            next_clock = t + 5
        elif t >= next_eit:
            pending.extend((18,s) for s in eit)
            next_eit = t + 1
    if pending:
        p,s = pending.pop(0)
        packets[i] = packet(p,s)
        inserted[hex(s[0])] += 1
        positions.setdefault(hex(s[0]),[]).append(t)
assert not pending
result = b''.join(packets)
assert len(result) == len(raw)
for i,b in enumerate(packets):
    old = raw[i*188:(i+1)*188]
    if pid(old) in (256,257): assert b == old
last = {}
for b in packets:
    p = pid(b)
    if p == 8191: continue
    c = b[3]&15
    if p in last: assert c == ((last[p]+(1 if b[3]&16 else 0))&15), (p,c,last[p])
    last[p] = c
(OUT/(sys.argv[2] if len(sys.argv)>2 else 'layer_a_si_prueba.ts')).write_bytes(result)
# B remains byte-identical, including its PAT and loop continuity.
(OUT/'layer_b_si_prueba.ts').write_bytes((OUT/'layer_b_oneseg.ts').read_bytes())
# Analysis-only reconstruction: PAT prefix lets generic TS tools identify A.
pat = (ROOT/'work/oneseg/pat.bin').read_bytes()
(WORK/'analysis.ts').write_bytes(packet(0,pat)+result)
report = {'created_utc':start.isoformat(), 'packets':len(packets), 'rate_bps':rate,
 'inserted_sections':dict(inserted), 'av_and_pcr_packets_byte_identical':True,
 'continuity_errors':0, 'max_interval_seconds':{k:max([b-a for a,b in zip(v,v[1:])] or [0]) for k,v in positions.items()},
 'limitation':'Experimental SI addition, not certification of ARIB conformity or Sony reception. EIT p/f on PID 0x12. Clock is a dated file snapshot; regenerate before later tests. PAT remains in B.'}
(OUT/'auditoria_si_prueba.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
