"""Read-only dependency checks. No device is opened and no flowgraph is built."""
import importlib
import shutil
import sys

def main():
    missing = []
    for name in ('ffmpeg', 'ffprobe', 'tstabcomp', 'SoapySDRUtil'):
        path = shutil.which(name)
        print(f'{name}: {path or "MISSING"}')
        if path is None:
            missing.append(name)
    for name in ('tkinter', 'numpy', 'gnuradio.gr', 'gnuradio.blocks',
                 'gnuradio.dtv', 'gnuradio.soapy', 'gnuradio.isdbt'):
        try:
            importlib.import_module(name)
            print(f'{name}: OK')
        except (ImportError, OSError) as error:
            print(f'{name}: {error}')
            missing.append(name)
    print('No RF transmission started.')
    return bool(missing)

if __name__ == '__main__':
    sys.exit(main())
