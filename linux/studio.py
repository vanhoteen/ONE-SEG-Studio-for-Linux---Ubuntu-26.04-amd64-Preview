"""Linux desktop frontend. RF starts only from the explicit transmit button."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))/'one-seg-studio'


class Studio:
    def __init__(self, window):
        self.window = window
        self.process = None
        self.prepared = None
        self.closing = False
        self.cancelled = False
        self.file = tk.StringVar()
        self.channel = tk.StringVar(value='20')
        self.rate = tk.StringVar(value='80')
        self.gain = tk.StringVar(value='0')
        self.amp = tk.BooleanVar(value=False)
        window.title('ONE SEG Studio · vanhoteen · Linux preview')
        window.geometry('820x640')
        window.minsize(720, 540)
        panel = ttk.Frame(window, padding=20)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='ONE SEG STUDIO', font=('', 25, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='for vanhoteen · Linux preview').pack(anchor='w')
        source = ttk.Frame(panel)
        source.pack(fill='x', pady=18)
        ttk.Entry(source, textvariable=self.file).pack(side='left', fill='x', expand=True)
        ttk.Button(source, text='Video…', command=self.choose).pack(side='right')
        settings = ttk.Frame(panel)
        settings.pack(fill='x')
        for column, (name, variable, values) in enumerate([
            ('Channel', self.channel, list(range(13, 63))),
            ('Video kb/s', self.rate, [80, 100, 200, 300]),
            ('VGA dB', self.gain, list(range(48)))
        ]):
            ttk.Label(settings, text=name).grid(row=0, column=column, padx=10)
            ttk.Combobox(settings, textvariable=variable, values=values,
                         state='readonly', width=14).grid(row=1, column=column, padx=10)
        ttk.Checkbutton(panel, text='RF amplifier', variable=self.amp).pack(anchor='w', pady=12)
        self.frequency = ttk.Label(panel)
        self.frequency.pack(anchor='w')
        self.status = ttk.Label(panel, text='Stopped')
        self.status.pack(anchor='w', pady=10)
        self.log = tk.Text(panel, height=12, state='disabled', wrap='word')
        self.log.pack(fill='both', expand=True)
        buttons = ttk.Frame(panel)
        buttons.pack(fill='x', pady=(15, 0))
        self.actions = []
        for name, action in [('Check tools', self.check), ('Detect HackRF', self.detect),
                             ('Prepare video', self.prepare), ('Transmit', self.transmit)]:
            button = ttk.Button(buttons, text=name, command=action)
            button.pack(side='left', padx=3)
            self.actions.append(button)
        ttk.Button(buttons, text='Stop', command=self.stop).pack(side='right')
        for variable in (self.file, self.channel, self.rate, self.gain, self.amp):
            variable.trace_add('write', self.changed)
        self.changed()
        window.protocol('WM_DELETE_WINDOW', self.close)

    def snapshot(self):
        path = Path(self.file.get()).expanduser()
        stat = path.stat() if path.is_file() else None
        return (str(path.resolve()), self.channel.get(), self.rate.get(), self.gain.get(),
                self.amp.get(), (stat.st_size, stat.st_mtime_ns) if stat else None)

    def changed(self, *_):
        self.prepared = None
        self.frequency.config(text=f'{(473142857.142857 + (int(self.channel.get())-13)*6000000)/1e6:.6f} MHz · Japan')

    def choose(self):
        if not self.process:
            name = filedialog.askopenfilename()
            if name:
                self.file.set(name)

    def append(self, text):
        self.log.config(state='normal')
        self.log.insert('end', text)
        self.log.see('end')
        self.log.config(state='disabled')

    def run(self, args, label, completed=None):
        if self.process:
            return
        DATA.mkdir(parents=True, exist_ok=True)
        self.cancelled = False
        self.completed = completed
        self.output = tempfile.TemporaryFile()
        self.offset = 0
        try:
            self.process = subprocess.Popen(args, cwd=ROOT, stdout=self.output,
                stderr=subprocess.STDOUT, start_new_session=True,
                env=dict(os.environ, ONESEG_DATA=str(DATA), PYTHONUNBUFFERED='1'))
        except OSError as error:
            self.output.close()
            messagebox.showerror('ONE SEG Studio', str(error))
            return
        self.status.config(text=label)
        for button in self.actions:
            button.config(state='disabled')
        self.window.after(100, self.poll)

    def poll(self):
        # pread does not move the child's shared log descriptor offset.
        chunk = os.pread(self.output.fileno(), 65536, self.offset)
        self.offset += len(chunk)
        if chunk:
            self.append(chunk.decode('utf-8', errors='replace'))
        result = self.process.poll()
        if result is None or chunk:
            self.window.after(100, self.poll)
            return
        self.output.close()
        self.process = None
        for button in self.actions:
            button.config(state='normal')
        self.status.config(text='Stopped' if self.cancelled else ('Completed' if result == 0 else 'Failed — see log'))
        if result == 0 and not self.cancelled and self.completed:
            self.completed()
        if self.closing:
            self.window.destroy()

    def check(self):
        self.run([sys.executable, str(ROOT/'linux/check.py')], 'Checking tools (no RF)')

    def detect(self):
        self.run(['SoapySDRUtil', '--probe=driver=hackrf'], 'Checking HackRF (no RF stream)')

    def prepare(self):
        snapshot = self.snapshot()
        self.prepared = None
        if snapshot[-1] is None:
            messagebox.showerror('Video', 'Choose a video file first.')
            return
        def done():
            if snapshot == self.snapshot():
                self.prepared = snapshot
                self.status.config(text='Prepared · RF stopped')
        self.run([sys.executable, str(ROOT/'prepare.py'), snapshot[0], snapshot[1],
                  snapshot[3], snapshot[2], str(int(snapshot[4]))], 'Preparing · RF stopped', done)

    def transmit(self):
        if self.prepared is None or self.prepared != self.snapshot():
            messagebox.showerror('Prepare', 'Prepare the video with the current settings first.')
            return
        self.run([sys.executable, str(ROOT/'signal_tx.py'), str(DATA/'outputs')], 'Starting transmitter — see log')

    def stop(self):
        if not self.process:
            return
        self.cancelled = True
        process = self.process
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        def force():
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.window.after(3000, force)

    def close(self):
        if self.process:
            self.closing = True
            self.stop()
        else:
            self.window.destroy()


if __name__ == '__main__':
    import fcntl
    DATA.mkdir(parents=True, exist_ok=True)
    lock = (DATA/'studio.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit('ONE SEG Studio is already running for this user.')
    window = tk.Tk()
    Studio(window)
    window.mainloop()
