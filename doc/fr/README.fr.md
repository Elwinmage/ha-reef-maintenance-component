# Reef maintenance 🐙
> Fait partie de l'[**écosystème ReefTech**](https://elwinmage.github.io/reeftank/)
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
[![GitHub Clones](https://img.shields.io/badge/dynamic/json?color=success&label=Clone&query=count&url=https://gist.githubusercontent.com/Elwinmage/37c1a33b8c2661fb88b060367900cf1c/raw/clone.json&logo=github)](https://github.com/MShawon/github-clone-count-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GH-code-size](https://img.shields.io/github/languages/code-size/Elwinmage/ha-reef-maintenance-component.svg?color=red&style=flat-square)](https://github.com/Elwinmage/ha-reef-maintenance-component)
[![BuyMeCoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://paypal.me/Elwinmage)

# Langues disponibles: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) <img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/> [<img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/de/README.de.md) [<img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/es/README.es.md) [<img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/it/README.it.md) [<img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/nl/README.nl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pl/README.pl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pt/README.pt.md)

Intégration Home Assistant qui suit les tâches de nettoyage et d'usure du matériel d'aquarium que Home Assistant **ne peut pas interroger** — pompes de brassage, pompes de remontée, écumeurs, réacteurs, tout ce que vous entretenez à la main.

Elle publie le même contrat d'entités `reef_role` que les deux intégrations d'appareils connectés : ses tâches apparaissent donc dans la vue maintenance de la carte, à côté du matériel connecté, sans aucune configuration côté carte.

<!-- ecosystem:start -->

## Projets liés

Les projets ReefTech s'articulent entre eux : les intégrations font entrer votre matériel dans Home Assistant, la carte l'affiche et le pilote, et le secours le maintient en marche pendant une coupure. Chacun fonctionne aussi seul.

<table>
  <tr>
    <th width="100px"></th>
    <th>Projet</th>
    <th>Rôle</th>
    <th>Fonctionne avec</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td>🐠<br /><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Appareils Red Sea ReefBeat, pilotés en local sans cloud : ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun et ReefWave.<br />blueprint d'alertes pour les modes anormaux, les calibrations et les batteries faibles. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td>🌊<br /><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Pompes Aqua Medic via l'API cloud Gizwits : brasseurs EcoDrift et SmartDrift, pompes DC Runner de remontée et d'écumeur.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td>🐙<br /><b>ha-reef-maintenance-component</b><br /><i>(ce dépôt)</i></td>
    <td>Suivi du nettoyage et de l'usure du matériel que Home Assistant ne peut pas interroger : pompes de brassage, pompes de remontée, écumeurs, réacteurs, tout ce que vous entretenez à la main.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td>🪸<br /><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Vue graphique interactive de chaque appareil sur votre tableau de bord, et seul moyen d'éditer les programmes avancés. Lit les trois intégrations ci-dessus via le contrat <code>reef_role</code> commun, sans configuration côté carte.</td>
    <td>les trois intégrations</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-blueprints/main/icon.png" width="64" alt="ha-reef-blueprints" /></td>
    <td>🐬<br /><a href="https://github.com/Elwinmage/ha-reef-blueprints"><b>ha-reef-blueprints</b></a></td>
    <td>Blueprints de notification communs à tout l'écosystème : entretiens en retard trouvés via le contrat <code>reef_role</code>, et appareils devenus injoignables. Huit langues.</td>
    <td>les trois intégrations</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td>⚡<br /><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Secours sur batterie en cas de coupure. Pack 24V LiFePO₄ piloté par un Raspberry Pi, avec dégradation progressive de la vitesse des pompes selon l'état de charge.</td>
    <td>seul, ou avec ha-reefbeat-component</td>
  </tr>
</table>

L'ensemble est documenté sur la [page du projet ReefTech](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## Avec ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

La vue maintenance de [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) rassemble toutes les tâches de cette intégration à côté de celles des appareils connectés. Triez par équipement ou par échéance, les dépassées en tête ; une pression sur une ligne enregistre l'intervention.

Rien à régler côté carte : elle trouve les tâches par l'attribut `reef_role`, donc un équipement ajouté ici apparaît là au rafraîchissement suivant.

Les tâches en retard peuvent aussi arriver sur votre téléphone : le blueprint [Reef maintenance watch](https://github.com/Elwinmage/ha-reef-blueprints) les trouve par ce même attribut `reef_role` et respecte les interrupteurs de notification par tâche.

[![Regarder la vidéo](https://img.youtube.com/vi/Ko46fHonOP4/0.jpg)](https://www.youtube.com/watch?v=Ko46fHonOP4)

## Installation

### Installation directe

Cliquez ici pour ouvrir directement le dépôt dans HACS et cliquez sur « Télécharger » : [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Elwinmage&repository=ha-reef-maintenance-component&category=integration)

### Recherche dans HACS

Ou cherchez « reef-maintenance » dans HACS.

## Fonctionnement

Une entrée de configuration par **marque**, un appareil par **équipement**, quatre entités par **tâche** :

| Entité | Rôle |
|---|---|
| Bouton | Enregistre l'intervention, et porte `days_left`, `overdue`, `interval_days`, `task_key`, `notify` en attributs |
| Nombre | Intervalle, dans l'unité naturelle de la tâche (jours, semaines ou mois) |
| Interrupteur | Coupe les alertes de dépassement pour cette tâche |
| Date | Antidate la dernière intervention |

L'entité date compte plus qu'il n'y paraît : sans elle, chaque tâche démarre à « jamais faite » le jour où vous ajoutez l'équipement, et elles arrivent toutes à échéance le même après-midi trois mois plus tard.

## Préréglages

| Marque | Modèle | Tâches |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | pompe, support magnétique, détartrage, pièces d'usure |
| Tunze | Turbelle nanostream | pompe, support magnétique, détartrage, pièces d'usure |
| Tunze | Silence / Silence PRO | crépine, pompe, détartrage, pièces d'usure |
| Jebao | SLW / MLW / SCP / SOW | pompe, support magnétique, détartrage, pièces d'usure |
| Jebao | DCP / MDP | crépine, pompe, détartrage, pièces d'usure |
| Générique | Pompe de brassage DC | pompe, support magnétique, détartrage, pièces d'usure |
| Générique | Pompe de remontée DC | crépine, pompe, détartrage, pièces d'usure |
| Générique | Écumeur à rotor à aiguilles | godet, venturi, rotor à aiguilles, détartrage, pièces d'usure |
| Générique | Équipement personnalisé | aucune — choisissez dans la bibliothèque ou saisissez la vôtre |

Les intervalles des préréglages suivent le fabricant lorsqu'il publie un chiffre (Tunze Turbelle : pompe et support magnétique tous les 1 à 2 mois ; Tunze Silence : nettoyage complet au moins annuel ; Jebao DCP : rotor mensuel ; Jebao SLW : mensuel à bimestriel) et la pratique récifale sinon. Ce ne sont que des points de départ, modifiables équipement par équipement.

Les tâches viennent d'une bibliothèque commune de 17 entrées, traduite en 8 langues. Un préréglage ne fait que référencer des clés de la bibliothèque et peut redéfinir les bornes d'intervalle — c'est pourquoi ajouter une marque ne coûte en général aucune nouvelle chaîne de traduction.

## Service

`reef_maintenance.reset` marque une tâche comme faite depuis une automatisation. Collez un tag NFC près de la pompe, scannez-le une fois le travail terminé, et la tâche est acquittée sans ouvrir de tableau de bord.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Développement

`scripts/gen_readme.py` régénère cette page et ses sept traductions, et `scripts/gen_translations.py` régénère `strings.json` et les 8 fichiers de locale depuis une table unique — plus de 800 chaînes composées à partir d'une formulation par tâche et par langue. Lancez-les après avoir touché à la bibliothèque de tâches, et commitez le résultat.

### Tests

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

La suite couvre entièrement le paquet et la CI l'y maintient. Il vaut la peine de savoir ce qu'elle protège, car l'essentiel est invisible à l'exécution :

- **Clés et unités des tâches.** Une clé se retrouve dans l'`unique_id` de l'entité et dans la clé de stockage : la renommer fait perdre l'historique des remises à zéro. Une mauvaise unité change silencieusement le sens d'un curseur d'intervalle.
- **`reef_role`.** L'attribut que ha-reef-card recherche. Si son préfixe change, la vue maintenance se vide sans la moindre erreur.
- **Arithmétique des jours.** `compute_days_left` arrondit à l'opposé de zéro dans les deux sens, et « jamais remis à zéro » vaut `None` et non « dépassé ». Tous les consommateurs lisent ces valeurs.
- **Collisions de slugs.** Deux tâches personnalisées dont les libellés se slugifient à l'identique partageraient un `unique_id`, et Home Assistant supprimerait l'un des deux jeux d'entités sans rien dire.
