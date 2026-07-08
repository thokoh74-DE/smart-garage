# Smart Garage

🇬🇧 [English Version](README.md)

<!-- Badges -->
<p align="center">

[![HACS Custom][hacs-badge]][hacs-url]
[![GitHub Release][release-badge]][release-url]
[![License][license-badge]][license-url]
[![Hassfest][hassfest-badge]][hassfest-url]
[![HACS Validation][hacs-val-badge]][hacs-val-url]
[![CodeQL][codeql-badge]][codeql-url]
[![Downloads][downloads-badge]][release-url]

</p>

<!-- Logo -->
<p align="center">
  <img src="brand/logo.png" width="300" alt="Smart Garage – Öffnen · Schließen · Belüften · Überwachen"/>
</p>

<p align="center">
  <b>Home Assistant Custom Integration für impulsgesteuerte Garagentore</b><br>
  <sub>Öffnen · Schließen · Belüften · Überwachen — vollautomatisch, vollständig lokal</sub>
</p>

<!-- HACS Install Button -->
<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="In HACS öffnen" height="40"/>
  </a>
  &nbsp;&nbsp;
  <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_garage">
    <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Integration hinzufügen" height="40"/>
  </a>
</p>

---

## 🏠 Was ist Smart Garage?

Smart Garage steuert **impulsgesteuerte Garagentore** — also Tore, bei denen ein einzelner Relaisimpuls folgenden Zyklus durchläuft:

> **Auf → Stop → Zu → Stop → Auf → …**

Anders als einfache Ein/Aus-Schalter verwendet Smart Garage eine **impulszählende State Machine**, die jederzeit weiß, wo das Tor steht — auch nach einem HA-Neustart, auch bei Bedienung über den physischen Taster, auch bei Stopp mitten in der Fahrt.

Entwickelt für **Homematic IP** Hardware, aber kompatibel mit **jedem impulsgesteuerten Garagentorantrieb**, der eine Home Assistant Switch- oder Button-Entity hat.

---

## ✨ Hauptfunktionen

<table>
<tr>
<td width="60">🚪</td>
<td><b>Impulsbasierte Torsteuerung</b><br>Impulszählende State Machine mit Sync-Punkten von Endschaltern. Kennt den exakten Torzustand jederzeit.</td>
</tr>
<tr>
<td>📍</td>
<td><b>Live-Position</b><br>Schätzt die Position während der Fahrt anhand der Fahrzeit. Zeigt „Position 45%" bei Stopp mitten in der Fahrt.</td>
</tr>
<tr>
<td>💾</td>
<td><b>Zustandsspeicherung</b><br>Überlebt HA-Neustarts. Stellt Sync-Zustand und Impulszähler über RestoreEntity wieder her.</td>
</tr>
<tr>
<td>🌬️</td>
<td><b>Lüftungssteuerung</b> (optional)<br>Öffnet das Tor automatisch einen kleinen Spalt basierend auf absoluter Luftfeuchtigkeit. Berücksichtigt Anwesenheit und Tageslicht. Manueller Schalter inklusive.</td>
</tr>
<tr>
<td>🌧️</td>
<td><b>Regen-Automatik</b> (optional)<br>Schließt das Tor bei Regen. Konfigurierbare Verzögerung. Push-Benachrichtigung vor dem Schließen.</td>
</tr>
<tr>
<td>🛡️</td>
<td><b>Versehentliches-Öffnen-Schutz</b><br>Erkennt, wenn sich das Tor deutlich über den Lüftungsspalt hinaus bewegt — bestätigt durch den oberen Endschalter oder anhaltende Vibration über einem Schwellwert — und schließt automatisch mit Benachrichtigung. Löst nur aus, wenn die Lüftungsstellung automatisch (feuchtebasiert) oder über den manuellen Lüftungsschalter erreicht wurde und das Tor danach übersteuert. Löst nie aus bei einem expliziten Öffnen-Befehl (UI, Service-Call oder physischer Taster), auch nicht aus der Lüftungsstellung heraus.</td>
</tr>
<tr>
<td>📡</td>
<td><b>Aktor-Überwachung</b><br>Warnt, wenn der Schaltaktor nicht erreichbar ist und das Tor geöffnet ist. Alle Entities werden als „nicht verfügbar" markiert.</td>
</tr>
<tr>
<td>🔘</td>
<td><b>Externer Taster</b><br>Erkennt physische Tasterbetätigungen und aktualisiert die State Machine entsprechend.</td>
</tr>
<tr>
<td>📊</td>
<td><b>Diagnose</b><br>Vollständiger State-Dump als Download von der Geräteseite. Spiegel-Sensoren für Dashboard-Anzeige.</td>
</tr>
<tr>
<td>🌍</td>
<td><b>Zweisprachig</b><br>Vollständige Deutsch + Englisch Übersetzungen. Entity-IDs immer auf Englisch. Anzeigenamen folgen der HA-Spracheinstellung.</td>
</tr>
</table>

---

## 📋 Voraussetzungen

| Komponente | Erforderlich? | Zweck |
|:-----------|:-------------:|:------|
| **Switch- oder Button-Entity** | ✅ Erforderlich | Schaltet den Garagentorantrieb (z.B. HmIP-PCBS) |
| Endschalter — unten | ⭐ Empfohlen | Bestätigt geschlossene Position (z.B. HmIP-FCI6 ch1) |
| Endschalter — oben | ⭐ Empfohlen | Bestätigt geöffnete Position (z.B. HmIP-FCI6 ch2) |
| Erschütterungssensor | 💡 Optional | Bewegungserkennung + Sicherheit (z.B. HmIP-STV) |
| Externer Taster | 💡 Optional | Erkennung physischer Tasterbetätigung |
| Temperatur + Feuchte — innen | 💡 Optional | Aktiviert Lüftungssteuerung |
| Temperatur + Feuchte — außen | 💡 Optional | Aktiviert Lüftungssteuerung |
| Regensensor | 💡 Optional | Aktiviert Regen-Automatik |
| Anwesenheits-Entity | 💡 Optional | Lüftung nur bei Anwesenheit |
| Benachrichtigungs-Service | 💡 Optional | Push-Nachrichten für Sicherheitsereignisse |

> 💡 **Sanfte Degradierung**: Die Integration funktioniert auch nur mit einem Steuerungsschalter. Jeder optionale Sensor fügt Funktionen hinzu. Ohne Klima-Sensoren → keine Lüftung. Ohne Regensensor → keine Regen-Automatik. Die Entities für deaktivierte Funktionen werden einfach nicht erstellt.

---

## 📦 Installation

### Über HACS (empfohlen)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="In HACS öffnen"/>
</a>

**Oder manuell:**
1. HACS öffnen → **Integrationen** → ⋮ → **Benutzerdefinierte Repositories**
2. URL: `https://github.com/thokoh74-DE/smart-garage`
3. Kategorie: **Integration**
4. Nach **Smart Garage** suchen → Installieren → HA neustarten

### Manuelle Installation

1. [Neuestes Release](https://github.com/thokoh74-DE/smart-garage/releases) herunterladen
2. `custom_components/smart_garage/` nach `config/custom_components/` kopieren
3. Home Assistant neustarten

---

## ⚙️ Einrichtung

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_garage">
  <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Integration hinzufügen"/>
</a>

**Oder:** Einstellungen → Geräte & Dienste → Integration hinzufügen → **Smart Garage**

### 5-Schritte-Assistent

| Schritt | Was konfiguriert wird |
|:-------:|:----------------------|
| **1** | **Name** (wird Gerätename + Entity-Präfix), Steuerungsschalter, Impulszeiten |
| **2** | Endschalter, Erschütterungssensor, externer Taster — *alles optional* |
| **3** | Versehentliches-Öffnen-Schutz, Vibrationsschwelle, Benachrichtigungs-Service |
| **4** | Lüftungssteuerung aktivieren oder deaktivieren |
| **5** | Klima-Sensoren, Regensensor, Schwellwerte — *alles optional* |

### Nachträgliche Konfiguration

Nach der Einrichtung: ⚙️ Zahnrad-Symbol → **Menü mit 4 unabhängigen Bereichen**. Nur bearbeiten, was nötig ist.

---

## 📊 Entities

### Steuerung

| Entity | Typ | Erstellt |
|:-------|:----|:---------|
| *(Gerätename)* | `cover` | Immer |
| Belüftung Automatik | `switch` | Bei aktivierter Lüftung |
| Regen Automatik | `switch` | Bei konfiguriertem Regensensor |
| Manuelle Lüftung | `switch` | Bei aktivierter Lüftung |

### Sensoren

| Entity | Typ | Erstellt |
|:-------|:----|:---------|
| Lüftungsempfehlung | `sensor` | Bei konfigurierten Klima-Sensoren |
| Abs. Feuchte Innen / Außen | `sensor` | Bei konfigurierten Klima-Sensoren |
| Taupunkt Innen / Außen | `sensor` | Bei konfigurierten Klima-Sensoren |
| Belüftung aktiv | `binary_sensor` | Bei aktivierter Lüftung |
| Aktor erreichbar | `binary_sensor` | Immer |

### Diagnose

| Entity | Typ | Beschreibung |
|:-------|:----|:-------------|
| Aktueller Zustand | `sensor` | Menschenlesbarer Zustand mit Position (z.B. „Position 45%") |
| Letzter Fahrbefehl | `sensor` | Letzte Zustandsänderung (übersetzter Enum) |
| Letzter Befehl | `sensor` | Letzter Benutzerbefehl (übersetzter Enum) |
| Impulszähler | `sensor` | Anzahl gesendeter Impulse seit dem letzten bestätigten Endschalter-Sync; setzt sich auf 0 zurück, sobald das Tor vollständig geschlossen oder geöffnet ist |
| Endschalter unten / oben | `sensor` | Spiegelt Hardware-Sensorstatus |
| Erschütterungssensor | `sensor` | Spiegelt Hardware-Sensorstatus |
| Schaltaktor | `sensor` | Spiegelt Hardware-Sensorstatus |

---

## 🔧 Funktionsweise

### Der Impulsmotor-Zyklus

```
Ab GESCHLOSSEN:
  Impuls 1 → ÖFFNET       Impuls 2 → GESTOPPT
  Impuls 3 → SCHLIEẞT     Impuls 4 → GESTOPPT
  Impuls 5 → ÖFFNET       (Zyklus wiederholt sich)

Ab GEÖFFNET:
  Impuls 1 → SCHLIEẞT     Impuls 2 → GESTOPPT
  Impuls 3 → ÖFFNET       Impuls 4 → GESTOPPT
  Impuls 5 → SCHLIEẞT     (Zyklus wiederholt sich)
```

### Impulszählende State Machine

Die Integration speichert zwei Werte:
- **Sync-Zustand** — letzte bestätigte Position vom Endschalter (`GESCHLOSSEN` oder `GEÖFFNET`)
- **Impulszähler** — Anzahl Impulse seit dem letzten Sync

Aktueller Torzustand = **`Sync-Zustand + (Impulszähler - 1) mod 4`**

Wenn ein Endschalter auslöst → Zähler wird auf 0 zurückgesetzt (neuer Sync-Punkt).

### Positionsberechnung

Während der Fahrt: `Position = verstrichene_Zeit ÷ Fahrzeit × 100%`

Die Position wird relativ zu einer **Basislinie berechnet, die zu Beginn jeder Bewegung erfasst wird** — nicht immer ausgehend von 0% oder 100%. Das ist wichtig bei wiederholten Stop-Umkehr-Zyklen: Öffnen, Stoppen, erneut Öffnen setzt die Berechnung korrekt an der zuletzt bekannten Position fort, statt sie auf eine volle 0–100%-Fahrt zurückzusetzen.

Sind Endschalter konfiguriert, nimmt die Integration **niemals** an, dass das Tor seine Endposition erreicht hat — sie wartet auf die Sensorbestätigung.

### Multi-Impuls-Befehle

| Von → Nach | Impulse | Sequenz |
|:-----------|:-------:|:--------|
| Geschlossen → Öffnet | 1 | Auf |
| Öffnet → Gestoppt | 1 | Stop |
| Gestoppt (oben) → Schließt | 1 | Zu |
| Gestoppt (oben) → Öffnet | 3 | Zu → Stop → Auf |
| Gestoppt (unten) → Schließt | 3 | Auf → Stop → Zu |
| Schließt → Öffnet | 2 | Stop → Auf |

Alle Multi-Impuls-Sequenzen laufen einmal gestartet immer vollständig durch — siehe [Befehlsserialisierung](#befehlsserialisierung) unten für den Umgang mit überlappenden Befehlen.

### Befehlsserialisierung

Ein neuer Befehl während einer laufenden Multi-Impuls-Sequenz (z.B. einer Zu→Stop→Auf-Umkehr) konnte früher dazu führen, dass Impulse zweier überlappender Befehle gleichzeitig gesendet wurden — der Impulszähler geriet dadurch außer Sync mit der echten Torposition. Jeder Befehl läuft jetzt unter einer exklusiven Sperre:

1. Ein neuer Befehl wartet, bis ein laufender Befehl vollständig abgeschlossen ist, bevor er startet.
2. Multi-Impuls-Sequenzen laufen immer ungestört bis zum Ende durch — sie werden nie mitten in der Sequenz unterbrochen.
3. Erst wenn der vorherige Befehl vollständig fertig ist, startet der neue Befehl und handelt auf Basis des tatsächlichen, resultierenden Torzustands.

Das garantiert, dass sich Impulse zweier Befehle niemals vermischen können. Der Kompromiss ist eine kleine Verzögerung (höchstens ein paar Impulspausen, typischerweise deutlich unter 2 Sekunden), falls ein neuer Befehl während einer laufenden Multi-Impuls-Sequenz eintrifft — ein deutlich sichereres und vorhersehbareres Verhalten, als zu versuchen, Impulse mitten im Ablauf zu unterbrechen.

Du kannst das am **Impulszähler**-Diagnosesensor live mitverfolgen: Er erhöht sich mit jedem gesendeten Impuls und setzt sich auf 0 zurück, sobald ein Endschalter bestätigt, dass das Tor vollständig geschlossen oder geöffnet ist — so lässt sich jederzeit prüfen, ob die interne Zählung mit der echten Torposition übereinstimmt.

---

## 🔌 Unterstützte Hardware

### Getestet mit

| Gerät | Typ | Zweck |
|:------|:----|:------|
| **HmIP-PCBS** | Schaltaktor | Steuerrelais (Impuls) |
| **HmIP-FCI6** | Kontaktinterface | Endschalter (ch1 = unten, ch2 = oben) |
| **HmIP-STV** | Neigungssensor | Erschütterung / Bewegungserkennung |

### Homematic IP Verkabelungshinweise

| Gerät | Kanal | Funktion | Invertieren? |
|:------|:------|:---------|:-------------|
| HmIP-FCI6 | ch1 | Endschalter unten | **Ja** (OFF = geschlossen) |
| HmIP-FCI6 | ch2 | Endschalter oben | **Nein** (ON = offen) |
| HmIP-PCBS | — | Steuerungsschalter | — |
| HmIP-STV | — | Erschütterungssensor | — |

### Kompatibel mit

Alle impulsgesteuerten Garagentorantriebe, die über eine Home Assistant `switch`- oder `button`-Entity steuerbar sind. Das umfasst Motoren von Hörmann, Marantec, Chamberlain, Sommer, Novoferm und andere mit einfachem Impuls-/Toggle-Mechanismus.

---

## 🐛 Fehlerbehebung

<details>
<summary><b>Entity-IDs haben falsche Sprache</b></summary>

Entity-IDs werden bei der ersten Erstellung generiert. Bei Altlasten aus früheren Versionen: Integration löschen und neu hinzufügen.
</details>

<details>
<summary><b>Homematic-Aktor verliert Verbindung</b></summary>

Die **Impulspause** in den Einstellungen erhöhen. Homematic IP-Geräte können die Verbindung verlieren, wenn sie zu viele HF-Signale in kurzer Zeit empfangen. Standard ist 1 Sekunde; versuche 2-3 Sekunden.
</details>

<details>
<summary><b>Falscher Zustand nach HA-Neustart</b></summary>

Der Zustand wird über RestoreEntity gespeichert. Falls falsch: Tor einmal betätigen, damit ein Endschalter auslöst und einen Sync triggert (setzt den Impulszähler auf 0).
</details>

<details>
<summary><b>Stop reagiert langsam</b></summary>

In v1.0 behoben: Service-Calls verwenden Fire-and-Forget (kein `blocking=True`), sodass der Stop-Befehl sofort verarbeitet wird.
</details>

<details>
<summary><b>Position wird nach wiederholten Stop-Umkehr-Zyklen ungenau</b></summary>

In v1.0.3 behoben: Die Position wird jetzt relativ zu einer Basislinie berechnet, die zu Beginn jeder Bewegung erfasst wird, statt immer von 0% oder 100% auszugehen. Auf die neueste Version aktualisieren, falls das Problem weiterhin auftritt.
</details>

<details>
<summary><b>Fehlerhafte „Versehentliches Öffnen"-Warnung beim eigenen Öffnen</b></summary>

In v1.0.3 behoben: Die Sicherheitswarnung erscheint nicht mehr bei einem expliziten Öffnen-Befehl (UI, Service-Call oder physischer Taster), auch nicht aus der Lüftungsstellung heraus. Sie erscheint jetzt korrekt nur noch, wenn das Tor nach einer automatischen oder manuellen Lüftungsauslösung über den Spalt hinausfährt, ohne dass ein expliziter Öffnen-Befehl vorlag.
</details>

<details>
<summary><b>Tor reagiert falsch (oder fährt in die falsche Richtung) nach schnellen Auf/Stop/Auf-Klicks</b></summary>

In v1.0.4 behoben: Befehle werden jetzt vollständig serialisiert, indem einfach auf das Ende jeder laufenden Multi-Impuls-Sequenz gewartet wird, statt sie zu unterbrechen. Ein früherer, unterbrechungsbasierter Ansatz (v1.0.3) konnte selbst dazu führen, dass eine Sequenz nach nur 1 von 3 Impulsen abbrach, wenn sich zwei Befehle überlappten — das Tor blieb dann hängen. Auf die neueste Version aktualisieren, falls das Problem weiterhin auftritt. Am **Impulszähler**-Diagnosesensor lässt sich prüfen, ob der interne Zähler mit der physischen Torbewegung übereinstimmt.
</details>

<details>
<summary><b>Diagnosedaten benötigt?</b></summary>

Geräteseite → ⋮ → **Diagnose herunterladen**. Erstellt eine JSON-Datei mit dem vollständigen State-Machine-Zustand, Sensorstatus und Konfiguration (sensible Daten geschwärzt).
</details>

---

## 🏆 Quality Scale

Diese Integration zielt auf den [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) **Silver**-Tier.

| Regel | Status |
|:------|:------:|
| Config Flow | ✅ |
| Entity Unique ID | ✅ |
| Unique Config Entry | ✅ |
| Test Before Setup | ✅ |
| Config Entry Unloading | ✅ |
| Entity Unavailable | ✅ |
| Action Exceptions | ✅ |
| Parallel Updates | ✅ |
| Integration Owner | ✅ |
| Diagnostics | ✅ |
| Entity Translations | ✅ |
| Devices | ✅ |
| Reconfigure Flow | ✅ |

Details in [`quality_scale.yaml`](custom_components/smart_garage/quality_scale.yaml).

---

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte lies [CONTRIBUTING.md](CONTRIBUTING.md) vor dem Einreichen eines PRs.

## 📄 Lizenz

[MIT](LICENSE) © Thomas

---

<!-- Badge URLs -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[hacs-url]: https://github.com/hacs/integration
[release-badge]: https://img.shields.io/github/v/release/thokoh74-DE/smart-garage?style=for-the-badge
[release-url]: https://github.com/thokoh74-DE/smart-garage/releases
[license-badge]: https://img.shields.io/github/license/thokoh74-DE/smart-garage?style=for-the-badge
[license-url]: https://github.com/thokoh74-DE/smart-garage/blob/main/LICENSE
[hassfest-badge]: https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hassfest.yml?label=Hassfest&style=for-the-badge
[hassfest-url]: https://github.com/thokoh74-DE/smart-garage/actions/workflows/hassfest.yml
[hacs-val-badge]: https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hacs.yml?label=HACS&style=for-the-badge
[hacs-val-url]: https://github.com/thokoh74-DE/smart-garage/actions/workflows/hacs.yml
[codeql-badge]: https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/codeql.yml?label=CodeQL&style=for-the-badge
[codeql-url]: https://github.com/thokoh74-DE/smart-garage/actions/workflows/codeql.yml
[downloads-badge]: https://img.shields.io/github/downloads/thokoh74-DE/smart-garage/total?style=for-the-badge
