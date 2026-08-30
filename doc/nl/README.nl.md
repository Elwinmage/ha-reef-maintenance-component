# Reef maintenance 🐙
> Onderdeel van het [**ReefTech Project Ecosystem**](https://elwinmage.github.io/reeftank/)
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

# Beschikbare talen: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) [<img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/fr/README.fr.md) [<img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/de/README.de.md) [<img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/es/README.es.md) [<img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/it/README.it.md) <img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/> [<img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pl/README.pl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pt/README.pt.md)

Home Assistant-integratie die schoonmaak- en slijtagetaken bijhoudt voor aquariumapparatuur die Home Assistant **niet kan uitlezen** — stromingspompen, opvoerpompen, eiwitafschuimers, reactoren, alles wat u met de hand onderhoudt.

Ze publiceert hetzelfde `reef_role`-entiteitencontract als de twee integraties voor verbonden apparaten, zodat haar taken in het onderhoudsoverzicht van de kaart verschijnen naast de verbonden apparatuur, zonder configuratie aan de kaartzijde.

<!-- ecosystem:start -->

## Verwante projecten

De ReefTech-projecten grijpen in elkaar: de integraties brengen uw apparatuur in Home Assistant, de kaart toont en bedient ze, en de back-up houdt alles draaiend tijdens een stroomuitval. Elk werkt ook op zichzelf.

<table>
  <tr>
    <th width="100px"></th>
    <th>Project</th>
    <th>Rol</th>
    <th>Werkt samen met</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Red Sea ReefBeat-apparaten, lokaal aangestuurd zonder cloud: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun en ReefWave.<br />blueprint met meldingen voor afwijkende modi, kalibraties en lage accu. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Aqua Medic-pompen via de Gizwits-cloud-API: EcoDrift- en SmartDrift-stromingspompen, DC Runner opvoer- en afschuimerpompen.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td><b>ha-reef-maintenance-component</b><br /><i>(deze repository)</i></td>
    <td>Schoonmaak- en slijtageopvolging voor apparatuur die Home Assistant niet kan uitlezen: stromingspompen, opvoerpompen, eiwitafschuimers, reactoren, alles wat u met de hand onderhoudt.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Interactieve grafische weergave van elk apparaat op uw dashboard, en de enige manier om geavanceerde schema's te bewerken. Leest de drie integraties via het gedeelde <code>reef_role</code>-contract, zonder configuratie aan de kaartzijde.</td>
    <td>alle drie de integraties</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-blueprints/main/icon.png" width="64" alt="ha-reef-blueprints" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-blueprints"><b>ha-reef-blueprints</b></a></td>
    <td>Meldings-blueprints voor het hele ecosysteem: achterstallig onderhoud gevonden via het <code>reef_role</code>-contract, en apparaten die onbereikbaar zijn geworden. Acht talen.</td>
    <td>alle drie de integraties</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Accuback-up bij stroomuitval. Een 24V LiFePO₄-pakket aangestuurd door een Raspberry Pi, met de pompsnelheid die geleidelijk zakt met de laadtoestand.</td>
    <td>zelfstandig, of samen met ha-reefbeat-component</td>
  </tr>
</table>

Alles staat samen gedocumenteerd op de [ReefTech-projectpagina](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## Met ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

Het onderhoudsoverzicht van [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) verzamelt alle taken van deze integratie naast die van de verbonden apparaten. Sorteer op apparaat of op vervaldatum, achterstallige eerst; druk op een regel en het werk is vastgelegd.

Aan de kaartzijde valt niets in te stellen: ze vindt de taken via het `reef_role`-attribuut, dus apparatuur die u hier toevoegt verschijnt daar bij de volgende verversing.

Achterstallige taken kunnen ook op uw telefoon komen: de blueprint [Reef maintenance watch](https://github.com/Elwinmage/ha-reef-blueprints) vindt ze via hetzelfde `reef_role`-attribuut en respecteert de meldingsschakelaars per taak.

[![Bekijk de video](https://img.youtube.com/vi/__A_DEFINIR__/0.jpg)](https://www.youtube.com/watch?v=__A_DEFINIR__)

## Hoe het werkt

Eén configuratie-item per **merk**, één apparaat per **apparatuur**, vier entiteiten per **taak**:

| Entiteit | Rol |
|---|---|
| Knop | Legt vast dat het werk gedaan is en draagt `days_left`, `overdue`, `interval_days`, `task_key`, `notify` als attributen |
| Getal | Interval, in de natuurlijke eenheid van de taak (dagen, weken of maanden) |
| Schakelaar | Dempt achterstandsmeldingen voor die taak |
| Datum | Zet de laatste onderhoudsbeurt met terugwerkende kracht |

De datumentiteit telt zwaarder dan ze lijkt: zonder haar begint elke taak op „nooit gedaan" op de dag dat u de apparatuur toevoegt, en vervallen ze drie maanden later allemaal dezelfde middag.

## Voorinstellingen

| Merk | Model | Taken |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | pomp, magneethouder, ontkalken, slijtdelen |
| Tunze | Turbelle nanostream | pomp, magneethouder, ontkalken, slijtdelen |
| Tunze | Silence / Silence PRO | aanzuigkorf, pomp, ontkalken, slijtdelen |
| Jebao | SLW / MLW / SCP / SOW | pomp, magneethouder, ontkalken, slijtdelen |
| Jebao | DCP / MDP | aanzuigkorf, pomp, ontkalken, slijtdelen |
| Generiek | DC-stromingspomp | pomp, magneethouder, ontkalken, slijtdelen |
| Generiek | DC-opvoerpomp | aanzuigkorf, pomp, ontkalken, slijtdelen |
| Generiek | Naaldrad-eiwitafschuimer | beker, venturi, naaldrad, ontkalken, slijtdelen |
| Generiek | Eigen apparatuur | geen — kies uit de bibliotheek of typ uw eigen taak |

De intervallen volgen de fabrikant waar die een getal publiceert (Tunze Turbelle: pomp en magneethouder elke 1–2 maanden; Tunze Silence: volledige reiniging minstens jaarlijks; Jebao DCP: maandelijks de rotor; Jebao SLW: maandelijks tot tweemaandelijks) en anders de rifpraktijk. Het zijn allemaal startpunten, per apparatuur aanpasbaar.

De taken komen uit een gedeelde bibliotheek van 17 items, vertaald in 8 talen. Een voorinstelling verwijst alleen naar bibliotheeksleutels en mag de intervalgrenzen overschrijven — daarom kost een nieuw merk meestal geen enkele nieuwe vertaalregel.

## Service

`reef_maintenance.reset` markeert een taak als gedaan vanuit een automatisering. Plak een NFC-tag bij de pomp, scan hem als u klaar bent, en de taak is afgetekend zonder een dashboard te openen.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Ontwikkeling

`scripts/gen_readme.py` genereert deze pagina en haar zeven vertalingen opnieuw, en `scripts/gen_translations.py` genereert `strings.json` en de 8 taalbestanden uit één brontabel — meer dan 800 teksten samengesteld uit één formulering per taak per taal. Draai ze na een wijziging aan de takenbibliotheek en commit het resultaat.

### Tests

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

De suite dekt het pakket volledig en de CI houdt dat zo. Het is nuttig te weten wat ze bewaakt, want het meeste is tijdens uitvoering onzichtbaar:

- **Taaksleutels en eenheden.** Een sleutel belandt in de `unique_id` van de entiteit en in de opslagsleutel, dus hernoemen wist de reset-geschiedenis. Een verkeerde eenheid verandert stilzwijgend wat een intervalschuif betekent.
- **`reef_role`.** Het attribuut waar ha-reef-card op zoekt. Verandert het voorvoegsel, dan blijft het onderhoudsoverzicht leeg zonder enige foutmelding.
- **Dagrekenkunde.** `compute_days_left` rondt in beide richtingen van nul af, en „nooit gereset" is `None` en niet achterstallig. Alle afnemers lezen die waarden.
- **Slug-botsingen.** Twee eigen taken waarvan de labels tot dezelfde slug leiden zouden één `unique_id` delen, en Home Assistant zou een van beide entiteitensets zonder melding laten vallen.
