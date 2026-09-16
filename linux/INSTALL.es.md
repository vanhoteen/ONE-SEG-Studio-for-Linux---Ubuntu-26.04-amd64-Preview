# Instalar ONE SEG Studio

Esta primera versión está preparada para Ubuntu 24.04 y 26.04 en ordenadores Intel/AMD de 64 bits. El autor ha confirmado la recepción en una Sony XDV-D500 con Ubuntu 26.04 amd64; Ubuntu 24.04 no está probado.

Recibirás una carpeta con el `.deb` de ONE SEG Studio, el paquete oficial de TSDuck y el instalador. Conserva los archivos juntos. En esa carpeta ejecuta:

```sh
bash INSTALL.sh
```

Se solicita la contraseña de administrador. Ubuntu instala los dos paquetes y descarga las dependencias necesarias. Hace falta conexión a Internet. No hay que compilar nada ni instalar Python con pip en el ordenador de destino.

Después abre **ONE SEG Studio** desde el menú de aplicaciones. Pulsa **Check tools**, conecta el HackRF y pulsa **Detect HackRF**. La instalación y estas comprobaciones no inician una transmisión. La emisión se inicia únicamente con **Transmit** después de preparar un vídeo y debe cumplir las normas locales.

El módulo gr-isdbt ya viene compilado. GNU Radio, FFmpeg y las bibliotecas se gestionan como dependencias de Ubuntu: no es un paquete autónomo sin Internet como el DMG de Mac. TSDuck se proporciona como segundo paquete oficial para no requerir añadir un repositorio externo.

Para desinstalar la aplicación: `sudo apt remove one-seg-studio`. Los vídeos preparados se conservan en `~/.local/share/one-seg-studio`.

The Debian build selects the matching Ubuntu TSDuck package and VOLK development package, and derives the Python ABI requirement from the build interpreter. Each installer checks the exact Ubuntu version recorded at build time.
