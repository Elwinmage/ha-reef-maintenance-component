#!/usr/bin/env python3
"""Generate strings.json and the 8 locale files from a single source table.

Every task produces four entity names (button, interval number, notification
switch, last-done date) and one selector option, in eight languages. Writing
that by hand is 800+ strings; here it is one wording per task per language,
and the script composes the rest.

    python3 scripts/gen_translations.py
"""

from __future__ import annotations

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
BASE = os.path.join(REPO_ROOT, "custom_components", "reef_maintenance")
TRANSLATIONS = os.path.join(BASE, "translations")

LANGS = ("en", "fr", "de", "es", "it", "nl", "pl", "pt")

# Task key -> display unit of its interval entity. Must match tasks.py.
TASK_UNITS: dict[str, str] = {
    "pump_clean": "weeks",
    "magnet_holder_clean": "weeks",
    "strainer_clean": "weeks",
    "pump_descale": "months",
    "wear_parts_replace": "months",
    "skimmer_cup_clean": "weeks",
    "venturi_clean": "weeks",
    "needle_wheel_clean": "months",
    "skimmer_body_descale": "months",
    "sock_replace": "days",
    "carbon_replace": "weeks",
    "resin_replace": "months",
    "probe_calibrate": "months",
    "probe_clean": "months",
    "uv_lamp_replace": "months",
    "water_change": "weeks",
    "glass_clean": "days",
    "icp_test": "months",
    "rodi_filter_replace": "months",
    "sump_clean": "months",
    "sand_vacuum": "weeks",
}

ORDER = list(TASK_UNITS)

# Task wording, in ORDER, per language.
NAMES: dict[str, list[str]] = {
    "en": [
        "Clean impeller and pump chamber",
        "Clean magnet holder and mount",
        "Clean suction strainer",
        "Descale pump",
        "Replace wear parts kit",
        "Clean collection cup",
        "Clean venturi and air line",
        "Clean needle wheel",
        "Descale skimmer body",
        "Replace filter sock",
        "Replace activated carbon",
        "Replace resins",
        "Calibrate probe",
        "Clean probe",
        "Replace UV lamp",
        "Water change",
        "Clean the glass",
        "ICP / water lab test",
        "Replace RO/DI filters",
        "Clean the sump",
        "Vacuum sand bed",
    ],
    "fr": [
        "Nettoyer le rotor et la chambre de pompe",
        "Nettoyer le support magnétique et la fixation",
        "Nettoyer la crépine d'aspiration",
        "Détartrer la pompe",
        "Remplacer le kit de pièces d'usure",
        "Nettoyer le gobelet",
        "Nettoyer le venturi et le tuyau d'air",
        "Nettoyer le rotor à aiguilles",
        "Détartrer le corps de l'écumeur",
        "Changer la chaussette",
        "Remplacer le charbon actif",
        "Remplacer les résines",
        "Étalonner la sonde",
        "Nettoyer la sonde",
        "Remplacer la lampe UV",
        "Changement d'eau",
        "Nettoyer les vitres",
        "Analyse ICP / test eau labo",
        "Remplacer les filtres RO/DI",
        "Nettoyer le bac décanteur",
        "Siphonner le sable",
    ],
    "de": [
        "Rotor und Pumpenkammer reinigen",
        "Magnethalter und Befestigung reinigen",
        "Ansaugkorb reinigen",
        "Pumpe entkalken",
        "Verschleißteile-Set ersetzen",
        "Schaumtopf reinigen",
        "Venturi und Luftschlauch reinigen",
        "Nadelrad reinigen",
        "Abschäumerkörper entkalken",
        "Filtersocke wechseln",
        "Aktivkohle ersetzen",
        "Harze ersetzen",
        "Sonde kalibrieren",
        "Sonde reinigen",
        "UV-Lampe ersetzen",
        "Wasserwechsel",
        "Scheiben reinigen",
        "ICP / Wasseranalyse im Labor",
        "RO/DI-Filter ersetzen",
        "Technikbecken reinigen",
        "Sandbett absaugen",
    ],
    "es": [
        "Limpiar el rotor y la cámara de la bomba",
        "Limpiar el soporte magnético y la fijación",
        "Limpiar la cesta de aspiración",
        "Descalcificar la bomba",
        "Sustituir el kit de piezas de desgaste",
        "Limpiar el vaso colector",
        "Limpiar el venturi y el tubo de aire",
        "Limpiar el rotor de agujas",
        "Descalcificar el cuerpo del skimmer",
        "Cambiar el calcetín de filtro",
        "Sustituir el carbón activo",
        "Sustituir las resinas",
        "Calibrar la sonda",
        "Limpiar la sonda",
        "Sustituir la lámpara UV",
        "Cambio de agua",
        "Limpiar los cristales",
        "Análisis ICP / test de agua en laboratorio",
        "Sustituir los filtros RO/DI",
        "Limpiar el sump",
        "Sifonar el lecho de arena",
    ],
    "it": [
        "Pulire il rotore e la camera della pompa",
        "Pulire il supporto magnetico e il fissaggio",
        "Pulire il cestello di aspirazione",
        "Decalcificare la pompa",
        "Sostituire il kit di parti soggette a usura",
        "Pulire il bicchiere di raccolta",
        "Pulire il venturi e il tubo dell'aria",
        "Pulire la girante ad aghi",
        "Decalcificare il corpo dello schiumatoio",
        "Cambiare il calzino filtrante",
        "Sostituire il carbone attivo",
        "Sostituire le resine",
        "Calibrare la sonda",
        "Pulire la sonda",
        "Sostituire la lampada UV",
        "Cambio d'acqua",
        "Pulire i vetri",
        "Analisi ICP / test acqua in laboratorio",
        "Sostituire i filtri RO/DI",
        "Pulire la sump",
        "Sifonare il letto di sabbia",
    ],
    "nl": [
        "Rotor en pompkamer reinigen",
        "Magneethouder en bevestiging reinigen",
        "Aanzuigkorf reinigen",
        "Pomp ontkalken",
        "Slijtdelenset vervangen",
        "Opvangbeker reinigen",
        "Venturi en luchtslang reinigen",
        "Naaldrotor reinigen",
        "Skimmerbehuizing ontkalken",
        "Filterkous vervangen",
        "Actieve kool vervangen",
        "Harsen vervangen",
        "Sonde kalibreren",
        "Sonde reinigen",
        "UV-lamp vervangen",
        "Waterwissel",
        "Ruiten reinigen",
        "ICP / wateranalyse in laboratorium",
        "RO/DI-filters vervangen",
        "Sump reinigen",
        "Zandbed afzuigen",
    ],
    "pl": [
        "Wyczyść wirnik i komorę pompy",
        "Wyczyść uchwyt magnetyczny i mocowanie",
        "Wyczyść kosz ssawny",
        "Odkamień pompę",
        "Wymień zestaw części zużywalnych",
        "Wyczyść kubek odpieniacza",
        "Wyczyść venturi i wężyk powietrza",
        "Wyczyść wirnik igiełkowy",
        "Odkamień korpus odpieniacza",
        "Wymień skarpetę filtracyjną",
        "Wymień węgiel aktywny",
        "Wymień żywice",
        "Skalibruj sondę",
        "Wyczyść sondę",
        "Wymień lampę UV",
        "Podmiana wody",
        "Wyczyść szyby",
        "Analiza ICP / badanie wody w laboratorium",
        "Wymień filtry RO/DI",
        "Wyczyść sump",
        "Odkurz podłoże piaskowe",
    ],
    "pt": [
        "Limpar o rotor e a câmara da bomba",
        "Limpar o suporte magnético e a fixação",
        "Limpar o cesto de aspiração",
        "Descalcificar a bomba",
        "Substituir o kit de peças de desgaste",
        "Limpar o copo coletor",
        "Limpar o venturi e o tubo de ar",
        "Limpar o rotor de agulhas",
        "Descalcificar o corpo do escumador",
        "Mudar a meia filtrante",
        "Substituir o carvão ativado",
        "Substituir as resinas",
        "Calibrar a sonda",
        "Limpar a sonda",
        "Substituir a lâmpada UV",
        "Mudança de água",
        "Limpar os vidros",
        "Análise ICP / teste de água em laboratório",
        "Substituir os filtros RO/DI",
        "Limpar a sump",
        "Aspirar o leito de areia",
    ],
}

# Suffixes appended to the companion entity names.
UNITS: dict[str, dict[str, str]] = {
    "en": {"days": "days", "weeks": "weeks", "months": "months"},
    "fr": {"days": "jours", "weeks": "semaines", "months": "mois"},
    "de": {"days": "Tage", "weeks": "Wochen", "months": "Monate"},
    "es": {"days": "días", "weeks": "semanas", "months": "meses"},
    "it": {"days": "giorni", "weeks": "settimane", "months": "mesi"},
    "nl": {"days": "dagen", "weeks": "weken", "months": "maanden"},
    "pl": {"days": "dni", "weeks": "tygodnie", "months": "miesiące"},
    "pt": {"days": "dias", "weeks": "semanas", "months": "meses"},
}

NOTIFY: dict[str, str] = {
    "en": "notifications",
    "fr": "notifications",
    "de": "Benachrichtigungen",
    "es": "notificaciones",
    "it": "notifiche",
    "nl": "meldingen",
    "pl": "powiadomienia",
    "pt": "notificações",
}

LAST_DONE: dict[str, str] = {
    "en": "last done",
    "fr": "dernière fois",
    "de": "zuletzt erledigt",
    "es": "última vez",
    "it": "ultima volta",
    "nl": "laatst gedaan",
    "pl": "ostatnio",
    "pt": "última vez",
}

# Config and options flow wording.
FLOW: dict[str, dict[str, str]] = {
    "en": {
        "user_title": "Reef maintenance",
        "user_desc": "Pick the brand of the equipment to track. One entry per brand; add as many equipments as you like afterwards.",
        "brand": "Brand",
        "already": "This brand is already configured.",
        "menu_add": "Add an equipment",
        "menu_edit": "Edit an equipment",
        "menu_remove": "Remove an equipment",
        "add_title": "New equipment",
        "add_desc": "Name it the way you call it at the tank, then pick the closest model.",
        "name": "Name",
        "preset": "Model",
        "tasks_title": "Tasks for {equipment}",
        "tasks_desc": "Tasks from the model are preselected — uncheck what does not apply. Add your own below if something is missing.",
        "tasks": "Tasks",
        "custom_tasks": "Custom tasks",
        "edit_title": "Edit an equipment",
        "edit_desc": "Which equipment?",
        "edit_eq_title": "Edit {equipment}",
        "edit_eq_desc": "Intervals are not set here: each task has its own slider on the dashboard.",
        "remove_title": "Remove an equipment",
        "remove_desc": "Its tasks and their history are deleted.",
        "equipment": "Equipment",
    },
    "fr": {
        "user_title": "Maintenance récifale",
        "user_desc": "Choisissez la marque du matériel à suivre. Une entrée par marque ; vous ajouterez autant d'équipements que voulu ensuite.",
        "brand": "Marque",
        "already": "Cette marque est déjà configurée.",
        "menu_add": "Ajouter un équipement",
        "menu_edit": "Modifier un équipement",
        "menu_remove": "Supprimer un équipement",
        "add_title": "Nouvel équipement",
        "add_desc": "Nommez-le comme vous l'appelez devant le bac, puis choisissez le modèle le plus proche.",
        "name": "Nom",
        "preset": "Modèle",
        "tasks_title": "Tâches de {equipment}",
        "tasks_desc": "Les tâches du modèle sont pré-cochées — décochez ce qui ne s'applique pas. Ajoutez les vôtres en dessous s'il en manque.",
        "tasks": "Tâches",
        "custom_tasks": "Tâches personnalisées",
        "edit_title": "Modifier un équipement",
        "edit_desc": "Quel équipement ?",
        "edit_eq_title": "Modifier {equipment}",
        "edit_eq_desc": "Les intervalles ne se règlent pas ici : chaque tâche a son propre curseur sur le tableau de bord.",
        "remove_title": "Supprimer un équipement",
        "remove_desc": "Ses tâches et leur historique sont supprimés.",
        "equipment": "Équipement",
    },
    "de": {
        "user_title": "Riff-Wartung",
        "user_desc": "Wählen Sie die Marke des Geräts. Ein Eintrag pro Marke; Geräte fügen Sie danach beliebig hinzu.",
        "brand": "Marke",
        "already": "Diese Marke ist bereits konfiguriert.",
        "menu_add": "Gerät hinzufügen",
        "menu_edit": "Gerät bearbeiten",
        "menu_remove": "Gerät entfernen",
        "add_title": "Neues Gerät",
        "add_desc": "Benennen Sie es so, wie Sie es am Becken nennen, und wählen Sie das passendste Modell.",
        "name": "Name",
        "preset": "Modell",
        "tasks_title": "Aufgaben für {equipment}",
        "tasks_desc": "Die Aufgaben des Modells sind vorausgewählt — entfernen Sie, was nicht zutrifft. Eigene Aufgaben unten ergänzen.",
        "tasks": "Aufgaben",
        "custom_tasks": "Eigene Aufgaben",
        "edit_title": "Gerät bearbeiten",
        "edit_desc": "Welches Gerät?",
        "edit_eq_title": "{equipment} bearbeiten",
        "edit_eq_desc": "Intervalle werden hier nicht gesetzt: jede Aufgabe hat ihren eigenen Regler im Dashboard.",
        "remove_title": "Gerät entfernen",
        "remove_desc": "Seine Aufgaben und deren Verlauf werden gelöscht.",
        "equipment": "Gerät",
    },
    "es": {
        "user_title": "Mantenimiento de arrecife",
        "user_desc": "Elige la marca del equipo a seguir. Una entrada por marca; después añadirás tantos equipos como quieras.",
        "brand": "Marca",
        "already": "Esta marca ya está configurada.",
        "menu_add": "Añadir un equipo",
        "menu_edit": "Editar un equipo",
        "menu_remove": "Eliminar un equipo",
        "add_title": "Nuevo equipo",
        "add_desc": "Ponle el nombre con el que lo llamas frente al acuario y elige el modelo más parecido.",
        "name": "Nombre",
        "preset": "Modelo",
        "tasks_title": "Tareas de {equipment}",
        "tasks_desc": "Las tareas del modelo vienen preseleccionadas: desmarca lo que no aplique. Añade las tuyas abajo si falta algo.",
        "tasks": "Tareas",
        "custom_tasks": "Tareas personalizadas",
        "edit_title": "Editar un equipo",
        "edit_desc": "¿Qué equipo?",
        "edit_eq_title": "Editar {equipment}",
        "edit_eq_desc": "Los intervalos no se ajustan aquí: cada tarea tiene su propio deslizador en el panel.",
        "remove_title": "Eliminar un equipo",
        "remove_desc": "Sus tareas y su historial se eliminan.",
        "equipment": "Equipo",
    },
    "it": {
        "user_title": "Manutenzione reef",
        "user_desc": "Scegli la marca dell'apparecchiatura da seguire. Una voce per marca; poi aggiungi quante apparecchiature vuoi.",
        "brand": "Marca",
        "already": "Questa marca è già configurata.",
        "menu_add": "Aggiungi un'apparecchiatura",
        "menu_edit": "Modifica un'apparecchiatura",
        "menu_remove": "Rimuovi un'apparecchiatura",
        "add_title": "Nuova apparecchiatura",
        "add_desc": "Chiamala come la chiami davanti alla vasca, poi scegli il modello più vicino.",
        "name": "Nome",
        "preset": "Modello",
        "tasks_title": "Attività di {equipment}",
        "tasks_desc": "Le attività del modello sono preselezionate: deseleziona ciò che non serve. Aggiungi le tue qui sotto se manca qualcosa.",
        "tasks": "Attività",
        "custom_tasks": "Attività personalizzate",
        "edit_title": "Modifica un'apparecchiatura",
        "edit_desc": "Quale apparecchiatura?",
        "edit_eq_title": "Modifica {equipment}",
        "edit_eq_desc": "Gli intervalli non si impostano qui: ogni attività ha il suo cursore nella dashboard.",
        "remove_title": "Rimuovi un'apparecchiatura",
        "remove_desc": "Le sue attività e la loro cronologia vengono eliminate.",
        "equipment": "Apparecchiatura",
    },
    "nl": {
        "user_title": "Rif-onderhoud",
        "user_desc": "Kies het merk van de apparatuur. Eén item per merk; daarna voeg je zoveel apparaten toe als je wilt.",
        "brand": "Merk",
        "already": "Dit merk is al geconfigureerd.",
        "menu_add": "Apparaat toevoegen",
        "menu_edit": "Apparaat bewerken",
        "menu_remove": "Apparaat verwijderen",
        "add_title": "Nieuw apparaat",
        "add_desc": "Noem het zoals je het bij de bak noemt en kies het dichtstbijzijnde model.",
        "name": "Naam",
        "preset": "Model",
        "tasks_title": "Taken van {equipment}",
        "tasks_desc": "De taken van het model zijn voorgeselecteerd — vink uit wat niet van toepassing is. Voeg hieronder je eigen taken toe.",
        "tasks": "Taken",
        "custom_tasks": "Eigen taken",
        "edit_title": "Apparaat bewerken",
        "edit_desc": "Welk apparaat?",
        "edit_eq_title": "{equipment} bewerken",
        "edit_eq_desc": "Intervallen stel je hier niet in: elke taak heeft een eigen schuifregelaar op het dashboard.",
        "remove_title": "Apparaat verwijderen",
        "remove_desc": "De taken en hun geschiedenis worden verwijderd.",
        "equipment": "Apparaat",
    },
    "pl": {
        "user_title": "Konserwacja rafy",
        "user_desc": "Wybierz markę sprzętu. Jeden wpis na markę; sprzęty dodasz później w dowolnej liczbie.",
        "brand": "Marka",
        "already": "Ta marka jest już skonfigurowana.",
        "menu_add": "Dodaj sprzęt",
        "menu_edit": "Edytuj sprzęt",
        "menu_remove": "Usuń sprzęt",
        "add_title": "Nowy sprzęt",
        "add_desc": "Nazwij go tak, jak mówisz o nim przy zbiorniku, i wybierz najbliższy model.",
        "name": "Nazwa",
        "preset": "Model",
        "tasks_title": "Zadania dla {equipment}",
        "tasks_desc": "Zadania modelu są wstępnie zaznaczone — odznacz to, co nie dotyczy. Poniżej dodaj własne, jeśli czegoś brakuje.",
        "tasks": "Zadania",
        "custom_tasks": "Zadania własne",
        "edit_title": "Edytuj sprzęt",
        "edit_desc": "Który sprzęt?",
        "edit_eq_title": "Edytuj {equipment}",
        "edit_eq_desc": "Interwałów nie ustawia się tutaj: każde zadanie ma własny suwak na pulpicie.",
        "remove_title": "Usuń sprzęt",
        "remove_desc": "Jego zadania i ich historia zostaną usunięte.",
        "equipment": "Sprzęt",
    },
    "pt": {
        "user_title": "Manutenção de recife",
        "user_desc": "Escolha a marca do equipamento a seguir. Uma entrada por marca; depois adiciona os equipamentos que quiser.",
        "brand": "Marca",
        "already": "Esta marca já está configurada.",
        "menu_add": "Adicionar um equipamento",
        "menu_edit": "Editar um equipamento",
        "menu_remove": "Remover um equipamento",
        "add_title": "Novo equipamento",
        "add_desc": "Dê-lhe o nome que usa junto ao aquário e escolha o modelo mais próximo.",
        "name": "Nome",
        "preset": "Modelo",
        "tasks_title": "Tarefas de {equipment}",
        "tasks_desc": "As tarefas do modelo vêm pré-selecionadas — desmarque o que não se aplica. Adicione as suas abaixo se faltar algo.",
        "tasks": "Tarefas",
        "custom_tasks": "Tarefas personalizadas",
        "edit_title": "Editar um equipamento",
        "edit_desc": "Qual equipamento?",
        "edit_eq_title": "Editar {equipment}",
        "edit_eq_desc": "Os intervalos não se definem aqui: cada tarefa tem o seu cursor no painel.",
        "remove_title": "Remover um equipamento",
        "remove_desc": "As suas tarefas e o respetivo histórico são eliminados.",
        "equipment": "Equipamento",
    },
}

# Unit of a user-defined task (see CUSTOM_TASK in tasks.py).
CUSTOM_UNIT = "weeks"


def build(lang: str) -> dict:
    """Compose the whole translation tree for one language."""
    names = dict(zip(ORDER, NAMES[lang]))
    unit_word = UNITS[lang]
    flow = FLOW[lang]

    buttons, numbers, switches, dates = {}, {}, {}, {}
    for key, name in names.items():
        unit = TASK_UNITS[key]
        buttons[f"maint_{key}"] = {"name": name}
        numbers[f"maint_{key}_interval_{unit}"] = {
            "name": f"{name} ({unit_word[unit]})"
        }
        switches[f"maint_{key}_notify"] = {"name": f"{name} ({NOTIFY[lang]})"}
        dates[f"maint_{key}_last_reset"] = {"name": f"{name} ({LAST_DONE[lang]})"}

    # User-defined tasks: the label arrives as a placeholder, only the fixed
    # part is translated.
    buttons["maint_custom"] = {"name": "{task}"}
    numbers[f"maint_custom_interval_{CUSTOM_UNIT}"] = {
        "name": "{task} (" + unit_word[CUSTOM_UNIT] + ")"
    }
    switches["maint_custom_notify"] = {"name": "{task} (" + NOTIFY[lang] + ")"}
    dates["maint_custom_last_reset"] = {"name": "{task} (" + LAST_DONE[lang] + ")"}

    return {
        "config": {
            "step": {
                "user": {
                    "title": flow["user_title"],
                    "description": flow["user_desc"],
                    "data": {"brand": flow["brand"]},
                }
            },
            "abort": {"already_configured": flow["already"]},
        },
        "options": {
            "step": {
                "init": {
                    "title": flow["user_title"],
                    "menu_options": {
                        "add": flow["menu_add"],
                        "edit": flow["menu_edit"],
                        "remove": flow["menu_remove"],
                    },
                },
                "add": {
                    "title": flow["add_title"],
                    "description": flow["add_desc"],
                    "data": {"name": flow["name"], "preset": flow["preset"]},
                },
                "tasks": {
                    "title": flow["tasks_title"],
                    "description": flow["tasks_desc"],
                    "data": {
                        "tasks": flow["tasks"],
                        "custom_tasks": flow["custom_tasks"],
                    },
                },
                "edit": {
                    "title": flow["edit_title"],
                    "description": flow["edit_desc"],
                    "data": {"id": flow["equipment"]},
                },
                "edit_equipment": {
                    "title": flow["edit_eq_title"],
                    "description": flow["edit_eq_desc"],
                    "data": {
                        "name": flow["name"],
                        "tasks": flow["tasks"],
                        "custom_tasks": flow["custom_tasks"],
                    },
                },
                "remove": {
                    "title": flow["remove_title"],
                    "description": flow["remove_desc"],
                    "data": {"id": flow["equipment"]},
                },
            }
        },
        "entity": {
            "button": buttons,
            "number": numbers,
            "switch": switches,
            "date": dates,
        },
        # Same wording as the buttons: the task picker and the entity it
        # creates must read identically, or the user cannot match them.
        "selector": {"library_task": {"options": dict(names)}},
    }


def write(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"  wrote {os.path.relpath(path, REPO_ROOT)}")


def main() -> None:
    os.makedirs(TRANSLATIONS, exist_ok=True)
    for lang in LANGS:
        write(os.path.join(TRANSLATIONS, f"{lang}.json"), build(lang))
    # strings.json is the English source of truth shipped to Home Assistant.
    write(os.path.join(BASE, "strings.json"), build("en"))


if __name__ == "__main__":
    main()
