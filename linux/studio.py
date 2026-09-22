"""ONE SEG Studio Linux frontend. RF starts only from the explicit transmit button."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))) / 'one-seg-studio'

NAVY = '#142b42'
NAVY_SOFT = '#1d3a56'
INK = '#1d2d3e'
MUTED = '#7d8791'
PAPER = '#f6f3ec'
CARD = '#ffffff'
RED = '#e63025'
BLUE = '#087bf4'
GREEN = '#2fc96c'
LINE = '#dde1e4'


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
        self.device_text = tk.StringVar(value='HackRF sin comprobar')
        self.status_text = tk.StringVar(value='Elige un vídeo para preparar el canal')
        self.file_name = tk.StringVar(value='Tu próximo canal empieza aquí')
        self.file_subtitle = tk.StringVar(value='Archivo de vídeo · perfil One-Seg')
        self.frequency_text = tk.StringVar()
        self.gain_text = tk.StringVar()

        window.title('ONE SEG Studio for vanhoteen · Linux preview')
        window.geometry('1180x790')
        window.minsize(940, 680)
        window.configure(bg=PAPER)
        self.configure_style()
        self.logo = self.load_logo()
        self.build()
        for variable in (self.file, self.channel, self.rate, self.gain, self.amp):
            variable.trace_add('write', self.changed)
        self.changed()
        window.protocol('WM_DELETE_WINDOW', self.close)

    def configure_style(self):
        style = ttk.Style(self.window)
        style.theme_use('clam')
        style.configure('Primary.TButton', background=RED, foreground='white', borderwidth=0,
                        padding=(18, 10), font=('TkDefaultFont', 11, 'bold'))
        style.map('Primary.TButton', background=[('active', '#c8271e'), ('disabled', '#efaaa5')])
        style.configure('Dark.TButton', background=NAVY, foreground='white', borderwidth=0,
                        padding=(14, 8), font=('TkDefaultFont', 10, 'bold'))
        style.map('Dark.TButton', background=[('active', NAVY_SOFT), ('disabled', '#aab3ba')])
        style.configure('Soft.TButton', background='#e3e4e1', foreground=INK, borderwidth=0,
                        padding=(13, 8), font=('TkDefaultFont', 10, 'bold'))
        style.map('Soft.TButton', background=[('active', '#d4d7d5'), ('disabled', '#eaebe9')])
        style.configure('Rate.TRadiobutton', background='#e8e8e5', foreground=INK, padding=(14, 7),
                        font=('TkDefaultFont', 10, 'bold'))
        style.map('Rate.TRadiobutton', background=[('selected', BLUE)], foreground=[('selected', 'white')])
        style.configure('TCombobox', padding=5)

    def load_logo(self):
        path = ROOT / 'Assets' / 'one-seg-logo.png'
        if not path.is_file():
            return None
        try:
            image = tk.PhotoImage(file=path)
            factor = max(1, image.width() // 76)
            return image.subsample(factor, factor)
        except tk.TclError:
            return None

    def label(self, parent, text='', *, size=11, weight='normal', fg=INK, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=fg,
                        font=('TkDefaultFont', size, weight), **kwargs)

    def card(self, parent, **kwargs):
        return tk.Frame(parent, bg=CARD, highlightbackground='#ecebe7', highlightthickness=1, **kwargs)

    def build(self):
        header = tk.Frame(self.window, bg=PAPER, padx=38, pady=23)
        header.pack(fill='x')
        if self.logo:
            tk.Label(header, image=self.logo, bg=PAPER).pack(side='left', padx=(0, 14))
        else:
            self.label(header, '▣', size=34, weight='bold', fg=RED).pack(side='left', padx=(0, 14))
        title = tk.Frame(header, bg=PAPER)
        title.pack(side='left')
        self.label(title, 'ONE SEG', size=29, weight='bold', fg=NAVY).pack(anchor='w')
        self.label(title, 'STUDIO  /  for vanhoteen', size=12, weight='bold', fg=NAVY).pack(anchor='w')
        right = tk.Frame(header, bg=PAPER)
        right.pack(side='right')
        self.label(right, 'ワンセグ', size=15, weight='bold', fg=NAVY).pack(anchor='e')
        self.label(right, 'Probado con Sony XDV-D500 · Linux beta', size=10, fg=MUTED).pack(anchor='e')
        tk.Frame(self.window, bg=RED, height=4).pack(fill='x')

        body = tk.Frame(self.window, bg=PAPER, padx=38, pady=22)
        body.pack(fill='both', expand=True)

        connection = self.card(body, padx=20, pady=15)
        connection.pack(fill='x', pady=(0, 20))
        self.label(connection, '⌁', size=25, weight='bold', fg=NAVY).pack(side='left', padx=(0, 12))
        conn_info = tk.Frame(connection, bg=CARD)
        conn_info.pack(side='left', fill='x', expand=True)
        self.label(conn_info, 'CONEXIÓN HACKRF', size=10, weight='bold', fg=NAVY).pack(anchor='w')
        self.label(conn_info, textvariable=self.device_text, size=13, fg=INK).pack(anchor='w')
        self.device_dot = tk.Label(connection, text='●', bg=CARD, fg='#9ca1a7', font=('TkDefaultFont', 14))
        self.device_dot.pack(side='right', padx=10)
        self.detect_button = ttk.Button(connection, text='Detectar HackRF', style='Dark.TButton', command=self.detect)
        self.detect_button.pack(side='right')

        columns = tk.Frame(body, bg=PAPER)
        columns.pack(fill='x')
        columns.columnconfigure(0, weight=1)
        columns.columnconfigure(1, weight=1)

        left = tk.Frame(columns, bg=PAPER)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        self.label(left, '01', size=10, weight='bold', fg=RED).pack(anchor='w', side='left')
        self.label(left, '  CONTENIDO', size=10, weight='bold', fg=NAVY).pack(anchor='w')
        preview = tk.Frame(left, bg=NAVY, height=205)
        preview.pack(fill='x', pady=(10, 12))
        preview.pack_propagate(False)
        self.label(preview, '▤', size=37, fg='#f5f4ed').pack(pady=(36, 6))
        tk.Label(preview, textvariable=self.file_name, bg=NAVY, fg='white',
                 font=('TkDefaultFont', 14, 'bold')).pack()
        tk.Label(preview, textvariable=self.file_subtitle, bg=NAVY, fg='#a8b2bd',
                 font=('TkDefaultFont', 10, 'bold')).pack(pady=(7, 0))
        ttk.Button(left, text='▱  Elegir vídeo…', style='Soft.TButton', command=self.choose).pack(fill='x')
        chips = tk.Frame(left, bg=PAPER, pady=14)
        chips.pack(anchor='w')
        for value in ('320 × 240', '15 FPS', 'AAC 48k'):
            chip = tk.Label(chips, text=value, bg='#e9e8e2', fg=NAVY, padx=12, pady=6,
                            font=('TkFixedFont', 9, 'bold'))
            chip.pack(side='left', padx=(0, 8))

        right = self.card(columns, padx=22, pady=19)
        right.grid(row=0, column=1, sticky='nsew', padx=(12, 0))
        heading = tk.Frame(right, bg=CARD)
        heading.pack(fill='x')
        self.label(heading, '02', size=10, weight='bold', fg=RED).pack(side='left')
        self.label(heading, '  CANAL Y CALIDAD', size=10, weight='bold', fg=NAVY).pack(side='left')
        channel_box = ttk.Spinbox(heading, from_=13, to=62, textvariable=self.channel, width=4,
                                  font=('TkFixedFont', 22, 'bold'), justify='center')
        channel_box.pack(side='right')
        self.label(right, 'CH', size=27, weight='bold', fg=NAVY).pack(anchor='w', pady=(16, 0))
        self.label(right, textvariable=self.frequency_text, size=11, fg=MUTED).pack(anchor='w', pady=(2, 13))
        tk.Frame(right, bg=LINE, height=1).pack(fill='x', pady=(0, 16))
        self.label(right, 'Bitrate de vídeo', size=11, weight='bold').pack(anchor='w')
        rate_bar = tk.Frame(right, bg=CARD, pady=9)
        rate_bar.pack(anchor='w')
        for value in ('80', '100', '200', '300'):
            ttk.Radiobutton(rate_bar, text=f'{value}k', value=value, variable=self.rate,
                            style='Rate.TRadiobutton').pack(side='left', padx=(0, 2))
        gain_head = tk.Frame(right, bg=CARD)
        gain_head.pack(fill='x', pady=(8, 0))
        self.label(gain_head, 'Ganancia VGA', size=11, weight='bold').pack(side='left')
        self.label(gain_head, textvariable=self.gain_text, size=11, weight='bold', fg=NAVY).pack(side='right')
        tk.Scale(right, from_=0, to=47, orient='horizontal', variable=self.gain, showvalue=False,
                 bg=CARD, fg=RED, activebackground=RED, highlightthickness=0, troughcolor='#dedfdd',
                 sliderrelief='flat').pack(fill='x', pady=(0, 10))
        amp_row = tk.Frame(right, bg=CARD)
        amp_row.pack(fill='x')
        self.label(amp_row, 'Amplificador RF', size=11, weight='bold').pack(side='left')
        ttk.Checkbutton(amp_row, variable=self.amp).pack(side='right')

        signal_head = tk.Frame(body, bg=PAPER, pady=18)
        signal_head.pack(fill='x')
        self.label(signal_head, '⌁', size=16, weight='bold', fg=NAVY).pack(side='left')
        self.label(signal_head, '  Señal de salida', size=11, weight='bold', fg=NAVY).pack(side='left')
        self.label(signal_head, 'I/Q', size=9, weight='bold', fg=RED).pack(side='right')
        graph = tk.Canvas(body, height=105, bg=NAVY, highlightthickness=0)
        graph.pack(fill='x')
        graph.bind('<Configure>', self.draw_graph)

        log_frame = self.card(body, padx=16, pady=10)
        log_frame.pack(fill='both', expand=True, pady=(17, 0))
        log_top = tk.Frame(log_frame, bg=CARD)
        log_top.pack(fill='x')
        self.label(log_top, 'Registro', size=10, weight='bold', fg=NAVY).pack(side='left')
        self.log = tk.Text(log_frame, height=6, state='disabled', wrap='word', borderwidth=0,
                           bg='#fbfbfa', fg=INK, font=('TkFixedFont', 9))
        self.log.pack(fill='both', expand=True, pady=(6, 0))

        footer = tk.Frame(self.window, bg=CARD, padx=38, pady=14, highlightbackground=LINE, highlightthickness=1)
        footer.pack(fill='x', side='bottom', before=body)
        self.status_dot = tk.Label(footer, text='●', bg=CARD, fg='#9ca1a7', font=('TkDefaultFont', 13))
        self.status_dot.pack(side='left')
        self.label(footer, textvariable=self.status_text, size=11, weight='bold').pack(side='left', padx=(9, 24))
        self.stop_button = ttk.Button(footer, text='■  Detener', style='Soft.TButton', command=self.stop)
        self.stop_button.pack(side='right')
        self.transmit_button = ttk.Button(footer, text='▶  Iniciar emisión', style='Primary.TButton', command=self.transmit)
        self.transmit_button.pack(side='right', padx=(10, 0))
        self.prepare_button = ttk.Button(footer, text='✧  Preparar vídeo', style='Soft.TButton', command=self.prepare)
        self.prepare_button.pack(side='right', padx=(0, 10))
        self.tools_button = ttk.Button(footer, text='Comprobar herramientas', style='Soft.TButton', command=self.check)
        self.tools_button.pack(side='right', padx=(0, 10))
        self.actions = [self.detect_button, self.tools_button, self.prepare_button, self.transmit_button]

    def draw_graph(self, event):
        canvas = event.widget
        canvas.delete('all')
        width, height = event.width, event.height
        for y in range(16, height, 25):
            canvas.create_line(16, y, width - 16, y, fill='#31495e')
        canvas.create_text(width // 2, height // 2, text='La gráfica aparecerá al emitir', fill='#a8b2bd',
                           font=('TkDefaultFont', 10, 'bold'))

    def snapshot(self):
        path = Path(self.file.get()).expanduser()
        stat = path.stat() if path.is_file() else None
        return (str(path.resolve()), self.channel.get(), self.rate.get(), self.gain.get(),
                self.amp.get(), (stat.st_size, stat.st_mtime_ns) if stat else None)

    def changed(self, *_):
        self.prepared = None
        try:
            channel = int(self.channel.get())
        except ValueError:
            channel = 20
        frequency = (473142857.142857 + (channel - 13) * 6000000) / 1e6
        self.frequency_text.set(f'{frequency:.6f} MHz  ·  Japón')
        self.gain_text.set(f'{self.gain.get()} dB')

    def choose(self):
        if self.process:
            return
        name = filedialog.askopenfilename(title='Elegir vídeo')
        if name:
            self.file.set(name)
            self.file_name.set(Path(name).name)
            self.file_subtitle.set('Archivo de vídeo seleccionado · perfil One-Seg')
            self.status_text.set('Vídeo seleccionado · prepara el canal')

    def append(self, text):
        self.log.config(state='normal')
        self.log.insert('end', text)
        self.log.see('end')
        self.log.config(state='disabled')

    def set_status(self, text, color='#9ca1a7'):
        self.status_text.set(text)
        self.status_dot.config(fg=color)

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
        self.set_status(label, '#f5a623')
        for button in self.actions:
            button.config(state='disabled')
        self.window.after(100, self.poll)

    def poll(self):
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
        if self.cancelled:
            self.set_status('Emisión detenida', '#9ca1a7')
        elif result == 0:
            self.set_status('Operación terminada', GREEN)
        else:
            self.set_status('Falló · consulta el registro', RED)
        if result == 0 and not self.cancelled and self.completed:
            self.completed()
        if self.closing:
            self.window.destroy()

    def check(self):
        self.run([sys.executable, str(ROOT / 'linux/check.py')], 'Comprobando herramientas · sin RF')

    def detect(self):
        def done():
            self.device_text.set('HackRF detectado y listo')
            self.device_dot.config(fg=GREEN)
            self.set_status('HackRF detectado · RF detenida', GREEN)
        self.run(['SoapySDRUtil', '--probe=driver=hackrf'], 'Comprobando HackRF · sin RF', done)

    def prepare(self):
        snapshot = self.snapshot()
        self.prepared = None
        if snapshot[-1] is None:
            messagebox.showerror('Vídeo', 'Elige primero un archivo de vídeo.')
            return
        def done():
            if snapshot == self.snapshot():
                self.prepared = snapshot
                self.set_status('Canal preparado · RF detenida', GREEN)
        self.run([sys.executable, str(ROOT / 'prepare.py'), snapshot[0], snapshot[1],
                  snapshot[3], snapshot[2], str(int(snapshot[4]))], 'Preparando vídeo · RF detenida', done)

    def transmit(self):
        if self.prepared is None or self.prepared != self.snapshot():
            messagebox.showerror('Preparar vídeo', 'Prepara el vídeo con la configuración actual antes de emitir.')
            return
        self.run([sys.executable, str(ROOT / 'signal_tx.py'), str(DATA / 'outputs')], 'Emisión activa · consulta el registro')

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
    lock = (DATA / 'studio.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit('ONE SEG Studio is already running for this user.')
    window = tk.Tk()
    Studio(window)
    window.mainloop()
