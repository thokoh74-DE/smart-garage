# Changelog / Änderungsprotokoll

## [1.0.4] – 2025-07-08

### Fixed / Behoben

- 🔒 **Command serialization simplified — fixes door getting stuck after v1.0.3's fix** – The v1.0.3 fix used an immediate-interrupt approach: a new command would signal any in-progress multi-pulse sequence to abort right away. This could itself cause a sequence to abort after only 1 of its 3 pulses if two commands overlapped (e.g. a duplicate/near-simultaneous service call), leaving the door stopped partway with no further movement. Commands now simply **wait** for any in-progress sequence to finish completely instead of interrupting it — multi-pulse sequences always run undisturbed to completion, and a new command only starts once the previous one has fully stopped. This trades a small delay (at most ~2 seconds, only when a new command arrives mid-sequence) for much higher reliability. / **Befehlsserialisierung vereinfacht — behebt hängenbleibendes Tor nach dem v1.0.3-Fix** – Der v1.0.3-Fix nutzte einen Sofort-Unterbrechungsansatz: Ein neuer Befehl signalisierte jeder laufenden Multi-Impuls-Sequenz, sofort abzubrechen. Das konnte selbst dazu führen, dass eine Sequenz nach nur 1 von 3 Impulsen abbrach, wenn sich zwei Befehle überlappten (z.B. durch einen doppelten/nahezu gleichzeitigen Service-Call) — das Tor blieb dann mitten in der Fahrt ohne weitere Bewegung stehen. Befehle **warten** jetzt einfach, bis eine laufende Sequenz vollständig abgeschlossen ist, statt sie zu unterbrechen — Multi-Impuls-Sequenzen laufen immer ungestört bis zum Ende durch, und ein neuer Befehl startet erst, wenn der vorherige vollständig fertig ist. Das kostet eine kleine Verzögerung (höchstens ca. 2 Sekunden, nur wenn ein neuer Befehl mitten in einer Sequenz eintrifft) für deutlich höhere Zuverlässigkeit.

### Added / Hinzugefügt

- 🔢 **Pulse Count diagnostic sensor** – Shows the number of pulses sent since the last confirmed limit-switch sync as a plain number, resetting to 0 the moment the door reaches fully closed or fully open. Makes it easy to verify the pulse-counting state machine matches the real door position at a glance. / **Diagnosesensor „Impulszähler"** – Zeigt die Anzahl der gesendeten Impulse seit dem letzten bestätigten Endschalter-Sync als einfache Zahl an und setzt sich auf 0 zurück, sobald das Tor vollständig geschlossen oder geöffnet ist. Macht es einfach, auf einen Blick zu prüfen, ob die impulszählende State Machine mit der echten Torposition übereinstimmt.

## [1.0.3] – 2025-07-08

### Fixed / Behoben

- 🔒 **Command race condition causing door desync** – Rapidly clicking through commands (e.g. Open → Stop → Open faster than a multi-pulse reversal sequence completes) could send pulses from two overlapping commands at the same time, corrupting the internal pulse counter and desyncing it from the real door position — leading to the door moving the wrong direction, becoming unresponsive, or falsely showing "fully open." Every command now runs under an exclusive lock: a new command immediately interrupts any in-progress pulse sequence and waits for it to fully stop before sending its own pulses, so pulses can never interleave. Stop remains instantly responsive throughout. / **Race Condition bei Befehlsüberlappung verursachte Tor-Desync** – Schnelles Durchklicken von Befehlen (z.B. Auf → Stop → Auf schneller als eine Multi-Impuls-Umkehrsequenz abschließt) konnte dazu führen, dass Impulse zweier überlappender Befehle gleichzeitig gesendet wurden, was den internen Impulszähler korrumpierte und von der echten Torposition entkoppelte — das Tor fuhr in die falsche Richtung, reagierte nicht mehr oder zeigte fälschlich „vollständig geöffnet" an. Jeder Befehl läuft jetzt unter einer exklusiven Sperre: Ein neuer Befehl unterbricht sofort jede laufende Impulssequenz und wartet, bis diese vollständig gestoppt hat, bevor er eigene Impulse sendet. Stop bleibt dabei durchgehend sofort reaktionsschnell.
- 📍 **Position estimation accuracy** – Position is now calculated relative to a baseline captured at the start of each movement, instead of always assuming travel from 0% or 100%. Repeated stop/reverse cycles no longer produce wildly inaccurate position jumps. / **Genauigkeit der Positionsberechnung** – Die Position wird jetzt relativ zu einer Basislinie berechnet, die zu Beginn jeder Bewegung erfasst wird, statt immer von 0% oder 100% auszugehen. Wiederholte Stop-Umkehr-Zyklen führen nicht mehr zu stark ungenauen Positionssprüngen.
- 🛡️ **False "accidental opening" alerts** – The safety warning no longer fires when the door is opened via an explicit command (UI, service call, or the physical garage button), even from a ventilating state. It now correctly fires only when the door overshoots past the ventilation gap after an *automatic* (humidity-based) or *manual switch* ventilation trigger, without an explicit open command. / **Fehlerhafte „Versehentliches Öffnen"-Warnungen** – Die Sicherheitswarnung erscheint nicht mehr, wenn das Tor über einen expliziten Befehl (UI, Service-Call oder physischer Garagentaster) geöffnet wird, auch nicht aus der Lüftungsstellung heraus. Sie erscheint jetzt korrekt nur noch, wenn das Tor nach einer automatischen oder manuellen Lüftungsauslösung über den Spalt hinausfährt, ohne dass ein expliziter Öffnen-Befehl vorlag.
- 📡 **Unreliable external-press detection removed** – The integration no longer tries to infer physical button presses from the control switch's own on/off echo, which was prone to misfires with RF hardware confirmation delays. Physical presses are still detected reliably via the dedicated external button entity, if configured. / **Unzuverlässige Erkennung externer Tasterdrücke entfernt** – Die Integration versucht nicht mehr, physische Tasterdrücke aus dem Ein/Aus-Echo des Schaltaktors selbst abzuleiten, was bei Funklaufzeiten der Hardware zu Fehlauslösungen neigte. Physische Tasterdrücke werden weiterhin zuverlässig über die dedizierte externe Taster-Entity erkannt, sofern konfiguriert.
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
