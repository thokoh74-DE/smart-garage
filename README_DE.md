# Smart Garage

🇬🇧 [English Version](README.md)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/thokoh74-DE/smart-garage?style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/releases)
[![License](https://img.shields.io/github/license/thokoh74-DE/smart-garage?style=for-the-badge)](LICENSE)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hassfest.yml?label=Hassfest&style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/actions/workflows/hassfest.yml)
[![HACS Validation](https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hacs.yml?label=HACS&style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/actions/workflows/hacs.yml)

<p align="center">
  <img src="brand/logo.png" width="256" alt="Smart Garage Logo"/>
</p>

<p align="center">
  <strong>Eine Home Assistant Custom Integration für impulsgesteuerte Garagentore</strong><br>
  Öffnen · Schließen · Belüften · Überwachen
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="In HACS öffnen"/>
  </a>
</p>

---

## Überblick

Smart Garage steuert **impulsgesteuerte Garagentore** – Tore, bei denen ein einzelner Relaisimpuls den Zyklus *Auf → Stop → Zu → Stop → Auf* durchläuft. Die Integration bietet eine impulszählende State Machine, optionale feuchtigkeitsbasierte Lüftungssteuerung, Regen-Automatik und umfassende Diagnose.

Entwickelt für **Homematic IP** (HmIP-PCBS, HmIP-FCI6, HmIP-STV), kompatibel mit jedem impulsgesteuerten Garagentorantrieb.

## Funktionen

| Funktion | Beschreibung | Benötigte Sensoren |
|----------|-------------|-------------------|
| 🚪 **Torsteuerung** | Öffnen, Schließen, Stop mit genauer Zustandsverfolgung | Nur Steuerungsschalter |
| 📍 **Positionsverfolgung** | Live-Positionsberechnung während der Fahrt | – |
| 🔄 **Impulszählung** | Zustand aus Sync-Punkt + Impulszähler | Endschalter (empfohlen) |
| 💾 **Zustandsspeicherung** | Überlebt HA-Neustarts | – |
| 🌬️ **Lüftung** | Auto-Lüftung basierend auf abs. Feuchte + Taupunkt | Temp + Feuchte (innen + außen) |
| 🌧️ **Regen-Automatik** | Tor schließen bei Regen mit Verzögerung | Regensensor |
| 🛡️ **Sicherheit** | Erkennt versehentliches Öffnen bei Lüftung | Erschütterungssensor |
| 📡 **Aktor-Überwachung** | Warnung bei Erreichbarkeitsverlust | – |
| 🔘 **Externer Taster** | Erkennt physische Tasterbetätigung | Taster-Event |
| 📊 **Diagnose** | Vollständiger State-Dump per HA-Download | – |
| 🌍 **Zweisprachig** | Deutsch + Englisch | – |

## Voraussetzungen

| Komponente | Status | Zweck |
|-----------|--------|-------|
| Switch- oder Button-Entity | **Erforderlich** | Schaltet den Garagentorantrieb |
| Endschalter (unten) | Empfohlen | Bestätigt geschlossene Position |
| Endschalter (oben) | Empfohlen | Bestätigt geöffnete Position |
| Erschütterungssensor | Optional | Bewegungserkennung + Sicherheit |
| Externer Taster | Optional | Physische Tastererkennung |
| Temp + Feuchte (innen) | Optional | Aktiviert Lüftung |
| Temp + Feuchte (außen) | Optional | Aktiviert Lüftung |
| Regensensor | Optional | Aktiviert Regen-Automatik |
| Anwesenheits-Entity | Optional | Lüftung nur bei Anwesenheit |

> Funktionen passen sich an: ohne Klima-Sensoren → keine Lüftungs-Entities. Ohne Regensensor → kein Regen-Schalter. Die Integration funktioniert auch nur mit einem Steuerungsschalter.

## Installation

### HACS (empfohlen)

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration)

Oder: HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories → `https://github.com/thokoh74-DE/smart-garage` → Kategorie: Integration

### Manuell
`custom_components/smart_garage/` nach `config/custom_components/` kopieren und HA neustarten.

## Einrichtung

**Einstellungen → Geräte & Dienste → Integration hinzufügen → Smart Garage**

5-Schritte-Assistent:
1. **Grundeinstellungen** – Name (Gerätepräfix), Steuerungsschalter, Impulszeiten
2. **Sensoren** – Endschalter, Erschütterungssensor, externer Taster (alles optional)
3. **Sicherheit** – Versehentliches-Öffnen-Schutz, Benachrichtigungs-Service
4. **Lüftung** – Aktivieren/Deaktivieren
5. **Klima** – Temp-/Feuchte-Sensoren, Regensensor, Schwellwerte (alles optional)

Nach der Einrichtung: Zahnrad → **Menü mit 4 unabhängigen Bereichen**.

## Erzeugte Entities

| Entity | Typ | Erstellt wenn |
|--------|-----|-------------|
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
| Letzter Fahrbefehl / Befehl | `sensor` (Diagnose) | Immer |
| Endschalter unten/oben | `sensor` (Diagnose) | Wenn konfiguriert |
| Erschütterungssensor | `sensor` (Diagnose) | Wenn konfiguriert |
| Schaltaktor | `sensor` (Diagnose) | Immer |

## Funktionsweise

```
Ab GESCHLOSSEN:  Impuls → Öffnet → Impuls → Stop → Impuls → Schließt → Impuls → Stop → ...
Ab GEÖFFNET:     Impuls → Schließt → Impuls → Stop → Impuls → Öffnet → Impuls → Stop → ...
```

Die Integration speichert **Sync-Zustand** (letzte Endschalter-Bestätigung) + **Impulszähler**. Aktueller Zustand = `Sync + Impulse mod 4`. Endschalter setzen den Zähler auf 0.

Sind Endschalter konfiguriert, wird der Torzustand **nur** durch Sensoren bestätigt – nie durch Fahrzeitannahmen.

## Homematic IP Verkabelung

| Gerät | Funktion | Invertieren |
|-------|----------|------------|
| HmIP-FCI6 ch1 | Endschalter unten | **JA** (OFF = geschlossen) |
| HmIP-FCI6 ch2 | Endschalter oben | **NEIN** (ON = offen) |
| HmIP-PCBS | Steuerungsschalter | – |
| HmIP-STV | Erschütterungssensor | – |

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Entity-IDs in falscher Sprache | Integration löschen + neu hinzufügen |
| Aktor verliert Verbindung | Impulspause in Einstellungen erhöhen |
| Falscher Zustand nach Neustart | Tor einmal betätigen → Endschalter-Sync |
| Diagnosedaten | Geräteseite → ⋮ → Diagnose herunterladen |

## Quality Scale

Diese Integration zielt auf den [Home Assistant Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) Silver-Tier. Details in `quality_scale.yaml`.

## Mitwirken

Siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Lizenz

[MIT](LICENSE) © Thomas
