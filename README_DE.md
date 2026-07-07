# Smart Garage

🇬🇧 [English Version](README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/thokoh74-DE/smart-garage)](https://github.com/thokoh74-DE/smart-garage/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img src="brand/icon.png" width="128" alt="Smart Garage Logo"/>

Eine Home Assistant Custom Integration für **impulsgesteuerte Garagentore** – also Tore, bei denen ein einzelner Relaisimpuls den Zyklus *Auf → Stop → Zu → Stop → Auf* durchläuft.

Entwickelt für **Homematic IP** Hardware (HmIP-PCBS, HmIP-FCI6, HmIP-STV), funktioniert aber mit jedem impulsgesteuerten Garagentorantrieb.

## Funktionen

### 🚪 Cover Entity mit Impulszählung
- **Impulszählende State Machine** – verfolgt die Torposition durch Zählen der Relaisimpulse ab dem letzten bekannten Synchronisierungspunkt (Endschalter)
- **Zustandsspeicherung** über HA-Neustarts hinweg via `RestoreEntity`
- **Live-Positionsberechnung** während der Fahrt basierend auf der konfigurierten Fahrzeit
- **Erkennung externer Impulse** – erkennt physische Tasterbetätigung und Automationen
- Unterstützt `Öffnen`, `Schließen`, `Stop` und `Position setzen`

### 🌬️ Lüftungssteuerung *(optional)*
- Berechnet **absolute Luftfeuchtigkeit** und **Taupunkt** aus Temperatur-/Feuchte-Sensoren
- Empfiehlt Lüftung, wenn die Innenfeuchte die Außenfeuchte um einen konfigurierbaren Schwellwert übersteigt
- Öffnet das Tor automatisch in einen kleinen Lüftungsspalt (konfigurierbar, z.B. 2s ≈ 10 cm)
- Berücksichtigt **Anwesenheit** (nur wenn jemand zuhause) und **Tageslicht** (Sonnenauf- bis -untergang)
- **Manueller Lüftungsschalter** für direkte Steuerung
- Voraussetzung: Temperatur- und Feuchte-Sensoren (innen + außen)

### 🌧️ Regen-Automatik *(optional)*
- Schließt das Tor automatisch bei Regen
- Konfigurierbare Verzögerung (Standard 4 Min.) – schließt nicht, wenn das Tor gerade erst geöffnet wurde
- Push-Benachrichtigung vor dem Schließen
- Voraussetzung: Regensensor (Binary Sensor)

### 🛡️ Sicherheit
- **Versehentliches-Öffnen-Schutz** – erkennt, wenn sich das Tor deutlich über den Lüftungsspalt hinaus bewegt (bestätigt durch den oberen Endschalter oder anhaltende Vibration über einem konfigurierbaren Schwellwert) und schließt automatisch mit Benachrichtigung
  - **Löst aus**, wenn die Lüftungsstellung automatisch (periodische Feuchte-Prüfung) oder über den manuellen Lüftungsschalter erreicht wurde und das Tor danach weit über den vorgesehenen Spalt hinaus weiterfährt
  - **Löst nie aus** bei einem expliziten Öffnen-Befehl – ein Klick auf „Öffnen" in der UI, ein Service-Call oder das Drücken des physischen Garagentasters öffnet das Tor immer vollständig, ohne Fehlalarm, auch aus der Lüftungsstellung heraus
- **Aktor-Erreichbarkeit** – warnt, wenn der Schaltaktor nicht erreichbar ist, während das Tor geöffnet ist

### 📊 Diagnosesensoren
Spiegel-Sensoren für Dashboard-Anzeige: Endschalter, Erschütterungssensor, Schaltaktor-Status, aktueller Zustand mit Position, letzter Fahrbefehl, letzter Befehl

### 🌍 Zweisprachigkeit
- Vollständige **deutsche** und **englische** UI-Übersetzungen
- Entity-IDs verwenden immer englische Suffixe
- Anzeigenamen folgen der HA-Systemsprache

## Voraussetzungen

| Komponente | Erforderlich | Zweck |
|-----------|-------------|-------|
| Switch- oder Button-Entity | ✅ Ja | Schaltet den Garagentorantrieb |
| Endschalter (unten) | ⬜ Empfohlen | Bestätigt die geschlossene Position |
| Endschalter (oben) | ⬜ Empfohlen | Bestätigt die geöffnete Position |
| Erschütterungssensor | ⬜ Optional | Erkennt Torbewegung, ermöglicht Sicherheitsschutz |
| Externer Taster | ⬜ Optional | Erkennt physische Tasterbetätigung |
| Temp. + Feuchte (innen) | ⬜ Optional | Aktiviert Lüftungssteuerung |
| Temp. + Feuchte (außen) | ⬜ Optional | Aktiviert Lüftungssteuerung |
| Regensensor | ⬜ Optional | Aktiviert Regen-Automatik |
| Anwesenheits-Entity | ⬜ Optional | Lüftung nur bei Anwesenheit |
| Benachrichtigungs-Service | ⬜ Optional | Push-Nachrichten für Ereignisse |

> **Hinweis**: Die Lüftungsfunktionen sind nur verfügbar, wenn alle vier Klima-Sensoren (Innen-/Außen-Temperatur + Feuchte) konfiguriert sind. Die Regen-Automatik benötigt einen Regensensor. Werden diese Sensoren nicht konfiguriert, werden die entsprechenden Funktionen und Schalter einfach nicht erstellt.

## Installation

### HACS (empfohlen)
1. HACS öffnen → **Integrationen** → ⋮ → **Benutzerdefinierte Repositories**
2. `https://github.com/thokoh74-DE/smart-garage` als **Integration** hinzufügen
3. Nach "Smart Garage" suchen und installieren
4. Home Assistant neustarten

### Manuell
1. `custom_components/smart_garage/` in deinen HA `config/custom_components/`-Ordner kopieren
2. Home Assistant neustarten

## Einrichtung

**Einstellungen → Geräte & Dienste → Integration hinzufügen → Smart Garage**

Der Setup-Assistent hat 5 Schritte:
1. **Grundeinstellungen**: Name (wird Gerätename + Entity-Präfix), Steuerungsschalter, Impuls-Zeiten
2. **Sensoren**: Endschalter, Erschütterungssensor, externer Taster *(alle optional)*
3. **Sicherheit**: Versehentliches-Öffnen-Schutz, Vibrationsschwelle, Benachrichtigungs-Service
4. **Lüftung**: Aktivieren/Deaktivieren
5. **Klima-Sensoren**: Innen-/Außen-Temp. + Feuchte, Regensensor, Schwellwerte *(alle optional)*

Nach der Einrichtung kannst du über den **Menü-basierten Options-Flow** (Zahnrad-Symbol) einzelne Bereiche bearbeiten, ohne alle Einstellungen durchklicken zu müssen.

## Erzeugte Entities

| Entity | Typ | Bedingung |
|--------|-----|-----------|
| *(Gerätename)* | `cover` | Immer |
| Belüftung Automatik | `switch` | Lüftung aktiviert |
| Regen Automatik | `switch` | Regensensor konfiguriert |
| Manuelle Lüftung | `switch` | Lüftung aktiviert |
| Lüftungsempfehlung | `sensor` | Klima-Sensoren konfiguriert |
| Abs. Feuchte Innen/Außen | `sensor` | Klima-Sensoren konfiguriert |
| Taupunkt Innen/Außen | `sensor` | Klima-Sensoren konfiguriert |
| Belüftung aktiv | `binary_sensor` | Lüftung aktiviert |
| Aktor erreichbar | `binary_sensor` | Immer |
| Aktueller Zustand | `sensor` (Diagnose) | Immer |
| Letzter Fahrbefehl / Letzter Befehl | `sensor` (Diagnose) | Immer |
| Endschalter unten/oben | `sensor` (Diagnose) | Wenn konfiguriert |
| Erschütterungssensor | `sensor` (Diagnose) | Wenn konfiguriert |
| Schaltaktor | `sensor` (Diagnose) | Immer |

## Funktionsweise

Der Impulsmotor durchläuft 4 Phasen pro Zyklus:

```
Ab GESCHLOSSEN:  Impuls → Öffnet → Impuls → Stop → Impuls → Schließt → Impuls → Stop → ...
Ab GEÖFFNET:     Impuls → Schließt → Impuls → Stop → Impuls → Öffnet → Impuls → Stop → ...
```

Die Integration speichert einen **Sync-Zustand** (letzte bestätigte Position vom Endschalter) und einen **Impulszähler**. Der aktuelle Torzustand ergibt sich aus `Sync-Zustand + Impulszähler mod 4`.

Wenn ein Endschalter auslöst, wird der Zähler auf 0 zurückgesetzt. Sind Endschalter konfiguriert, nimmt die Integration **niemals** an, dass das Tor seine Endposition auf Basis der Fahrzeit erreicht hat – sie wartet auf die Sensorbestätigung.

### Positionsberechnung

Die Position wird relativ zu einer **Basislinie berechnet, die zu Beginn jeder Bewegung erfasst wird** – nicht immer ausgehend von 0% oder 100%. Das ist wichtig bei wiederholten Stop-Umkehr-Zyklen: Öffnen, Stoppen, erneut Öffnen setzt die Berechnung korrekt an der zuletzt bekannten Position fort, statt sie auf eine volle 0–100%-Fahrt zurückzusetzen.

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Entity-IDs haben deutsche Namen | Integration löschen, verwaiste Entities entfernen, neu hinzufügen |
| Aktor verliert Verbindung | Impulspause in den Grundeinstellungen erhöhen |
| Falscher Zustand nach Neustart | Tor einmal betätigen, damit ein Endschalter einen Sync auslöst |
| Stop reagiert nicht | In v1.0 behoben – keine blockierenden Service-Calls mehr |

## Homematic IP Verkabelungshinweise

Für die typische Homematic IP Konfiguration:
- **HmIP-PCBS** (Schaltaktor): Steuert den Garagentorantrieb per Impuls
- **HmIP-FCI6** (Kontakt-Interface): ch1 = Endschalter unten, ch2 = Endschalter oben
- **HmIP-STV** (Neigungssensor): Erkennt Torbewegung
- **Endschalter-Invertierung**: ch1 (unten) → **Invertieren JA** (OFF = geschlossen), ch2 (oben) → **Invertieren NEIN** (ON = offen)

## Lizenz

[MIT](LICENSE)
