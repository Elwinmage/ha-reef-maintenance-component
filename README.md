# Reef maintenance 🐙
> Part of the [**ReefTech Project Ecosystem**](https://elwinmage.github.io/reeftank/)
<p align="center">
  <img src="icon.png"  width="50%"/>
</p>

Home Assistant integration that tracks cleaning and wear tasks for aquarium
equipment Home Assistant **cannot talk to** — flow pumps, return pumps,
skimmers, media reactors, anything you clean by hand.

It publishes the same `reef_role` entity contract as
[ha-reefbeat-component](https://github.com/Elwinmage/ha-reefbeat-component) and
[ha-aquamedic-component](https://github.com/Elwinmage/ha-aquamedic-component),
so its tasks show up in the maintenance view of
[ha-reef-card](https://github.com/Elwinmage/ha-reef-card) next to the connected
gear, with no card-side configuration.

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
