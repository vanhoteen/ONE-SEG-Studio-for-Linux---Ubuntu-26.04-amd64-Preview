"""Headless transmitter and throttled local waveform snapshots for the studio UI."""
import json
import os
from pathlib import Path
import signal
import sys
import time

import numpy as np
from gnuradio import gr


class Waveform(gr.sync_block):
    def __init__(self, destination):
        gr.sync_block.__init__(self, name='Studio waveform', in_sig=[np.complex64], out_sig=None)
        self.destination = Path(destination)
        self.next_update = 0.0

    def work(self, inputs, outputs):
        samples = inputs[0]
        now = time.monotonic()
        if len(samples) and now >= self.next_update:
            self.next_update = now + 0.25
            # A consecutive short window, not a decimated RF quality estimate.
            window = samples[:256]
            data = {'i': window.real.tolist(), 'q': window.imag.tolist(),
                    'rms': float(np.sqrt(np.mean(np.abs(samples)**2))),
                    'peak': float(np.max(np.abs(samples))), 'time': time.time()}
            try:
                temporary = self.destination.with_suffix('.tmp')
                temporary.write_text(json.dumps(data, allow_nan=False))
                os.replace(temporary, self.destination)
            except (OSError, ValueError):
                pass  # Display failures must not stop the transmitter.
        return len(samples)


def main():
    directory = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(directory))
    from studio_tx import studio_tx
    tb = studio_tx()
    monitor = Waveform(directory/'waveform.json')
    tb.connect(tb.rational_resampler_xxx_0, monitor)
    def stop(*_): tb.stop()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        tb.start()
        print('Transmisor iniciado. Gráfica integrada activa.', flush=True)
        tb.wait()
    finally:
        tb.stop()
        tb.wait()


if __name__ == '__main__': main()
