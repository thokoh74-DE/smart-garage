# Changelog / Änderungsprotokoll

## [1.0.0] – 2025-07-05

### Added / Hinzugefügt
- 🚪 Pulse-counting state machine with `RestoreEntity` persistence / Impulszählende State Machine mit Zustandsspeicherung
- 🎮 Cover entity: open, close, stop, set_position / Cover-Entity: Öffnen, Schließen, Stop, Position setzen
- 🌬️ Integrated ventilation control with abs. humidity + dew point / Integrierte Lüftungssteuerung mit abs. Feuchte + Taupunkt
- 🌧️ Rain auto-close with delay and push notification / Regen-Automatik mit Verzögerung und Push-Nachricht
- 🛡️ Accidental opening protection via vibration sensor / Versehentliches-Öffnen-Schutz via Erschütterungssensor
- 🔘 Manual ventilation switch / Manueller Lüftungsschalter
- 📡 Actor reachability monitoring / Aktor-Erreichbarkeitsüberwachung
- 🎛️ External button/event detection / Erkennung externer Taster/Events
- 📊 Diagnostic mirror sensors / Diagnose-Spiegel-Sensoren
- 📍 Current state sensor with live position % / Aktueller-Zustand-Sensor mit Live-Position %
- 🏷️ Last drive + last command with translated enum states / Letzter Fahrbefehl + Befehl mit übersetzten Zuständen
- ⚙️ Menu-based options flow (4 independent sections) / Menübasierter Options-Flow (4 unabhängige Bereiche)
- 🌍 Full i18n: German + English / Vollständige Zweisprachigkeit: Deutsch + Englisch
- 🏗️ HACS-compatible repository / HACS-kompatibles Repository
- ⚡ All sensors optional – graceful degradation / Alle Sensoren optional – Funktionen passen sich an

### Technical / Technisch
- Travel timer only as fallback when no limit switch configured / Fahrzeit-Timer nur als Fallback ohne Endschalter
- Fire-and-forget service calls for responsive stop / Nicht-blockierende Service-Calls für schnellen Stop
- Command sequence counter for multi-pulse abort / Befehlszähler für Multi-Impuls-Abbruch
- Language-dependent default device name / Sprachabhängiger Standard-Gerätename
