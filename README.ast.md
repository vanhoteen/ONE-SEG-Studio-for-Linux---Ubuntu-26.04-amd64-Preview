# ONE SEG Studio for Linux

## 🌐 Escueyi la to llingua

### [🇬🇧 English](README.md)
### [🇪🇸 Castellano](README.es.md)
### [<img src="Assets/flag-asturias.svg" width="32" alt="Asturias"> Asturianu](README.ast.md)
### [🇩🇪 Deutsch](README.de.md)
### [<img src="Assets/flag-catalunya.svg" width="32" alt="Catalunya"> Català](README.ca.md)

---

<img src="Assets/app-icon.png" width="180" alt="ONE SEG Studio">

> **VERSIÓN EXPERIMENTAL DE PRUEBES — Ubuntu 26.04 LTS · amd64 (Intel/AMD de 64 bits). Nun ye una versión estable.**

Proyeutu de **vanhoteen** pa preparar vídeos y xenerar una señal xaponesa One-Seg con HackRF One. Na configuración habitual, el segmentu central de los trece d'ISDB-T lleva televisión pa pequeños receptores, ensin Internet.

L'autor probó la instalación y la recepción nuna Sony XDV-D500 con Ubuntu 26.04 amd64. Otres distribuciones y arquitectures nun tán verificaes.

## Instalación

[Descargues del instalador](https://github.com/vanhoteen/ONE-SEG-Studio-for-Linux---Ubuntu-26.04-amd64-Preview/releases). L'autor va xubir el paquete probáu por separao. Los archivos **Source code** nun son l'instalador.

Descarga y descomprime la carpeta completa. Caltién xuntos los dos `.deb`, `INSTALL.sh`, `UBUNTU_VERSION` y `SHA256SUMS`. Abre una terminal nella y executa:

```bash
bash INSTALL.sh
```

Necesites Internet y contraseña d'alministrador. Instálense la aplicación, TSDuck y les dependencies de Ubuntu; nun fai falta compilar. Abre ONE SEG Studio nel menú d'aplicaciones del escritoriu.

Conecta HackRF, pulsa **Check tools** y **Detect HackRF**, escueyi un vídeo y pulsa **Prepare video**. **Transmit** entama la emisión; **Stop** pá­rala. La instalación y la preparación nun emiten.

## Llendes y responsabilidá

Interfaz namái n'inglés. Nun inclúi cámara nin gráfica integrada; nun garantiza un bucle continuu nin certificación de la norma. Comprueba les frecuencies, potencies y permisos del to país antes d'emitir. Un canal xaponés nun da autorización local. Evita interferencies; l'usuariu ye responsable de los permisos y del usu del equipu. Na midida permitida pola llei, l'autor nun asume responsabilidá por usos non autorizaos o interferencies causaes pol usuariu.

Más detalles na [guía en castellano](README.es.md), les [notes de compilación](linux/README.md) y les [licencies](LICENSE-NOTICE.md).

## Demo · One-Seg

[![One-Seg demo](https://img.youtube.com/vi/hW7jU8Ro0uk/hqdefault.jpg)](https://youtu.be/hW7jU8Ro0uk)

[macOS project](https://github.com/vanhoteen/ONE-SEG-Studio-)
