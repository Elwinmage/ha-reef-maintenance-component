#!/usr/bin/env python3
"""Generate README.md and its seven translations from one source.

Usage, from the repository root::

    python3 scripts/gen_readme.py
    python3 ../reeftank/scripts/gen_ecosystem.py   # run from the parent dir

Order matters: this script writes the whole file, so it must run *before*
gen_ecosystem.py, which inserts the shared "Related projects" block before the
`anchor` heading of each language.

Edit T below, never the generated files. Eight hand-maintained copies of the
same page is exactly how they end up disagreeing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = "https://github.com/Elwinmage/ha-reef-maintenance-component"
CARD = "https://github.com/Elwinmage/ha-reef-card"
BLUEPRINTS = "https://github.com/Elwinmage/ha-reef-blueprints"
SITE = "https://elwinmage.github.io/reeftank/"
OVERVIEW = f"{CARD}/raw/main/doc/img/maintenance/overview.png"

# Replace with the real id once the video is up. Left as a token on purpose:
# a plausible-looking placeholder would ship unnoticed, this one cannot.
VIDEO_ID = "Ko46fHonOP4"

# Flag, language code, and the path the flag links to. English is the root
# README; the rest live under doc/<lang>/.
LANGS = [
    ("gb", "en", "README.md"),
    ("fr", "fr", "doc/fr/README.fr.md"),
    ("de", "de", "doc/de/README.de.md"),
    ("es", "es", "doc/es/README.es.md"),
    ("it", "it", "doc/it/README.it.md"),
    ("nl", "nl", "doc/nl/README.nl.md"),
    ("pl", "pl", "doc/pl/README.pl.md"),
    ("pt", "pt", "doc/pt/README.pt.md"),
]

# Clone counter, kept in a gist by the github-clone-count-badge workflow: the
# GitHub API only serves the last 14 days, so the count has to live outside the
# repository. One gist per repository — pointing this at another repo's gist
# would show that repo's count. Left empty until the gist exists, and the badge
# is then simply not emitted rather than rendering broken.
CLONE_GIST_ID = "37c1a33b8c2661fb88b060367900cf1c"

CLONE_BADGE = (
    (
        "[![GitHub Clones](https://img.shields.io/badge/dynamic/json"
        "?color=success&label=Clone&query=count"
        "&url=https://gist.githubusercontent.com/Elwinmage/"
        f"{CLONE_GIST_ID}/raw/clone.json&logo=github)]"
        "(https://github.com/MShawon/github-clone-count-badge)\n"
    )
    if CLONE_GIST_ID
    else ""
)

BADGES = f"""[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/hacs)
[![IoT Class](https://img.shields.io/badge/IoT%20Class-Local%20Push-green?style=flat-square)](https://developers.home-assistant.io/docs/architecture_index/#branding)
[![GH-release](https://img.shields.io/github/v/release/Elwinmage/ha-reef-maintenance-component.svg?style=flat-square)]({REPO}/releases)
![Installations](https://img.shields.io/badge/dynamic/json?label=Active%20Installs&query=estimated&cacheSeconds=3600&url=https%3A%2F%2Fraw.githubusercontent.com%2FElwinmage%2Fha-reef-maintenance-component%2Fmain%2Fbadges%2Fstats.json&color=CE1126&logo=home-assistant)
[![Ruff Status]({REPO}/actions/workflows/main.yml/badge.svg)]({REPO}/actions/workflows/main.yml)
[![HA & HACS Validation]({REPO}/actions/workflows/hass_and_hacs.yml/badge.svg)]({REPO}/actions/workflows/hass_and_hacs.yml)
[![Coverage](https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/badges/coverage.svg)](https://app.codecov.io/gh/Elwinmage/ha-reef-maintenance-component)
[![GH-last-commit](https://img.shields.io/github/last-commit/Elwinmage/ha-reef-maintenance-component.svg?style=flat-square)]({REPO}/commits/main)
{CLONE_BADGE}[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GH-code-size](https://img.shields.io/github/languages/code-size/Elwinmage/ha-reef-maintenance-component.svg?color=red&style=flat-square)]({REPO})
[![BuyMeCoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://paypal.me/Elwinmage)"""

SERVICE_YAML = """```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```"""

TESTS_SH = """```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \\
       --cov-report=term-missing
```"""

HACS_BADGE = (
    "[![Open your Home Assistant instance and open a repository inside the "
    "Home Assistant Community Store.]"
    "(https://my.home-assistant.io/badges/hacs_repository.svg)]"
    "(https://my.home-assistant.io/redirect/hacs_repository/"
    "?owner=Elwinmage&repository=ha-reef-maintenance-component"
    "&category=integration)"
)

T: dict[str, dict[str, str]] = {
    "en": {
        "ecosystem_line": f"Part of the [**ReefTech Project Ecosystem**]({SITE})",
        "languages": "Supported Languages",
        "intro": (
            "Home Assistant integration that tracks cleaning and wear tasks for "
            "aquarium equipment Home Assistant **cannot talk to** — flow pumps, "
            "return pumps, skimmers, media reactors, anything you clean by hand."
        ),
        "contract": (
            "It publishes the same `reef_role` entity contract as the two "
            "connected-device integrations, so its tasks show up in the "
            "maintenance view of the card next to the connected gear, with no "
            "card-side configuration."
        ),
        "watch": "Watch the video",
        "card_title": "With ha-reef-card",
        "card_body": (
            f"The maintenance view of [ha-reef-card]({CARD}) gathers every task "
            "from this integration alongside those of the connected devices. "
            "Sort by equipment or by due date, overdue first; press a row and "
            "the job is recorded."
        ),
        "card_note": (
            "Nothing to set up on the card side: it finds the tasks through the "
            "`reef_role` attribute, so an equipment added here appears there on "
            "the next refresh."
        ),
        "notify_link": (
            f"Overdue tasks can also reach your phone: the [Reef maintenance watch]({BLUEPRINTS}) blueprint finds them through the same `reef_role` attribute and honours the per-task notification switches."
        ),
        "install_title": "Installation",
        "install_direct_title": "Direct installation",
        "install_direct_body": 'Click here to open the repository directly in HACS and click "Download":',
        "install_search_title": "Search in HACS",
        "install_search_body": 'Or search for "reef-maintenance" in HACS.',
        "how_title": "How it works",
        "how_body": (
            "One config entry per **brand**, one device per **equipment**, four "
            "entities per **task**:"
        ),
        "h_entity": "Entity",
        "h_role": "Role",
        "e_button": "Button",
        "r_button": (
            "Records that the job is done, and carries `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` as attributes"
        ),
        "e_number": "Number",
        "r_number": "Interval, in the task's natural unit (days, weeks or months)",
        "e_switch": "Switch",
        "r_switch": "Mutes overdue alerts for that task",
        "e_date": "Date",
        "r_date": "Backdates the last intervention",
        "how_note": (
            "The date entity matters more than it looks: without it every task "
            'starts from "never done" the day you add the equipment, and they '
            "all fall due the same afternoon three months later."
        ),
        "presets_title": "Presets",
        "h_brand": "Brand",
        "h_model": "Model",
        "h_tasks": "Tasks",
        "generic": "Generic",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "DC flow pump",
        "m_return": "DC return pump",
        "m_skimmer": "Needle wheel skimmer",
        "m_routine": "Routine aquarium maintenance",
        "m_custom": "Custom equipment",
        "t_pump": "pump, magnet holder, descale, wear parts",
        "t_strainer": "strainer, pump, descale, wear parts",
        "t_skimmer": "cup, venturi, needle wheel, descale, wear parts",
        "t_routine": "water change, glass, ICP test, RO/DI filters, sump, sand",
        "t_none": "none — pick from the library or type your own",
        "presets_note": (
            "Preset intervals follow the manufacturer whenever one publishes a "
            "figure (Tunze Turbelle: pump and magnet holder every 1–2 months; "
            "Tunze Silence: full clean at least yearly; Jebao DCP: monthly "
            "impeller cleaning; Jebao SLW: monthly to bi-monthly) and reef "
            "keeping practice otherwise. All of them are starting points you can "
            "change per equipment."
        ),
        "presets_lib": (
            "Tasks come from a shared library of 21 entries, translated in 8 "
            "languages. A preset only references library keys and may override "
            "the interval bounds — which is why adding a brand usually costs no "
            "new translation string."
        ),
        "service_title": "Service",
        "service_body": (
            "`reef_maintenance.reset` marks a task done from an automation. "
            "Stick an NFC tag next to the pump, scan it when you are done, and "
            "the task is acknowledged without opening a dashboard."
        ),
        "dev_title": "Development",
        "dev_body": (
            "`scripts/gen_readme.py` regenerates this page and its seven "
            "translations, and `scripts/gen_translations.py` regenerates "
            "`strings.json` and the 8 locale files from a single source table — "
            "800+ strings composed from one wording per task per language. Run "
            "them after touching the task library, and commit the result."
        ),
        "tests_title": "Tests",
        "tests_body": (
            "The suite covers the package fully and CI keeps it that way. It is "
            "worth knowing what it is guarding, because most of it is invisible "
            "at runtime:"
        ),
        "tests_1": (
            "**Task keys and units.** A key lands in the entity `unique_id` and "
            "in the storage key, so renaming one loses the user's reset history. "
            "A wrong unit silently changes what an interval slider means."
        ),
        "tests_2": (
            "**`reef_role`.** The attribute ha-reef-card scans for. If its "
            "prefix changes, the maintenance view goes empty with no error "
            "anywhere."
        ),
        "tests_3": (
            "**Day arithmetic.** `compute_days_left` rounds away from zero in "
            'both directions, and "never reset" is `None` rather than overdue. '
            "Every consumer reads those values."
        ),
        "tests_4": (
            "**Slug collisions.** Two custom tasks whose labels slugify "
            "identically would share a `unique_id`, and Home Assistant would "
            "drop one of the two entity sets without saying so."
        ),
    },
    "fr": {
        "ecosystem_line": f"Fait partie de l'[**écosystème ReefTech**]({SITE})",
        "languages": "Langues disponibles",
        "intro": (
            "Intégration Home Assistant qui suit les tâches de nettoyage et "
            "d'usure du matériel d'aquarium que Home Assistant **ne peut pas "
            "interroger** — pompes de brassage, pompes de remontée, écumeurs, "
            "réacteurs, tout ce que vous entretenez à la main."
        ),
        "contract": (
            "Elle publie le même contrat d'entités `reef_role` que les deux "
            "intégrations d'appareils connectés : ses tâches apparaissent donc "
            "dans la vue maintenance de la carte, à côté du matériel connecté, "
            "sans aucune configuration côté carte."
        ),
        "watch": "Regarder la vidéo",
        "card_title": "Avec ha-reef-card",
        "card_body": (
            f"La vue maintenance de [ha-reef-card]({CARD}) rassemble toutes les "
            "tâches de cette intégration à côté de celles des appareils "
            "connectés. Triez par équipement ou par échéance, les dépassées en "
            "tête ; une pression sur une ligne enregistre l'intervention."
        ),
        "card_note": (
            "Rien à régler côté carte : elle trouve les tâches par l'attribut "
            "`reef_role`, donc un équipement ajouté ici apparaît là au "
            "rafraîchissement suivant."
        ),
        "notify_link": (
            f"Les tâches en retard peuvent aussi arriver sur votre téléphone : le blueprint [Reef maintenance watch]({BLUEPRINTS}) les trouve par ce même attribut `reef_role` et respecte les interrupteurs de notification par tâche."
        ),
        "install_title": "Installation",
        "install_direct_title": "Installation directe",
        "install_direct_body": "Cliquez ici pour ouvrir directement le dépôt dans HACS et cliquez sur \u00ab Télécharger \u00bb :",
        "install_search_title": "Recherche dans HACS",
        "install_search_body": "Ou cherchez \u00ab reef-maintenance \u00bb dans HACS.",
        "how_title": "Fonctionnement",
        "how_body": (
            "Une entrée de configuration par **marque**, un appareil par "
            "**équipement**, quatre entités par **tâche** :"
        ),
        "h_entity": "Entité",
        "h_role": "Rôle",
        "e_button": "Bouton",
        "r_button": (
            "Enregistre l'intervention, et porte `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` en attributs"
        ),
        "e_number": "Nombre",
        "r_number": (
            "Intervalle, dans l'unité naturelle de la tâche (jours, semaines ou mois)"
        ),
        "e_switch": "Interrupteur",
        "r_switch": "Coupe les alertes de dépassement pour cette tâche",
        "e_date": "Date",
        "r_date": "Antidate la dernière intervention",
        "how_note": (
            "L'entité date compte plus qu'il n'y paraît : sans elle, chaque "
            "tâche démarre à « jamais faite » le jour où vous ajoutez "
            "l'équipement, et elles arrivent toutes à échéance le même "
            "après-midi trois mois plus tard."
        ),
        "presets_title": "Préréglages",
        "h_brand": "Marque",
        "h_model": "Modèle",
        "h_tasks": "Tâches",
        "generic": "Générique",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "Pompe de brassage DC",
        "m_return": "Pompe de remontée DC",
        "m_skimmer": "Écumeur à rotor à aiguilles",
        "m_routine": "Entretien courant de l'aquarium",
        "m_custom": "Équipement personnalisé",
        "t_pump": "pompe, support magnétique, détartrage, pièces d'usure",
        "t_strainer": "crépine, pompe, détartrage, pièces d'usure",
        "t_skimmer": "godet, venturi, rotor à aiguilles, détartrage, pièces d'usure",
        "t_routine": "changement d'eau, vitres, test ICP, filtres RO/DI, décanteur, sable",
        "t_none": "aucune — choisissez dans la bibliothèque ou saisissez la vôtre",
        "presets_note": (
            "Les intervalles des préréglages suivent le fabricant lorsqu'il "
            "publie un chiffre (Tunze Turbelle : pompe et support magnétique "
            "tous les 1 à 2 mois ; Tunze Silence : nettoyage complet au moins "
            "annuel ; Jebao DCP : rotor mensuel ; Jebao SLW : mensuel à "
            "bimestriel) et la pratique récifale sinon. Ce ne sont que des "
            "points de départ, modifiables équipement par équipement."
        ),
        "presets_lib": (
            "Les tâches viennent d'une bibliothèque commune de 21 entrées, "
            "traduite en 8 langues. Un préréglage ne fait que référencer des "
            "clés de la bibliothèque et peut redéfinir les bornes d'intervalle — "
            "c'est pourquoi ajouter une marque ne coûte en général aucune "
            "nouvelle chaîne de traduction."
        ),
        "service_title": "Service",
        "service_body": (
            "`reef_maintenance.reset` marque une tâche comme faite depuis une "
            "automatisation. Collez un tag NFC près de la pompe, scannez-le une "
            "fois le travail terminé, et la tâche est acquittée sans ouvrir de "
            "tableau de bord."
        ),
        "dev_title": "Développement",
        "dev_body": (
            "`scripts/gen_readme.py` régénère cette page et ses sept "
            "traductions, et `scripts/gen_translations.py` régénère "
            "`strings.json` et les 8 fichiers de locale depuis une table unique "
            "— plus de 800 chaînes composées à partir d'une formulation par "
            "tâche et par langue. Lancez-les après avoir touché à la "
            "bibliothèque de tâches, et commitez le résultat."
        ),
        "tests_title": "Tests",
        "tests_body": (
            "La suite couvre entièrement le paquet et la CI l'y maintient. Il "
            "vaut la peine de savoir ce qu'elle protège, car l'essentiel est "
            "invisible à l'exécution :"
        ),
        "tests_1": (
            "**Clés et unités des tâches.** Une clé se retrouve dans "
            "l'`unique_id` de l'entité et dans la clé de stockage : la renommer "
            "fait perdre l'historique des remises à zéro. Une mauvaise unité "
            "change silencieusement le sens d'un curseur d'intervalle."
        ),
        "tests_2": (
            "**`reef_role`.** L'attribut que ha-reef-card recherche. Si son "
            "préfixe change, la vue maintenance se vide sans la moindre erreur."
        ),
        "tests_3": (
            "**Arithmétique des jours.** `compute_days_left` arrondit à "
            "l'opposé de zéro dans les deux sens, et « jamais remis à zéro » "
            "vaut `None` et non « dépassé ». Tous les consommateurs lisent ces "
            "valeurs."
        ),
        "tests_4": (
            "**Collisions de slugs.** Deux tâches personnalisées dont les "
            "libellés se slugifient à l'identique partageraient un `unique_id`, "
            "et Home Assistant supprimerait l'un des deux jeux d'entités sans "
            "rien dire."
        ),
    },
    "de": {
        "ecosystem_line": f"Teil des [**ReefTech Project Ecosystem**]({SITE})",
        "languages": "Verfügbare Sprachen",
        "intro": (
            "Home-Assistant-Integration, die Reinigungs- und Verschleißaufgaben "
            "für Aquarientechnik verfolgt, die Home Assistant **nicht abfragen "
            "kann** — Strömungspumpen, Rückförderpumpen, Abschäumer, Reaktoren, "
            "alles was von Hand gewartet wird."
        ),
        "contract": (
            "Sie veröffentlicht denselben `reef_role`-Entitätsvertrag wie die "
            "beiden Integrationen für verbundene Geräte, sodass ihre Aufgaben in "
            "der Wartungsansicht der Karte neben der verbundenen Technik "
            "erscheinen — ohne Konfiguration auf Kartenseite."
        ),
        "watch": "Video ansehen",
        "card_title": "Mit ha-reef-card",
        "card_body": (
            f"Die Wartungsansicht von [ha-reef-card]({CARD}) sammelt alle "
            "Aufgaben dieser Integration neben denen der verbundenen Geräte. "
            "Sortieren Sie nach Gerät oder nach Fälligkeit, überfällige zuerst; "
            "ein Druck auf eine Zeile protokolliert die Arbeit."
        ),
        "card_note": (
            "Auf Kartenseite ist nichts einzurichten: sie findet die Aufgaben "
            "über das `reef_role`-Attribut, ein hier angelegtes Gerät erscheint "
            "dort also beim nächsten Aktualisieren."
        ),
        "notify_link": (
            f"Überfällige Aufgaben können auch auf Ihr Telefon: der Blueprint [Reef maintenance watch]({BLUEPRINTS}) findet sie über dasselbe `reef_role`-Attribut und beachtet die Benachrichtigungsschalter je Aufgabe."
        ),
        "install_title": "Installation",
        "install_direct_title": "Direkte Installation",
        "install_direct_body": "Klicken Sie hier, um das Repository direkt in HACS zu öffnen, und klicken Sie auf \u00abHerunterladen\u00bb:",
        "install_search_title": "Suche in HACS",
        "install_search_body": "Oder suchen Sie nach \u00abreef-maintenance\u00bb in HACS.",
        "how_title": "Funktionsweise",
        "how_body": (
            "Ein Konfigurationseintrag je **Marke**, ein Gerät je "
            "**Ausrüstung**, vier Entitäten je **Aufgabe**:"
        ),
        "h_entity": "Entität",
        "h_role": "Funktion",
        "e_button": "Schaltfläche",
        "r_button": (
            "Protokolliert die erledigte Arbeit und trägt `days_left`, "
            "`overdue`, `interval_days`, `task_key`, `notify` als Attribute"
        ),
        "e_number": "Zahl",
        "r_number": (
            "Intervall, in der natürlichen Einheit der Aufgabe (Tage, Wochen "
            "oder Monate)"
        ),
        "e_switch": "Schalter",
        "r_switch": "Schaltet Überfälligkeitshinweise für diese Aufgabe stumm",
        "e_date": "Datum",
        "r_date": "Trägt die letzte Wartung rückwirkend ein",
        "how_note": (
            "Die Datums-Entität ist wichtiger als sie aussieht: ohne sie startet "
            'jede Aufgabe am Tag der Anlage bei „nie gemacht", und alle werden '
            "drei Monate später am selben Nachmittag fällig."
        ),
        "presets_title": "Voreinstellungen",
        "h_brand": "Marke",
        "h_model": "Modell",
        "h_tasks": "Aufgaben",
        "generic": "Generisch",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "DC-Strömungspumpe",
        "m_return": "DC-Rückförderpumpe",
        "m_skimmer": "Nadelrad-Abschäumer",
        "m_routine": "Routinemäßige Aquarienpflege",
        "m_custom": "Eigene Ausrüstung",
        "t_pump": "Pumpe, Magnethalter, Entkalken, Verschleißteile",
        "t_strainer": "Ansaugkorb, Pumpe, Entkalken, Verschleißteile",
        "t_skimmer": "Topf, Venturi, Nadelrad, Entkalken, Verschleißteile",
        "t_routine": "Wasserwechsel, Scheiben, ICP-Test, RO/DI-Filter, Technikbecken, Sand",
        "t_none": "keine — aus der Bibliothek wählen oder eigene eintragen",
        "presets_note": (
            "Die Intervalle folgen dem Hersteller, wo er eine Angabe "
            "veröffentlicht (Tunze Turbelle: Pumpe und Magnethalter alle 1–2 "
            "Monate; Tunze Silence: Komplettreinigung mindestens jährlich; "
            "Jebao DCP: Laufrad monatlich; Jebao SLW: monatlich bis "
            "zweimonatlich), sonst der Riffpraxis. Alle sind Ausgangswerte und "
            "je Ausrüstung änderbar."
        ),
        "presets_lib": (
            "Die Aufgaben stammen aus einer gemeinsamen Bibliothek mit 21 "
            "Einträgen, übersetzt in 8 Sprachen. Eine Voreinstellung verweist "
            "nur auf Bibliotheksschlüssel und darf die Intervallgrenzen "
            "überschreiben — deshalb kostet eine neue Marke meist keine neue "
            "Übersetzung."
        ),
        "service_title": "Dienst",
        "service_body": (
            "`reef_maintenance.reset` markiert eine Aufgabe aus einer "
            "Automatisierung heraus als erledigt. Kleben Sie ein NFC-Tag an die "
            "Pumpe, scannen Sie es nach getaner Arbeit, und die Aufgabe ist "
            "quittiert, ohne ein Dashboard zu öffnen."
        ),
        "dev_title": "Entwicklung",
        "dev_body": (
            "`scripts/gen_readme.py` erzeugt diese Seite und ihre sieben "
            "Übersetzungen neu, `scripts/gen_translations.py` erzeugt "
            "`strings.json` und die 8 Sprachdateien aus einer einzigen "
            "Quelltabelle — über 800 Zeichenketten aus je einer Formulierung pro "
            "Aufgabe und Sprache. Nach Änderungen an der Aufgabenbibliothek "
            "ausführen und das Ergebnis committen."
        ),
        "tests_title": "Tests",
        "tests_body": (
            "Die Suite deckt das Paket vollständig ab und die CI hält das so. Es "
            "lohnt zu wissen, was sie absichert, denn das meiste ist zur "
            "Laufzeit unsichtbar:"
        ),
        "tests_1": (
            "**Aufgabenschlüssel und Einheiten.** Ein Schlüssel landet in der "
            "`unique_id` der Entität und im Speicherschlüssel; ihn umzubenennen "
            "verliert die Rücksetzhistorie. Eine falsche Einheit ändert "
            "stillschweigend die Bedeutung eines Intervallreglers."
        ),
        "tests_2": (
            "**`reef_role`.** Das Attribut, nach dem ha-reef-card sucht. Ändert "
            "sich sein Präfix, bleibt die Wartungsansicht leer — ohne jede "
            "Fehlermeldung."
        ),
        "tests_3": (
            "**Tagesarithmetik.** `compute_days_left` rundet in beide "
            'Richtungen von null weg, und „nie zurückgesetzt" ist `None` und '
            "nicht überfällig. Alle Verbraucher lesen diese Werte."
        ),
        "tests_4": (
            "**Slug-Kollisionen.** Zwei eigene Aufgaben, deren Bezeichnungen "
            "identisch slugifizieren, teilten sich eine `unique_id`, und Home "
            "Assistant verwürfe eines der beiden Entitätensets kommentarlos."
        ),
    },
    "es": {
        "ecosystem_line": f"Parte del [**ecosistema ReefTech**]({SITE})",
        "languages": "Idiomas disponibles",
        "intro": (
            "Integración de Home Assistant que sigue las tareas de limpieza y "
            "desgaste del equipo de acuario que Home Assistant **no puede "
            "consultar** — bombas de movimiento, bombas de retorno, skimmers, "
            "reactores, todo lo que se limpia a mano."
        ),
        "contract": (
            "Publica el mismo contrato de entidades `reef_role` que las dos "
            "integraciones de dispositivos conectados, así que sus tareas "
            "aparecen en la vista de mantenimiento de la tarjeta junto al equipo "
            "conectado, sin configuración del lado de la tarjeta."
        ),
        "watch": "Ver el vídeo",
        "card_title": "Con ha-reef-card",
        "card_body": (
            f"La vista de mantenimiento de [ha-reef-card]({CARD}) reúne todas "
            "las tareas de esta integración junto a las de los dispositivos "
            "conectados. Ordena por equipo o por vencimiento, las vencidas "
            "primero; pulsa una fila y el trabajo queda registrado."
        ),
        "card_note": (
            "Nada que configurar en la tarjeta: encuentra las tareas por el "
            "atributo `reef_role`, así que un equipo añadido aquí aparece allí "
            "en la siguiente actualización."
        ),
        "notify_link": (
            f"Las tareas vencidas también pueden llegar a su móvil: el blueprint [Reef maintenance watch]({BLUEPRINTS}) las encuentra por ese mismo atributo `reef_role` y respeta los interruptores de notificación por tarea."
        ),
        "install_title": "Instalación",
        "install_direct_title": "Instalación directa",
        "install_direct_body": "Haga clic aquí para abrir el repositorio directamente en HACS y pulse \u00abDescargar\u00bb:",
        "install_search_title": "Buscar en HACS",
        "install_search_body": "O busque \u00abreef-maintenance\u00bb en HACS.",
        "how_title": "Cómo funciona",
        "how_body": (
            "Una entrada de configuración por **marca**, un dispositivo por "
            "**equipo**, cuatro entidades por **tarea**:"
        ),
        "h_entity": "Entidad",
        "h_role": "Función",
        "e_button": "Botón",
        "r_button": (
            "Registra el trabajo hecho y lleva `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` como atributos"
        ),
        "e_number": "Número",
        "r_number": (
            "Intervalo, en la unidad natural de la tarea (días, semanas o meses)"
        ),
        "e_switch": "Interruptor",
        "r_switch": "Silencia los avisos de vencimiento de esa tarea",
        "e_date": "Fecha",
        "r_date": "Retrodata la última intervención",
        "how_note": (
            "La entidad de fecha importa más de lo que parece: sin ella cada "
            "tarea arranca en «nunca hecha» el día que añades el equipo, y todas "
            "vencen la misma tarde tres meses después."
        ),
        "presets_title": "Preajustes",
        "h_brand": "Marca",
        "h_model": "Modelo",
        "h_tasks": "Tareas",
        "generic": "Genérico",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "Bomba de movimiento DC",
        "m_return": "Bomba de retorno DC",
        "m_skimmer": "Skimmer de rotor de agujas",
        "m_routine": "Mantenimiento rutinario del acuario",
        "m_custom": "Equipo personalizado",
        "t_pump": "bomba, soporte magnético, descalcificar, piezas de desgaste",
        "t_strainer": "filtro, bomba, descalcificar, piezas de desgaste",
        "t_skimmer": (
            "vaso, venturi, rotor de agujas, descalcificar, piezas de desgaste"
        ),
        "t_routine": "cambio de agua, cristales, test ICP, filtros RO/DI, sump, arena",
        "t_none": "ninguna — elige de la biblioteca o escribe la tuya",
        "presets_note": (
            "Los intervalos siguen al fabricante cuando publica una cifra "
            "(Tunze Turbelle: bomba y soporte magnético cada 1–2 meses; Tunze "
            "Silence: limpieza completa al menos anual; Jebao DCP: rotor "
            "mensual; Jebao SLW: mensual a bimestral) y la práctica del arrecife "
            "en los demás casos. Todos son puntos de partida modificables por "
            "equipo."
        ),
        "presets_lib": (
            "Las tareas vienen de una biblioteca común de 21 entradas, traducida "
            "a 8 idiomas. Un preajuste solo referencia claves de la biblioteca y "
            "puede redefinir los límites del intervalo — por eso añadir una "
            "marca no suele costar ninguna cadena de traducción nueva."
        ),
        "service_title": "Servicio",
        "service_body": (
            "`reef_maintenance.reset` marca una tarea como hecha desde una "
            "automatización. Pega una etiqueta NFC junto a la bomba, léela al "
            "terminar, y la tarea queda reconocida sin abrir un panel."
        ),
        "dev_title": "Desarrollo",
        "dev_body": (
            "`scripts/gen_readme.py` regenera esta página y sus siete "
            "traducciones, y `scripts/gen_translations.py` regenera "
            "`strings.json` y los 8 archivos de idioma desde una única tabla "
            "fuente — más de 800 cadenas compuestas a partir de una redacción "
            "por tarea e idioma. Ejecútalos tras tocar la biblioteca de tareas y "
            "confirma el resultado."
        ),
        "tests_title": "Pruebas",
        "tests_body": (
            "La suite cubre el paquete por completo y la CI lo mantiene así. "
            "Vale la pena saber qué protege, porque casi todo es invisible en "
            "ejecución:"
        ),
        "tests_1": (
            "**Claves y unidades de tarea.** Una clave acaba en el `unique_id` "
            "de la entidad y en la clave de almacenamiento, así que renombrarla "
            "pierde el historial de reinicios. Una unidad equivocada cambia en "
            "silencio el significado de un deslizador de intervalo."
        ),
        "tests_2": (
            "**`reef_role`.** El atributo que busca ha-reef-card. Si cambia su "
            "prefijo, la vista de mantenimiento se queda vacía sin ningún error."
        ),
        "tests_3": (
            "**Aritmética de días.** `compute_days_left` redondea alejándose de "
            "cero en ambos sentidos, y «nunca reiniciada» es `None`, no vencida. "
            "Todos los consumidores leen esos valores."
        ),
        "tests_4": (
            "**Colisiones de slug.** Dos tareas personalizadas cuyas etiquetas "
            "se convierten al mismo slug compartirían un `unique_id`, y Home "
            "Assistant descartaría uno de los dos conjuntos de entidades sin "
            "decirlo."
        ),
    },
    "it": {
        "ecosystem_line": f"Parte dell'[**ecosistema ReefTech**]({SITE})",
        "languages": "Lingue disponibili",
        "intro": (
            "Integrazione Home Assistant che tiene traccia delle attività di "
            "pulizia e usura dell'attrezzatura da acquario che Home Assistant "
            "**non può interrogare** — pompe di movimento, pompe di risalita, "
            "schiumatoi, reattori, tutto ciò che si pulisce a mano."
        ),
        "contract": (
            "Pubblica lo stesso contratto di entità `reef_role` delle due "
            "integrazioni per dispositivi connessi, quindi le sue attività "
            "compaiono nella vista manutenzione della scheda accanto "
            "all'attrezzatura connessa, senza configurazione lato scheda."
        ),
        "watch": "Guarda il video",
        "card_title": "Con ha-reef-card",
        "card_body": (
            f"La vista manutenzione di [ha-reef-card]({CARD}) raccoglie tutte le "
            "attività di questa integrazione accanto a quelle dei dispositivi "
            "connessi. Ordina per attrezzatura o per scadenza, le scadute per "
            "prime; premi una riga e il lavoro viene registrato."
        ),
        "card_note": (
            "Nulla da configurare lato scheda: trova le attività tramite "
            "l'attributo `reef_role`, quindi un'attrezzatura aggiunta qui "
            "compare lì al successivo aggiornamento."
        ),
        "notify_link": (
            f"Le attività scadute possono anche arrivare sul telefono: il blueprint [Reef maintenance watch]({BLUEPRINTS}) le trova tramite lo stesso attributo `reef_role` e rispetta gli interruttori di notifica per attività."
        ),
        "install_title": "Installazione",
        "install_direct_title": "Installazione diretta",
        "install_direct_body": "Cliccate qui per aprire il repository direttamente in HACS e premete \u00abDownload\u00bb:",
        "install_search_title": "Cercare in HACS",
        "install_search_body": "Oppure cercate \u00abreef-maintenance\u00bb in HACS.",
        "how_title": "Come funziona",
        "how_body": (
            "Una voce di configurazione per **marca**, un dispositivo per "
            "**attrezzatura**, quattro entità per **attività**:"
        ),
        "h_entity": "Entità",
        "h_role": "Ruolo",
        "e_button": "Pulsante",
        "r_button": (
            "Registra il lavoro svolto e porta `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` come attributi"
        ),
        "e_number": "Numero",
        "r_number": (
            "Intervallo, nell'unità naturale dell'attività (giorni, settimane o mesi)"
        ),
        "e_switch": "Interruttore",
        "r_switch": "Silenzia gli avvisi di scadenza per quell'attività",
        "e_date": "Data",
        "r_date": "Retrodata l'ultimo intervento",
        "how_note": (
            "L'entità data conta più di quanto sembri: senza di essa ogni "
            "attività parte da «mai fatta» il giorno in cui aggiungi "
            "l'attrezzatura, e scadono tutte lo stesso pomeriggio tre mesi dopo."
        ),
        "presets_title": "Preset",
        "h_brand": "Marca",
        "h_model": "Modello",
        "h_tasks": "Attività",
        "generic": "Generico",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "Pompa di movimento DC",
        "m_return": "Pompa di risalita DC",
        "m_skimmer": "Schiumatoio a girante ad aghi",
        "m_routine": "Manutenzione ordinaria dell'acquario",
        "m_custom": "Attrezzatura personalizzata",
        "t_pump": "pompa, supporto magnetico, decalcificazione, parti di usura",
        "t_strainer": "filtro, pompa, decalcificazione, parti di usura",
        "t_skimmer": (
            "bicchiere, venturi, girante ad aghi, decalcificazione, parti di usura"
        ),
        "t_routine": "cambio acqua, vetri, test ICP, filtri RO/DI, sump, sabbia",
        "t_none": "nessuna — scegli dalla libreria o scrivi la tua",
        "presets_note": (
            "Gli intervalli seguono il produttore quando pubblica un dato "
            "(Tunze Turbelle: pompa e supporto magnetico ogni 1–2 mesi; Tunze "
            "Silence: pulizia completa almeno annuale; Jebao DCP: girante "
            "mensile; Jebao SLW: mensile o bimestrale) e la pratica di "
            "acquariofilia altrimenti. Sono tutti punti di partenza, "
            "modificabili per singola attrezzatura."
        ),
        "presets_lib": (
            "Le attività provengono da una libreria comune di 21 voci, tradotta "
            "in 8 lingue. Un preset si limita a referenziare chiavi della "
            "libreria e può ridefinire i limiti dell'intervallo — per questo "
            "aggiungere una marca di solito non costa alcuna nuova stringa di "
            "traduzione."
        ),
        "service_title": "Servizio",
        "service_body": (
            "`reef_maintenance.reset` segna un'attività come svolta da "
            "un'automazione. Attacca un tag NFC vicino alla pompa, scansionalo a "
            "lavoro finito, e l'attività è confermata senza aprire una dashboard."
        ),
        "dev_title": "Sviluppo",
        "dev_body": (
            "`scripts/gen_readme.py` rigenera questa pagina e le sue sette "
            "traduzioni, e `scripts/gen_translations.py` rigenera `strings.json` "
            "e gli 8 file di lingua da un'unica tabella sorgente — oltre 800 "
            "stringhe composte da una formulazione per attività e per lingua. "
            "Eseguili dopo aver toccato la libreria delle attività e committa il "
            "risultato."
        ),
        "tests_title": "Test",
        "tests_body": (
            "La suite copre interamente il pacchetto e la CI lo mantiene tale. "
            "Vale la pena sapere cosa protegge, perché la maggior parte è "
            "invisibile a runtime:"
        ),
        "tests_1": (
            "**Chiavi e unità delle attività.** Una chiave finisce "
            "nell'`unique_id` dell'entità e nella chiave di archiviazione, "
            "quindi rinominarla perde lo storico dei reset. Un'unità sbagliata "
            "cambia in silenzio il significato di un cursore di intervallo."
        ),
        "tests_2": (
            "**`reef_role`.** L'attributo che ha-reef-card cerca. Se il suo "
            "prefisso cambia, la vista manutenzione resta vuota senza alcun "
            "errore."
        ),
        "tests_3": (
            "**Aritmetica dei giorni.** `compute_days_left` arrotonda "
            "allontanandosi da zero in entrambe le direzioni, e «mai "
            "reimpostata» è `None`, non scaduta. Tutti i consumatori leggono "
            "quei valori."
        ),
        "tests_4": (
            "**Collisioni di slug.** Due attività personalizzate le cui "
            "etichette si slugificano allo stesso modo condividerebbero un "
            "`unique_id`, e Home Assistant scarterebbe uno dei due set di entità "
            "senza dirlo."
        ),
    },
    "nl": {
        "ecosystem_line": f"Onderdeel van het [**ReefTech Project Ecosystem**]({SITE})",
        "languages": "Beschikbare talen",
        "intro": (
            "Home Assistant-integratie die schoonmaak- en slijtagetaken bijhoudt "
            "voor aquariumapparatuur die Home Assistant **niet kan uitlezen** — "
            "stromingspompen, opvoerpompen, eiwitafschuimers, reactoren, alles "
            "wat u met de hand onderhoudt."
        ),
        "contract": (
            "Ze publiceert hetzelfde `reef_role`-entiteitencontract als de twee "
            "integraties voor verbonden apparaten, zodat haar taken in het "
            "onderhoudsoverzicht van de kaart verschijnen naast de verbonden "
            "apparatuur, zonder configuratie aan de kaartzijde."
        ),
        "watch": "Bekijk de video",
        "card_title": "Met ha-reef-card",
        "card_body": (
            f"Het onderhoudsoverzicht van [ha-reef-card]({CARD}) verzamelt alle "
            "taken van deze integratie naast die van de verbonden apparaten. "
            "Sorteer op apparaat of op vervaldatum, achterstallige eerst; druk "
            "op een regel en het werk is vastgelegd."
        ),
        "card_note": (
            "Aan de kaartzijde valt niets in te stellen: ze vindt de taken via "
            "het `reef_role`-attribuut, dus apparatuur die u hier toevoegt "
            "verschijnt daar bij de volgende verversing."
        ),
        "notify_link": (
            f"Achterstallige taken kunnen ook op uw telefoon komen: de blueprint [Reef maintenance watch]({BLUEPRINTS}) vindt ze via hetzelfde `reef_role`-attribuut en respecteert de meldingsschakelaars per taak."
        ),
        "install_title": "Installatie",
        "install_direct_title": "Directe installatie",
        "install_direct_body": 'Klik hier om de repository rechtstreeks in HACS te openen en klik op "Downloaden":',
        "install_search_title": "Zoeken in HACS",
        "install_search_body": 'Of zoek naar "reef-maintenance" in HACS.',
        "how_title": "Hoe het werkt",
        "how_body": (
            "Eén configuratie-item per **merk**, één apparaat per "
            "**apparatuur**, vier entiteiten per **taak**:"
        ),
        "h_entity": "Entiteit",
        "h_role": "Rol",
        "e_button": "Knop",
        "r_button": (
            "Legt vast dat het werk gedaan is en draagt `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` als attributen"
        ),
        "e_number": "Getal",
        "r_number": (
            "Interval, in de natuurlijke eenheid van de taak (dagen, weken of maanden)"
        ),
        "e_switch": "Schakelaar",
        "r_switch": "Dempt achterstandsmeldingen voor die taak",
        "e_date": "Datum",
        "r_date": "Zet de laatste onderhoudsbeurt met terugwerkende kracht",
        "how_note": (
            "De datumentiteit telt zwaarder dan ze lijkt: zonder haar begint "
            'elke taak op „nooit gedaan" op de dag dat u de apparatuur '
            "toevoegt, en vervallen ze drie maanden later allemaal dezelfde "
            "middag."
        ),
        "presets_title": "Voorinstellingen",
        "h_brand": "Merk",
        "h_model": "Model",
        "h_tasks": "Taken",
        "generic": "Generiek",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "DC-stromingspomp",
        "m_return": "DC-opvoerpomp",
        "m_skimmer": "Naaldrad-eiwitafschuimer",
        "m_routine": "Routineonderhoud aquarium",
        "m_custom": "Eigen apparatuur",
        "t_pump": "pomp, magneethouder, ontkalken, slijtdelen",
        "t_strainer": "aanzuigkorf, pomp, ontkalken, slijtdelen",
        "t_skimmer": "beker, venturi, naaldrad, ontkalken, slijtdelen",
        "t_routine": "waterwissel, ruiten, ICP-test, RO/DI-filters, sump, zand",
        "t_none": "geen — kies uit de bibliotheek of typ uw eigen taak",
        "presets_note": (
            "De intervallen volgen de fabrikant waar die een getal publiceert "
            "(Tunze Turbelle: pomp en magneethouder elke 1–2 maanden; Tunze "
            "Silence: volledige reiniging minstens jaarlijks; Jebao DCP: "
            "maandelijks de rotor; Jebao SLW: maandelijks tot tweemaandelijks) "
            "en anders de rifpraktijk. Het zijn allemaal startpunten, per "
            "apparatuur aanpasbaar."
        ),
        "presets_lib": (
            "De taken komen uit een gedeelde bibliotheek van 21 items, vertaald "
            "in 8 talen. Een voorinstelling verwijst alleen naar "
            "bibliotheeksleutels en mag de intervalgrenzen overschrijven — "
            "daarom kost een nieuw merk meestal geen enkele nieuwe vertaalregel."
        ),
        "service_title": "Service",
        "service_body": (
            "`reef_maintenance.reset` markeert een taak als gedaan vanuit een "
            "automatisering. Plak een NFC-tag bij de pomp, scan hem als u klaar "
            "bent, en de taak is afgetekend zonder een dashboard te openen."
        ),
        "dev_title": "Ontwikkeling",
        "dev_body": (
            "`scripts/gen_readme.py` genereert deze pagina en haar zeven "
            "vertalingen opnieuw, en `scripts/gen_translations.py` genereert "
            "`strings.json` en de 8 taalbestanden uit één brontabel — meer dan "
            "800 teksten samengesteld uit één formulering per taak per taal. "
            "Draai ze na een wijziging aan de takenbibliotheek en commit het "
            "resultaat."
        ),
        "tests_title": "Tests",
        "tests_body": (
            "De suite dekt het pakket volledig en de CI houdt dat zo. Het is "
            "nuttig te weten wat ze bewaakt, want het meeste is tijdens "
            "uitvoering onzichtbaar:"
        ),
        "tests_1": (
            "**Taaksleutels en eenheden.** Een sleutel belandt in de "
            "`unique_id` van de entiteit en in de opslagsleutel, dus hernoemen "
            "wist de reset-geschiedenis. Een verkeerde eenheid verandert "
            "stilzwijgend wat een intervalschuif betekent."
        ),
        "tests_2": (
            "**`reef_role`.** Het attribuut waar ha-reef-card op zoekt. "
            "Verandert het voorvoegsel, dan blijft het onderhoudsoverzicht leeg "
            "zonder enige foutmelding."
        ),
        "tests_3": (
            "**Dagrekenkunde.** `compute_days_left` rondt in beide richtingen "
            'van nul af, en „nooit gereset" is `None` en niet achterstallig. '
            "Alle afnemers lezen die waarden."
        ),
        "tests_4": (
            "**Slug-botsingen.** Twee eigen taken waarvan de labels tot dezelfde "
            "slug leiden zouden één `unique_id` delen, en Home Assistant zou een "
            "van beide entiteitensets zonder melding laten vallen."
        ),
    },
    "pl": {
        "ecosystem_line": f"Część [**ekosystemu ReefTech**]({SITE})",
        "languages": "Dostępne języki",
        "intro": (
            "Integracja Home Assistant śledząca zadania czyszczenia i zużycia "
            "sprzętu akwariowego, z którym Home Assistant **nie może się "
            "komunikować** — pompy cyrkulacyjne, pompy obiegowe, odpieniacze, "
            "reaktory, wszystko co czyścisz ręcznie."
        ),
        "contract": (
            "Publikuje ten sam kontrakt encji `reef_role` co dwie integracje "
            "urządzeń podłączonych, więc jej zadania pojawiają się w widoku "
            "konserwacji karty obok sprzętu podłączonego, bez konfiguracji po "
            "stronie karty."
        ),
        "watch": "Obejrzyj wideo",
        "card_title": "Z ha-reef-card",
        "card_body": (
            f"Widok konserwacji [ha-reef-card]({CARD}) zbiera wszystkie zadania "
            "tej integracji obok zadań urządzeń podłączonych. Sortuj według "
            "sprzętu lub terminu, zaległe najpierw; naciśnij wiersz, a praca "
            "zostanie zapisana."
        ),
        "card_note": (
            "Po stronie karty nie ma nic do ustawienia: znajduje zadania przez "
            "atrybut `reef_role`, więc sprzęt dodany tutaj pojawi się tam przy "
            "następnym odświeżeniu."
        ),
        "notify_link": (
            f"Zaległe zadania mogą też trafić na telefon: blueprint [Reef maintenance watch]({BLUEPRINTS}) znajduje je przez ten sam atrybut `reef_role` i respektuje przełączniki powiadomień poszczególnych zadań."
        ),
        "install_title": "Instalacja",
        "install_direct_title": "Bezpośrednia instalacja",
        "install_direct_body": "Kliknij tutaj, aby otworzyć repozytorium bezpośrednio w HACS i kliknij \u00abPobierz\u00bb:",
        "install_search_title": "Szukaj w HACS",
        "install_search_body": "Lub wyszukaj \u00abreef-maintenance\u00bb w HACS.",
        "how_title": "Jak to działa",
        "how_body": (
            "Jeden wpis konfiguracji na **markę**, jedno urządzenie na "
            "**sprzęt**, cztery encje na **zadanie**:"
        ),
        "h_entity": "Encja",
        "h_role": "Rola",
        "e_button": "Przycisk",
        "r_button": (
            "Zapisuje wykonanie pracy i niesie `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` jako atrybuty"
        ),
        "e_number": "Liczba",
        "r_number": (
            "Interwał, w naturalnej jednostce zadania (dni, tygodnie lub miesiące)"
        ),
        "e_switch": "Przełącznik",
        "r_switch": "Wycisza powiadomienia o zaległości tego zadania",
        "e_date": "Data",
        "r_date": "Wstecznie datuje ostatnią interwencję",
        "how_note": (
            "Encja daty znaczy więcej, niż się wydaje: bez niej każde zadanie "
            'startuje od „nigdy nie wykonano" w dniu dodania sprzętu, a '
            "wszystkie stają się wymagalne tego samego popołudnia trzy miesiące "
            "później."
        ),
        "presets_title": "Ustawienia wstępne",
        "h_brand": "Marka",
        "h_model": "Model",
        "h_tasks": "Zadania",
        "generic": "Generyczne",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "Pompa cyrkulacyjna DC",
        "m_return": "Pompa obiegowa DC",
        "m_skimmer": "Odpieniacz z wirnikiem igiełkowym",
        "m_routine": "Rutynowa konserwacja akwarium",
        "m_custom": "Sprzęt własny",
        "t_pump": "pompa, uchwyt magnetyczny, odkamienianie, części zużywalne",
        "t_strainer": "sitko, pompa, odkamienianie, części zużywalne",
        "t_skimmer": (
            "kubek, venturi, wirnik igiełkowy, odkamienianie, części zużywalne"
        ),
        "t_routine": "podmiana wody, szyby, test ICP, filtry RO/DI, sump, piasek",
        "t_none": "brak — wybierz z biblioteki lub wpisz własne",
        "presets_note": (
            "Interwały idą za producentem tam, gdzie podaje liczbę (Tunze "
            "Turbelle: pompa i uchwyt magnetyczny co 1–2 miesiące; Tunze "
            "Silence: pełne czyszczenie co najmniej raz w roku; Jebao DCP: "
            "wirnik co miesiąc; Jebao SLW: co miesiąc do co dwa miesiące), a "
            "poza tym za praktyką rafową. Wszystkie są punktami wyjścia, "
            "zmiennymi dla każdego sprzętu."
        ),
        "presets_lib": (
            "Zadania pochodzą ze wspólnej biblioteki 21 pozycji, przetłumaczonej "
            "na 8 języków. Ustawienie wstępne tylko odwołuje się do kluczy "
            "biblioteki i może nadpisać granice interwału — dlatego dodanie "
            "marki zwykle nie kosztuje żadnego nowego ciągu tłumaczenia."
        ),
        "service_title": "Usługa",
        "service_body": (
            "`reef_maintenance.reset` oznacza zadanie jako wykonane z poziomu "
            "automatyzacji. Przyklej tag NFC przy pompie, zeskanuj go po "
            "zakończeniu, a zadanie zostanie potwierdzone bez otwierania "
            "pulpitu."
        ),
        "dev_title": "Rozwój",
        "dev_body": (
            "`scripts/gen_readme.py` generuje tę stronę i jej siedem tłumaczeń, "
            "a `scripts/gen_translations.py` generuje `strings.json` i 8 plików "
            "językowych z jednej tabeli źródłowej — ponad 800 ciągów złożonych z "
            "jednego sformułowania na zadanie i język. Uruchom je po zmianie "
            "biblioteki zadań i zatwierdź wynik."
        ),
        "tests_title": "Testy",
        "tests_body": (
            "Zestaw pokrywa pakiet w całości, a CI tego pilnuje. Warto wiedzieć, "
            "czego strzeże, bo większość jest niewidoczna w działaniu:"
        ),
        "tests_1": (
            "**Klucze i jednostki zadań.** Klucz trafia do `unique_id` encji i "
            "do klucza magazynu, więc zmiana nazwy gubi historię resetów. Zła "
            "jednostka po cichu zmienia znaczenie suwaka interwału."
        ),
        "tests_2": (
            "**`reef_role`.** Atrybut, którego szuka ha-reef-card. Jeśli zmieni "
            "się jego przedrostek, widok konserwacji pozostanie pusty bez "
            "żadnego błędu."
        ),
        "tests_3": (
            "**Arytmetyka dni.** `compute_days_left` zaokrągla w obie strony od "
            'zera, a „nigdy nie zresetowano" to `None`, a nie zaległość. '
            "Wszyscy odbiorcy czytają te wartości."
        ),
        "tests_4": (
            "**Kolizje slugów.** Dwa własne zadania, których etykiety dają ten "
            "sam slug, dzieliłyby jeden `unique_id`, a Home Assistant bez słowa "
            "porzuciłby jeden z dwóch zestawów encji."
        ),
    },
    "pt": {
        "ecosystem_line": f"Parte do [**ecossistema ReefTech**]({SITE})",
        "languages": "Idiomas disponíveis",
        "intro": (
            "Integração Home Assistant que acompanha as tarefas de limpeza e "
            "desgaste do equipamento de aquário que o Home Assistant **não "
            "consegue interrogar** — bombas de circulação, bombas de retorno, "
            "escumadores, reatores, tudo o que limpa à mão."
        ),
        "contract": (
            "Publica o mesmo contrato de entidades `reef_role` que as duas "
            "integrações de aparelhos ligados, por isso as suas tarefas "
            "aparecem na vista de manutenção do cartão ao lado do equipamento "
            "ligado, sem configuração do lado do cartão."
        ),
        "watch": "Ver o vídeo",
        "card_title": "Com o ha-reef-card",
        "card_body": (
            f"A vista de manutenção do [ha-reef-card]({CARD}) reúne todas as "
            "tarefas desta integração ao lado das dos aparelhos ligados. Ordene "
            "por equipamento ou por prazo, as vencidas primeiro; prima uma linha "
            "e o trabalho fica registado."
        ),
        "card_note": (
            "Nada a configurar do lado do cartão: encontra as tarefas pelo "
            "atributo `reef_role`, por isso um equipamento aqui adicionado "
            "aparece lá na atualização seguinte."
        ),
        "notify_link": (
            f"As tarefas em atraso também podem chegar ao seu telemóvel: o blueprint [Reef maintenance watch]({BLUEPRINTS}) encontra-as pelo mesmo atributo `reef_role` e respeita os interruptores de notificação por tarefa."
        ),
        "install_title": "Instalação",
        "install_direct_title": "Instalação direta",
        "install_direct_body": "Clique aqui para abrir o repositório diretamente no HACS e clique em \u00abDownload\u00bb:",
        "install_search_title": "Procurar no HACS",
        "install_search_body": "Ou procure \u00abreef-maintenance\u00bb no HACS.",
        "how_title": "Como funciona",
        "how_body": (
            "Uma entrada de configuração por **marca**, um aparelho por "
            "**equipamento**, quatro entidades por **tarefa**:"
        ),
        "h_entity": "Entidade",
        "h_role": "Função",
        "e_button": "Botão",
        "r_button": (
            "Regista o trabalho feito e transporta `days_left`, `overdue`, "
            "`interval_days`, `task_key`, `notify` como atributos"
        ),
        "e_number": "Número",
        "r_number": (
            "Intervalo, na unidade natural da tarefa (dias, semanas ou meses)"
        ),
        "e_switch": "Interruptor",
        "r_switch": "Silencia os avisos de atraso dessa tarefa",
        "e_date": "Data",
        "r_date": "Retroage a última intervenção",
        "how_note": (
            "A entidade de data conta mais do que parece: sem ela cada tarefa "
            "começa em «nunca feita» no dia em que adiciona o equipamento, e "
            "todas vencem na mesma tarde três meses depois."
        ),
        "presets_title": "Predefinições",
        "h_brand": "Marca",
        "h_model": "Modelo",
        "h_tasks": "Tarefas",
        "generic": "Genérico",
        "m_stream": "Turbelle stream / stream 3",
        "m_nano": "Turbelle nanostream",
        "m_silence": "Silence / Silence PRO",
        "m_slw": "SLW / MLW / SCP / SOW",
        "m_dcp": "DCP / MDP",
        "m_flow": "Bomba de circulação DC",
        "m_return": "Bomba de retorno DC",
        "m_skimmer": "Escumador de rotor de agulhas",
        "m_routine": "Manutenção de rotina do aquário",
        "m_custom": "Equipamento personalizado",
        "t_pump": "bomba, suporte magnético, descalcificar, peças de desgaste",
        "t_strainer": "filtro, bomba, descalcificar, peças de desgaste",
        "t_skimmer": (
            "copo, venturi, rotor de agulhas, descalcificar, peças de desgaste"
        ),
        "t_routine": "mudança de água, vidros, teste ICP, filtros RO/DI, sump, areia",
        "t_none": "nenhuma — escolha da biblioteca ou escreva a sua",
        "presets_note": (
            "Os intervalos seguem o fabricante sempre que publica um valor "
            "(Tunze Turbelle: bomba e suporte magnético a cada 1–2 meses; Tunze "
            "Silence: limpeza completa pelo menos anual; Jebao DCP: rotor "
            "mensal; Jebao SLW: mensal a bimestral) e a prática de recife nos "
            "restantes casos. São todos pontos de partida, alteráveis por "
            "equipamento."
        ),
        "presets_lib": (
            "As tarefas vêm de uma biblioteca comum de 21 entradas, traduzida em "
            "8 idiomas. Uma predefinição apenas referencia chaves da biblioteca "
            "e pode redefinir os limites do intervalo — daí que acrescentar uma "
            "marca não costume custar qualquer nova cadeia de tradução."
        ),
        "service_title": "Serviço",
        "service_body": (
            "`reef_maintenance.reset` marca uma tarefa como feita a partir de "
            "uma automação. Cole uma etiqueta NFC junto à bomba, leia-a quando "
            "terminar, e a tarefa fica confirmada sem abrir um painel."
        ),
        "dev_title": "Desenvolvimento",
        "dev_body": (
            "`scripts/gen_readme.py` regenera esta página e as suas sete "
            "traduções, e `scripts/gen_translations.py` regenera `strings.json` "
            "e os 8 ficheiros de idioma a partir de uma única tabela de origem — "
            "mais de 800 cadeias compostas a partir de uma redação por tarefa e "
            "por idioma. Execute-os depois de mexer na biblioteca de tarefas e "
            "faça commit do resultado."
        ),
        "tests_title": "Testes",
        "tests_body": (
            "A suite cobre o pacote por completo e a CI mantém-no assim. Vale a "
            "pena saber o que protege, porque a maior parte é invisível em "
            "execução:"
        ),
        "tests_1": (
            "**Chaves e unidades das tarefas.** Uma chave acaba no `unique_id` "
            "da entidade e na chave de armazenamento, por isso renomeá-la perde "
            "o histórico de reinícios. Uma unidade errada muda em silêncio o "
            "significado de um cursor de intervalo."
        ),
        "tests_2": (
            "**`reef_role`.** O atributo que o ha-reef-card procura. Se o seu "
            "prefixo mudar, a vista de manutenção fica vazia sem qualquer erro."
        ),
        "tests_3": (
            "**Aritmética dos dias.** `compute_days_left` arredonda afastando-se "
            "de zero nos dois sentidos, e «nunca reiniciada» é `None` e não "
            "vencida. Todos os consumidores leem esses valores."
        ),
        "tests_4": (
            "**Colisões de slug.** Duas tarefas personalizadas cujas etiquetas "
            "dão o mesmo slug partilhariam um `unique_id`, e o Home Assistant "
            "descartaria um dos dois conjuntos de entidades sem o dizer."
        ),
    },
}


def language_bar(current: str) -> str:
    """The flag row, with the current language shown but not linked."""
    parts = []
    for flag, code, path in LANGS:
        img = (
            f'<img src="https://flagicons.lipis.dev/flags/4x3/{flag}.svg" width="5%"/>'
        )
        if code == current:
            parts.append(img)
        else:
            parts.append(f"[{img}]({REPO}/blob/main/{path})")
    return " ".join(parts)


def video(t: dict[str, str]) -> str:
    """The YouTube thumbnail-as-link, same shape as in ha-reef-card."""
    return (
        f"[![{t['watch']}](https://img.youtube.com/vi/{VIDEO_ID}/0.jpg)]"
        f"(https://www.youtube.com/watch?v={VIDEO_ID})"
    )


def presets_table(t: dict[str, str]) -> str:
    rows = [
        ("Tunze", t["m_stream"], t["t_pump"]),
        ("Tunze", t["m_nano"], t["t_pump"]),
        ("Tunze", t["m_silence"], t["t_strainer"]),
        ("Jebao", t["m_slw"], t["t_pump"]),
        ("Jebao", t["m_dcp"], t["t_strainer"]),
        (t["generic"], t["m_flow"], t["t_pump"]),
        (t["generic"], t["m_return"], t["t_strainer"]),
        (t["generic"], t["m_skimmer"], t["t_skimmer"]),
        (t["generic"], t["m_routine"], t["t_routine"]),
        (t["generic"], t["m_custom"], t["t_none"]),
    ]
    head = f"| {t['h_brand']} | {t['h_model']} | {t['h_tasks']} |\n|---|---|---|"
    return "\n".join([head] + [f"| {a} | {b} | {c} |" for a, b, c in rows])


ECOSYSTEM_START = "<!-- ecosystem:start -->"
ECOSYSTEM_END = "<!-- ecosystem:end -->"


def preserve_ecosystem(existing: str, generated: str) -> str:
    """Carry an existing "Related projects" block into the new content.

    That block is written by reeftank/scripts/gen_ecosystem.py, which lives in
    another repository and is not available in CI. Without this, regenerating
    would silently drop it, and the workflow that checks the generated files
    are up to date would fail on every run.

    The block goes back where gen_ecosystem puts it: just before the first
    second-level heading.
    """
    start = existing.find(ECOSYSTEM_START)
    if start == -1:
        return generated
    end = existing.find(ECOSYSTEM_END)
    if end == -1:
        return generated
    block = existing[start : end + len(ECOSYSTEM_END)]

    at = generated.find("\n## ")
    if at == -1:
        return generated
    return generated[: at + 1] + block + "\n\n" + generated[at + 1 :]


def render(code: str) -> str:
    t = T[code]
    icon = "icon.png" if code == "en" else f"{REPO}/raw/main/icon.png"
    return f"""# Reef maintenance 🐙
> {t["ecosystem_line"]}
<p align="center">
  <img src="{icon}"  width="50%"/>
</p>

{BADGES}

# {t["languages"]}: {language_bar(code)}

{t["intro"]}

{t["contract"]}

## {t["card_title"]}

<p align="center">
  <img src="{OVERVIEW}" width="90%"/>
</p>

{t["card_body"]}

{t["card_note"]}

{t["notify_link"]}

{video(t)}

## {t["install_title"]}

### {t["install_direct_title"]}

{t["install_direct_body"]} {HACS_BADGE}

### {t["install_search_title"]}

{t["install_search_body"]}

## {t["how_title"]}

{t["how_body"]}

| {t["h_entity"]} | {t["h_role"]} |
|---|---|
| {t["e_button"]} | {t["r_button"]} |
| {t["e_number"]} | {t["r_number"]} |
| {t["e_switch"]} | {t["r_switch"]} |
| {t["e_date"]} | {t["r_date"]} |

{t["how_note"]}

## {t["presets_title"]}

{presets_table(t)}

{t["presets_note"]}

{t["presets_lib"]}

## {t["service_title"]}

{t["service_body"]}

{SERVICE_YAML}

## {t["dev_title"]}

{t["dev_body"]}

### {t["tests_title"]}

{TESTS_SH}

{t["tests_body"]}

- {t["tests_1"]}
- {t["tests_2"]}
- {t["tests_3"]}
- {t["tests_4"]}
"""


def main() -> None:
    missing = [
        (code, key)
        for _, code, _ in LANGS
        for key in T["en"]
        if key not in T.get(code, {})
    ]
    if missing:
        raise SystemExit(f"untranslated keys: {missing}")

    for _, code, path in LANGS:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        target.write_text(preserve_ecosystem(existing, render(code)), encoding="utf-8")
        print("written", path)


if __name__ == "__main__":
    sys.exit(main())
