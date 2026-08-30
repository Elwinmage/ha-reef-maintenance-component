# Reef maintenance 🐙
> Teil des [**ReefTech Project Ecosystem**](https://elwinmage.github.io/reeftank/)
<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-maintenance-component/raw/main/icon.png"  width="50%"/>
</p>

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/hacs)
[![IoT Class](https://img.shields.io/badge/IoT%20Class-Local%20Push-green?style=flat-square)](https://developers.home-assistant.io/docs/architecture_index/#branding)
[![GH-release](https://img.shields.io/github/v/release/Elwinmage/ha-reef-maintenance-component.svg?style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component/releases)
![Installations](https://img.shields.io/badge/dynamic/json?label=Active%20Installs&query=estimated&cacheSeconds=3600&url=https%3A%2F%2Fraw.githubusercontent.com%2FElwinmage%2Fha-reef-maintenance-component%2Fmain%2Fbadges%2Fstats.json&color=CE1126&logo=home-assistant)
[![Ruff Status](https://github.com/Elwinmage/ha-reef-maintenance-component/actions/workflows/main.yml/badge.svg)](https://github.com/Elwinmage/ha-reef-maintenance-component/actions/workflows/main.yml)
[![HA & HACS Validation](https://github.com/Elwinmage/ha-reef-maintenance-component/actions/workflows/hass_and_hacs.yml/badge.svg)](https://github.com/Elwinmage/ha-reef-maintenance-component/actions/workflows/hass_and_hacs.yml)
[![Coverage](https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/badges/coverage.svg)](https://app.codecov.io/gh/Elwinmage/ha-reef-maintenance-component)
[![GH-last-commit](https://img.shields.io/github/last-commit/Elwinmage/ha-reef-maintenance-component.svg?style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GH-code-size](https://img.shields.io/github/languages/code-size/Elwinmage/ha-reef-maintenance-component.svg?color=red&style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component)
[![BuyMeCoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://paypal.me/Elwinmage)

# Verfügbare Sprachen: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) [<img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/fr/README.fr.md) <img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/> [<img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/es/README.es.md) [<img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/it/README.it.md) [<img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/nl/README.nl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pl/README.pl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pt/README.pt.md)

Home-Assistant-Integration, die Reinigungs- und Verschleißaufgaben für Aquarientechnik verfolgt, die Home Assistant **nicht abfragen kann** — Strömungspumpen, Rückförderpumpen, Abschäumer, Reaktoren, alles was von Hand gewartet wird.

Sie veröffentlicht denselben `reef_role`-Entitätsvertrag wie die beiden Integrationen für verbundene Geräte, sodass ihre Aufgaben in der Wartungsansicht der Karte neben der verbundenen Technik erscheinen — ohne Konfiguration auf Kartenseite.

<!-- ecosystem:start -->

## Verwandte Projekte

Die ReefTech-Projekte greifen ineinander: die Integrationen bringen Ihre Geräte in Home Assistant, die Karte zeigt und steuert sie, und das Backup hält sie bei einem Stromausfall am Laufen. Jedes funktioniert auch für sich allein.

<table>
  <tr>
    <th width="100px"></th>
    <th>Projekt</th>
    <th>Funktion</th>
    <th>Arbeitet mit</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Red Sea ReefBeat-Geräte, lokal gesteuert ohne Cloud: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun und ReefWave.<br />Enthält <b>ReefBeat watch</b>, ein Alarm-Blueprint für überfällige Wartungen, abweichende Modi, niedrigen Akkustand und nicht erreichbare Geräte. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Aqua Medic-Pumpen über die Gizwits-Cloud-API: EcoDrift- und SmartDrift-Strömungspumpen, DC Runner Rückförder- und Abschäumerpumpen.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td><b>ha-reef-maintenance-component</b><br /><i>(dieses Repository)</i></td>
    <td>Reinigungs- und Verschleißverfolgung für Geräte, die Home Assistant nicht erreicht: Strömungspumpen, Rückförderpumpen, Abschäumer, Reaktoren, alles was von Hand gewartet wird.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Interaktive grafische Ansicht jedes Geräts auf Ihrem Dashboard und der einzige Weg, erweiterte Zeitpläne zu bearbeiten. Liest die drei Integrationen über den gemeinsamen <code>reef_role</code>-Vertrag, ohne Konfiguration auf Kartenseite.</td>
    <td>alle drei Integrationen</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Batterie-Backup bei Stromausfall. Ein 24V LiFePO₄-Pack, gesteuert von einem Raspberry Pi, mit schrittweiser Reduzierung der Pumpendrehzahl je nach Ladezustand.</td>
    <td>eigenständig oder zusammen mit ha-reefbeat-component</td>
  </tr>
</table>

Alle zusammen sind auf der [ReefTech-Projektseite](https://elwinmage.github.io/reeftank/) dokumentiert.

<!-- ecosystem:end -->

## Mit ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

Die Wartungsansicht von [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) sammelt alle Aufgaben dieser Integration neben denen der verbundenen Geräte. Sortieren Sie nach Gerät oder nach Fälligkeit, überfällige zuerst; ein Druck auf eine Zeile protokolliert die Arbeit.

Auf Kartenseite ist nichts einzurichten: sie findet die Aufgaben über das `reef_role`-Attribut, ein hier angelegtes Gerät erscheint dort also beim nächsten Aktualisieren.

[![Video ansehen](https://img.youtube.com/vi/__A_DEFINIR__/0.jpg)](https://www.youtube.com/watch?v=__A_DEFINIR__)

## Funktionsweise

Ein Konfigurationseintrag je **Marke**, ein Gerät je **Ausrüstung**, vier Entitäten je **Aufgabe**:

| Entität | Funktion |
|---|---|
| Schaltfläche | Protokolliert die erledigte Arbeit und trägt `days_left`, `overdue`, `interval_days`, `task_key`, `notify` als Attribute |
| Zahl | Intervall, in der natürlichen Einheit der Aufgabe (Tage, Wochen oder Monate) |
| Schalter | Schaltet Überfälligkeitshinweise für diese Aufgabe stumm |
| Datum | Trägt die letzte Wartung rückwirkend ein |

Die Datums-Entität ist wichtiger als sie aussieht: ohne sie startet jede Aufgabe am Tag der Anlage bei „nie gemacht", und alle werden drei Monate später am selben Nachmittag fällig.

## Voreinstellungen

| Marke | Modell | Aufgaben |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | Pumpe, Magnethalter, Entkalken, Verschleißteile |
| Tunze | Turbelle nanostream | Pumpe, Magnethalter, Entkalken, Verschleißteile |
| Tunze | Silence / Silence PRO | Ansaugkorb, Pumpe, Entkalken, Verschleißteile |
| Jebao | SLW / MLW / SCP / SOW | Pumpe, Magnethalter, Entkalken, Verschleißteile |
| Jebao | DCP / MDP | Ansaugkorb, Pumpe, Entkalken, Verschleißteile |
| Generisch | DC-Strömungspumpe | Pumpe, Magnethalter, Entkalken, Verschleißteile |
| Generisch | DC-Rückförderpumpe | Ansaugkorb, Pumpe, Entkalken, Verschleißteile |
| Generisch | Nadelrad-Abschäumer | Topf, Venturi, Nadelrad, Entkalken, Verschleißteile |
| Generisch | Eigene Ausrüstung | keine — aus der Bibliothek wählen oder eigene eintragen |

Die Intervalle folgen dem Hersteller, wo er eine Angabe veröffentlicht (Tunze Turbelle: Pumpe und Magnethalter alle 1–2 Monate; Tunze Silence: Komplettreinigung mindestens jährlich; Jebao DCP: Laufrad monatlich; Jebao SLW: monatlich bis zweimonatlich), sonst der Riffpraxis. Alle sind Ausgangswerte und je Ausrüstung änderbar.

Die Aufgaben stammen aus einer gemeinsamen Bibliothek mit 17 Einträgen, übersetzt in 8 Sprachen. Eine Voreinstellung verweist nur auf Bibliotheksschlüssel und darf die Intervallgrenzen überschreiben — deshalb kostet eine neue Marke meist keine neue Übersetzung.

## Dienst

`reef_maintenance.reset` markiert eine Aufgabe aus einer Automatisierung heraus als erledigt. Kleben Sie ein NFC-Tag an die Pumpe, scannen Sie es nach getaner Arbeit, und die Aufgabe ist quittiert, ohne ein Dashboard zu öffnen.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Entwicklung

`scripts/gen_readme.py` erzeugt diese Seite und ihre sieben Übersetzungen neu, `scripts/gen_translations.py` erzeugt `strings.json` und die 8 Sprachdateien aus einer einzigen Quelltabelle — über 800 Zeichenketten aus je einer Formulierung pro Aufgabe und Sprache. Nach Änderungen an der Aufgabenbibliothek ausführen und das Ergebnis committen.

### Tests

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

Die Suite deckt das Paket vollständig ab und die CI hält das so. Es lohnt zu wissen, was sie absichert, denn das meiste ist zur Laufzeit unsichtbar:

- **Aufgabenschlüssel und Einheiten.** Ein Schlüssel landet in der `unique_id` der Entität und im Speicherschlüssel; ihn umzubenennen verliert die Rücksetzhistorie. Eine falsche Einheit ändert stillschweigend die Bedeutung eines Intervallreglers.
- **`reef_role`.** Das Attribut, nach dem ha-reef-card sucht. Ändert sich sein Präfix, bleibt die Wartungsansicht leer — ohne jede Fehlermeldung.
- **Tagesarithmetik.** `compute_days_left` rundet in beide Richtungen von null weg, und „nie zurückgesetzt" ist `None` und nicht überfällig. Alle Verbraucher lesen diese Werte.
- **Slug-Kollisionen.** Zwei eigene Aufgaben, deren Bezeichnungen identisch slugifizieren, teilten sich eine `unique_id`, und Home Assistant verwürfe eines der beiden Entitätensets kommentarlos.
