from pathlib import Path
from collections import deque,Counter
p=Path('work/oneseg');out=Path('outputs')
import sys
raw=bytearray((p/(sys.argv[1] if len(sys.argv)>1 else 'base_440563.ts')).read_bytes());packets=[raw[i:i+188] for i in range(0,len(raw),188)]
def pid(b):return ((b[1]&31)<<8)|b[2]
# Locate audio bytes across TS/PES boundaries; only change MPEG identification in ADTS.
audio=bytearray();locations=[]
for i,b in enumerate(packets):
 if pid(b)!=257 or not b[3]&16:continue
 off=4+(1+b[4] if b[3]&32 else 0)
 if b[1]&64:
  assert b[off:off+3]==b'\x00\x00\x01'
  off+=9+b[off+8]
 for j in range(off,188):audio.append(b[j]);locations.append((i,j))
j=0;frames=0
while j<len(audio):
 assert audio[j]==255 and audio[j+1]&0xf6==0xf0,(j,len(audio))
 length=((audio[j+3]&3)<<11)|(audio[j+4]<<3)|(audio[j+5]>>5)
 assert length>=7 and j+length<=len(audio)
 i,k=locations[j+1];packets[i][k]|=8
 j+=length;frames+=1
# Extract the existing PCR-to-byte-clock origin and remove old PCR fields.
origin=None
rate=440563.1533659215
for i,b in enumerate(packets):
 if b[3]&32 and b[4]>=7 and b[5]&16:
  q=b[6:12];v=(((q[0]<<25)|(q[1]<<17)|(q[2]<<9)|(q[3]<<1)|(q[4]>>7))*300)+((q[4]&1)<<8)+q[5]
  if origin is None:origin=v-(i*188+11)*8*27000000/440563
  b[5]&=0xef;b[6:12]=b'\xff'*6
assert origin is not None
sections={n:(p/(n+'.bin')).read_bytes() for n in ['pmt','sdt','nit']};cc=Counter()
null=bytearray([0x47,0x1f,0xff,0x10])+bytearray([255])*184
def table(pid,s):
 b=bytearray([0x47,0x40|(pid>>8),pid&255,0x10,0])+s
 return b+bytearray([255])*(188-len(b))
def pcrpacket(i):
 v=round(origin+(i*188+11)*8*27000000/rate);base,ext=divmod(v,300)
 q=bytes([(base>>25)&255,(base>>17)&255,(base>>9)&255,(base>>1)&255,((base&1)<<7)|0x7e|(ext>>8),ext&255])
 return bytearray([0x47,0x01,0x00,0x20,183,0x10])+q+bytearray([255])*176
# Keep packets in order; reserved PCR slots consume stuffing capacity via a queue.
queue=deque();result=[];maxqueue=0;lastnit=-1000
for i in range(len(packets)+4096):
 if i<len(packets):
  b=packets[i];k=pid(b)
  if k==4096:b=table(8136,sections['pmt'])
  elif k==17:b=table(17,sections['sdt'])
  elif k in (0,8191):b=None
  if b is not None:queue.append(b)
 if i%16==0:b=pcrpacket(i)
 elif i-lastnit>=100 and (not queue or (i<len(packets) and pid(packets[i]) in (0,8191))):
  b=table(16,sections['nit']);lastnit=i
 elif queue:b=queue.popleft()
 else:b=null.copy()
 k=pid(b)
 if k!=8191:
  if b[3]&16:cc[k]=(cc[k]+1)%16
  b[3]=(b[3]&0xf0)|cc[k]
 result.append(b);maxqueue=max(maxqueue,len(queue))
 if i>=len(packets)-1 and not queue and (i+1)%64==0:break
assert not queue
(out/(sys.argv[2] if len(sys.argv)>2 else 'layer_a_corregida.ts')).write_bytes(b''.join(result))
print('AAC MPEG-2 frames:',frames,'packets:',len(result),'max queued packets:',maxqueue,'PCR every 16 packets, exact layer rate',rate)
