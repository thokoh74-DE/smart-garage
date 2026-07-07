# Changelog / Änderungsprotokoll

## [1.0.3] – 2025-07-07

### Fixed / Behoben
- 📍 **Position estimation accuracy** – Position is now calculated relative to a baseline captured at the start of each movement, instead of always assuming travel from 0% or 100%. Repeated stop/reverse cycles (open → stop → open → stop → open) no longer produce wildly inaccurate position jumps. / **Genauigkeit der Positionsberechnung** – Die Position wird jetzt relativ zu einer Basislinie berechnet, die zu Beginn jeder Bewegung erfasst wird, statt immer von 0% oder 100% auszugehen. Wiederholte Stop-Umkehr-Zyklen (Öffnen → Stop → Öffnen → Stop → Öffnen) führen nicht mehr zu stark ungenauen Positionssprüngen.
- 🛡️ **False "accidental opening" alerts** – The safety warning no longer fires when the door is opened via an explicit command (UI, service call, or the physical garage button), even from a ventilating state. It now correctly fires only when the door overshoots past the ventilation gap after an *automatic* (humidity-based) or *manual switch* ventilation trigger, without an explicit open command. / **Fehlerhafte „Versehentliches Öffnen"-Warnungen** – Die Sicherheitswarnung erscheint nicht mehr, wenn das Tor über einen expliziten Befehl (UI, Service-Call oder physischer Garagentaster) geöffnet wird, auch nicht aus der Lüftungsstellung heraus. Sie erscheint jetzt korrekt nur noch, wenn das Tor nach einer *automatischen* (feuchtebasierten) oder *manuellen* Lüftungsauslösung über den Spalt hinausfährt, ohne dass ein expliziter Öffnen-Befehl vorlag.
- 🔧 **Firmware version display** – The device page now reads the version dynamically from `manifest.json` instead of showing a hardcoded value that never matched the installed release. / **Firmware-Versionsanzeige** – Die Geräteseite liest die Version jetzt dynamisch aus `manifest.json`, statt einen fest einprogrammierten Wert anzuzeigen, der nie mit dem installierten Release übereinstimmte.
- 🐛 **Duplicate `async_stop` method** – The controller had two methods named `async_stop` (lifecycle cleanup vs. door stop command); the second silently shadowed the first. The cleanup method is now `async_unload`. / **Doppelte `async_stop`-Methode** – Der Controller hatte zwei Methoden namens `async_stop` (Lifecycle-Cleanup vs. Tor-Stop-Befehl); die zweite überschrieb die erste stillschweigend. Die Cleanup-Methode heißt jetzt `async_unload`.
- 🧹 Removed wildcard imports (`from .const import *`) across all files in favor of explicit imports, resolving 196+ lint findings. / Wildcard-Imports (`from .const import *`) in allen Dateien durch explizite Imports ersetzt, behebt 196+ Lint-Befunde.

### Added / Hinzugefügt
- ✅ `ConfigEntryNotReady` raised when the control switch entity doesn't exist yet at setup / `ConfigEntryNotReady` wird ausgelöst, wenn die Steuerungsschalter-Entity beim Setup noch nicht existiert
- ✅ Duplicate config entry prevention via `async_set_unique_id` / Verhinderung doppelter Konfigurationseinträge via `async_set_unique_id`
- ✅ `available` property on all entities – marks them unavailable when the actor is unreachable / `available`-Property auf allen Entities – markiert sie als nicht verfügbar, wenn der Aktor nicht erreichbar ist
- ✅ `HomeAssistantError` raised on failed cover commands instead of failing silently / `HomeAssistantError` bei fehlgeschlagenen Cover-Befehlen statt stillem Fehlschlag
- ✅ `PARALLEL_UPDATES = 1` on the cover platform to prevent race conditions / `PARALLEL_UPDATES = 1` auf der Cover-Plattform verhindert Race Conditions
- ✅ `diagnostics.py` for downloadable state dumps from the device page / `diagnostics.py` für herunterladbare State-Dumps von der Geräteseite
- ✅ `quality_scale.yaml` tracking Home Assistant Quality Scale compliance / `quality_scale.yaml` zur Nachverfolgung der Home Assistant Quality Scale

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
