# Reef maintenance 🐙
> Part of the [**ReefTech Project Ecosystem**](https://elwinmage.github.io/reeftank/)
<p align="center">
  <img src="icon.png"  width="50%"/>
</p>

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/hacs)
[![IoT Class](https://img.shields.io/badge/IoT%20Class-Local%20Push-green?style=flat-square)](https://developers.home-assistant.io/docs/architecture_index/#branding)
[![GH-release](https://img.shields.io/github/v/release/Elwinmage/ha-reef-maintenance-component.svg?style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component/releases)
[![GH-last-commit](https://img.shields.io/github/last-commit/Elwinmage/ha-reef-maintenance-component.svg?style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GH-code-size](https://img.shields.io/github/languages/code-size/Elwinmage/ha-reef-maintenance-component.svg?color=red&style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component)
[![BuyMeCoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://paypal.me/Elwinmage)

Home Assistant integration that tracks cleaning and wear tasks for aquarium
equipment Home Assistant **cannot talk to** — flow pumps, return pumps,
skimmers, media reactors, anything you clean by hand.

It publishes the same `reef_role` entity contract as the two connected-device
integrations, so its tasks show up in the maintenance view of the card next to
the connected gear, with no card-side configuration.

<!-- ecosystem:start -->

## Related projects

The ReefTech projects fit together: the integrations bring your equipment into Home Assistant, the card displays and drives it, and the backup keeps it running through an outage. Each one also works on its own.

<table>
  <tr>
    <th width="200px"></th>
    <th>Project</th>
    <th>What it does</th>
    <th>Works with</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="200" alt="ha-reefbeat-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Red Sea ReefBeat devices, controlled locally with no cloud: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun and ReefWave.<br />Ships <b>ReefBeat watch</b>, an alert blueprint for overdue maintenance, abnormal modes, low battery and unreachable devices. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="200" alt="ha-aquamedic-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Aqua Medic pumps through the Gizwits cloud API: EcoDrift and SmartDrift wavemakers, DC Runner return and skimmer pumps.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="200" alt="ha-reef-maintenance-component" /></td>
    <td><b>ha-reef-maintenance-component</b><br /><i>(this repository)</i></td>
    <td>Cleaning and wear tracking for the equipment Home Assistant cannot talk to: flow pumps, return pumps, skimmers, media reactors, anything you service by hand.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="200" alt="ha-reef-card" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Interactive graphical view of each device on your dashboard, and the only way to edit advanced schedules. Reads the three integrations above through the shared <code>reef_role</code> contract, with no card-side configuration.</td>
    <td>all three integrations</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="200" alt="reefbeatEnergyBackup" /></td>
    <td><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Battery backup for power outages. A 24V LiFePO₄ pack driven by a Raspberry Pi, with pump speed degraded progressively according to the state of charge.</td>
    <td>standalone, or alongside ha-reefbeat-component</td>
  </tr>
</table>

All of them are documented together on the [ReefTech project page](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## How it works

One config entry per **brand**, one device per **equipment**, four entities per
**task**:

| Entity | Role |
|---|---|
| Button | Records that the job is done, and carries `days_left`, `overdue`, `interval_days`, `task_key`, `notify` as attributes |
| Number | Interval, in the task's natural unit (days, weeks or months) |
| Switch | Mutes overdue alerts for that task |
| Date | Backdates the last intervention |

The date entity matters more than it looks: without it every task starts from
"never done" the day you add the equipment, and they all fall due the same
afternoon three months later.

## Presets

| Brand | Model | Tasks |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | pump, magnet holder, descale, wear parts |
| Tunze | Turbelle nanostream | pump, magnet holder, descale, wear parts |
| Tunze | Silence / Silence PRO | strainer, pump, descale, wear parts |
| Jebao | SLW / MLW / SCP / SOW | pump, magnet holder, descale, wear parts |
| Jebao | DCP / MDP | strainer, pump, descale, wear parts |
| Generic | DC flow pump | pump, magnet holder, descale, wear parts |
| Generic | DC return pump | strainer, pump, descale, wear parts |
| Generic | Needle wheel skimmer | cup, venturi, needle wheel, descale, wear parts |
| Generic | Custom equipment | none — pick from the library or type your own |

Preset intervals follow the manufacturer whenever one publishes a figure
(Tunze Turbelle: pump and magnet holder every 1–2 months; Tunze Silence: full
clean at least yearly; Jebao DCP: monthly impeller cleaning; Jebao SLW:
monthly to bi-monthly) and reef keeping practice otherwise. All of them are
starting points you can change per equipment.

Tasks come from a shared library of 17 entries, translated in 8 languages.
A preset only references library keys and may override the interval bounds —
which is why adding a brand usually costs no new translation string.

## Service

`reef_maintenance.reset` marks a task done from an automation. Stick an NFC
tag next to the pump, scan it when you are done, and the task is acknowledged
without opening a dashboard.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Development

`scripts/gen_translations.py` regenerates `strings.json` and the 8 locale
files from a single source table — 800+ strings composed from one wording per
task per language. Run it after touching the task library, and commit the
result.
