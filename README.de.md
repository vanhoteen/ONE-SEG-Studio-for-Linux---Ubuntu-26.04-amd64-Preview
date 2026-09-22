# ONE SEG Studio for Linux

## 🌐 Wähle deine Sprache

### [🇬🇧 English](README.md)
### [🇪🇸 Castellano](README.es.md)
### [<img src="Assets/flag-asturias.svg" width="32" alt="Asturias"> Asturianu](README.ast.md)
### [🇩🇪 Deutsch](README.de.md)
### [<img src="Assets/flag-catalunya.svg" width="32" alt="Catalunya"> Català](README.ca.md)

---

<img src="Assets/app-icon.png" width="180" alt="ONE SEG Studio">

> **EXPERIMENTELLE TESTVERSION — Ubuntu 26.04 LTS · amd64 (Intel/AMD, 64 Bit). Keine stabile Veröffentlichung.**

Ein Projekt von **vanhoteen**: Videos vorbereiten und mit einem HackRF One ein japanisches One-Seg-Fernsehsignal erzeugen. Bei der üblichen ISDB-T-Konfiguration versorgt das mittlere der dreizehn Segmente tragbare Empfänger mit Fernsehen geringerer Auflösung, ohne Internetempfang.

Der Autor hat Installation und Empfang mit einem Sony XDV-D500 unter Ubuntu 26.04 amd64 erfolgreich getestet. Andere Distributionen und Architekturen sind nicht geprüft.

## Installation

[Installer herunterladen](https://github.com/vanhoteen/ONE-SEG-Studio-for-Linux---Ubuntu-26.04-amd64-Preview/releases). Der Autor lädt das getestete Paket separat hoch. Die automatischen **Source code**-Archive sind keine Installer.

Den vollständigen Installer-Ordner herunterladen und entpacken. Beide `.deb`-Dateien, `INSTALL.sh`, `UBUNTU_VERSION` und `SHA256SUMS` zusammen lassen. Im Ordner ein Terminal öffnen:

```bash
bash INSTALL.sh
```

Internet und Administratorpasswort werden benötigt. Die Anwendung, TSDuck und Ubuntu-Abhängigkeiten werden installiert. Auf dem Zielcomputer muss nichts kompiliert werden. Anschließend ONE SEG Studio im Anwendungsmenü des Linux-Desktops öffnen.

HackRF anschließen, **Check tools** und **Detect HackRF** wählen, Video auswählen und **Prepare video** anklicken. **Transmit** startet die Aussendung; **Stop** beendet sie. Installation und Vorbereitung senden nicht.

## Grenzen und Verantwortung

Die Linux-Oberfläche ist auf Spanisch und Englisch verfügbar. Kameraeingang und integrierte Signalanzeige fehlen; unterbrechungslose Wiederholung ist nicht garantiert. Keine Normzertifizierung. Vor dem Senden örtliche Frequenz-, Leistungs- und Genehmigungsvorschriften prüfen. Eine japanische Kanalnummer ist keine örtliche Sendegenehmigung. Schädliche Störungen vermeiden; der Nutzer ist für Genehmigungen und Betrieb verantwortlich. Soweit gesetzlich zulässig, übernimmt der Autor keine Verantwortung für unbefugten Betrieb oder vom Nutzer verursachte Störungen.

Weitere Angaben: [englische Anleitung](README.md), [Build-Anleitung](linux/README.md), [Lizenzen](LICENSE-NOTICE.md).

## Demo · One-Seg

[![One-Seg demo](https://img.youtube.com/vi/hW7jU8Ro0uk/hqdefault.jpg)](https://youtu.be/hW7jU8Ro0uk)

[macOS project](https://github.com/vanhoteen/ONE-SEG-Studio-)
