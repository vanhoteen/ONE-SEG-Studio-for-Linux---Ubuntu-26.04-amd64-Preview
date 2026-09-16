# ONE SEG Studio for Linux

## 🌐 Tria el teu idioma

### [🇬🇧 English](README.md)
### [🇪🇸 Castellano](README.es.md)
### [<img src="Assets/flag-asturias.svg" width="32" alt="Asturias"> Asturianu](README.ast.md)
### [🇩🇪 Deutsch](README.de.md)
### [<img src="Assets/flag-catalunya.svg" width="32" alt="Catalunya"> Català](README.ca.md)

---

<img src="Assets/app-icon.png" width="180" alt="ONE SEG Studio">

> **VERSIÓ EXPERIMENTAL DE PROVES — Ubuntu 26.04 LTS · amd64 (Intel/AMD de 64 bits). No és una versió estable.**

Projecte de **vanhoteen** per preparar vídeos i generar un senyal japonès One-Seg amb un HackRF One. En la configuració habitual d'ISDB-T, el segment central dels tretze porta televisió de menys resolució per a receptors petits, sense Internet.

L'autor ha provat la instal·lació i la recepció en una Sony XDV-D500 amb Ubuntu 26.04 amd64. Altres distribucions i arquitectures no s'han verificat.

## Instal·lació

[Descàrregues de l'instal·lador](https://github.com/vanhoteen/ONE-SEG-Studio-for-Linux---Ubuntu-26.04-amd64-Preview/releases). L'autor pujarà el paquet provat per separat. Els fitxers automàtics **Source code** no són l'instal·lador.

Descarrega i descomprimeix la carpeta completa. Mantén junts els dos `.deb`, `INSTALL.sh`, `UBUNTU_VERSION` i `SHA256SUMS`. Obre un terminal dins de la carpeta i executa:

```bash
bash INSTALL.sh
```

Cal Internet i la contrasenya d'administrador. S'instal·len l'aplicació, TSDuck i les dependències d'Ubuntu; no cal compilar a l'ordinador de destinació. Obre ONE SEG Studio des del menú d'aplicacions de l'escriptori Linux.

Connecta el HackRF, prem **Check tools** i **Detect HackRF**, tria un vídeo i prem **Prepare video**. **Transmit** inicia l'emissió; **Stop** l'atura. Instal·lar i preparar no emet.

## Limitacions i responsabilitat

Interfície Linux només en anglès. No inclou càmera ni gràfica integrada, i no garanteix un bucle continu ni certificació de la norma. Comprova les freqüències, potències i autoritzacions del teu país abans d'emetre. Un canal japonès no concedeix autorització local. Evita interferències; l'usuari és responsable dels permisos i de l'ús de l'equip. En la mesura permesa per la llei, l'autor no assumeix responsabilitat pels usos no autoritzats o les interferències causades per l'usuari.

Més detalls a la [guia en castellà](README.es.md), les [notes de compilació](linux/README.md) i les [llicències](LICENSE-NOTICE.md).

## Demo · One-Seg

[![One-Seg demo](https://img.youtube.com/vi/hW7jU8Ro0uk/hqdefault.jpg)](https://youtu.be/hW7jU8Ro0uk)

[macOS project](https://github.com/vanhoteen/ONE-SEG-Studio-)
