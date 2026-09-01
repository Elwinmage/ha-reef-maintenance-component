# Reef maintenance 🐙
> Parte dell'[**ecosistema ReefTech**](https://elwinmage.github.io/reeftank/)
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

# Lingue disponibili: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) [<img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/fr/README.fr.md) [<img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/de/README.de.md) [<img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/es/README.es.md) <img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/> [<img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/nl/README.nl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pl/README.pl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pt/README.pt.md)

Integrazione Home Assistant che tiene traccia delle attività di pulizia e usura dell'attrezzatura da acquario che Home Assistant **non può interrogare** — pompe di movimento, pompe di risalita, schiumatoi, reattori, tutto ciò che si pulisce a mano.

Pubblica lo stesso contratto di entità `reef_role` delle due integrazioni per dispositivi connessi, quindi le sue attività compaiono nella vista manutenzione della scheda accanto all'attrezzatura connessa, senza configurazione lato scheda.

<!-- ecosystem:start -->

## Progetti correlati

I progetti ReefTech si incastrano tra loro: le integrazioni portano la tua attrezzatura in Home Assistant, la scheda la mostra e la pilota, e il backup la mantiene in funzione durante un blackout. Ognuno funziona anche da solo.

<table>
  <tr>
    <th width="100px"></th>
    <th>Progetto</th>
    <th>Ruolo</th>
    <th>Funziona con</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td>🐠<br /><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Dispositivi Red Sea ReefBeat, pilotati in locale senza cloud: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun e ReefWave.<br />blueprint di allerta per modalità anomale, calibrazioni e batteria scarica. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td>🌊<br /><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Pompe Aqua Medic tramite l'API cloud Gizwits: pompe di movimento EcoDrift e SmartDrift, pompe DC Runner di risalita e dello schiumatoio.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td>🐙<br /><b>ha-reef-maintenance-component</b><br /><i>(questo repository)</i></td>
    <td>Tracciamento di pulizia e usura per l'attrezzatura che Home Assistant non può interrogare: pompe di movimento, pompe di risalita, schiumatoi, reattori, tutto ciò che curi a mano.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td>🪸<br /><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Vista grafica interattiva di ogni dispositivo sulla tua dashboard, e unico modo per modificare le programmazioni avanzate. Legge le tre integrazioni tramite il contratto <code>reef_role</code> comune, senza configurazione lato scheda.</td>
    <td>tutte e tre le integrazioni</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-blueprints/main/icon.png" width="64" alt="ha-reef-blueprints" /></td>
    <td>🐬<br /><a href="https://github.com/Elwinmage/ha-reef-blueprints"><b>ha-reef-blueprints</b></a></td>
    <td>Blueprint di notifica comuni a tutto l'ecosistema: manutenzioni scadute trovate tramite il contratto <code>reef_role</code>, e dispositivi diventati irraggiungibili. Otto lingue.</td>
    <td>tutte e tre le integrazioni</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td>⚡<br /><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Backup a batteria in caso di blackout. Un pacco 24V LiFePO₄ gestito da un Raspberry Pi, con degrado progressivo della velocità delle pompe in base allo stato di carica.</td>
    <td>da solo, o insieme a ha-reefbeat-component</td>
  </tr>
</table>

Sono tutti documentati insieme sulla [pagina del progetto ReefTech](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## Con ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

La vista manutenzione di [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) raccoglie tutte le attività di questa integrazione accanto a quelle dei dispositivi connessi. Ordina per attrezzatura o per scadenza, le scadute per prime; premi una riga e il lavoro viene registrato.

Nulla da configurare lato scheda: trova le attività tramite l'attributo `reef_role`, quindi un'attrezzatura aggiunta qui compare lì al successivo aggiornamento.

Le attività scadute possono anche arrivare sul telefono: il blueprint [Reef maintenance watch](https://github.com/Elwinmage/ha-reef-blueprints) le trova tramite lo stesso attributo `reef_role` e rispetta gli interruttori di notifica per attività.

[![Guarda il video](https://img.youtube.com/vi/Ko46fHonOP4/0.jpg)](https://www.youtube.com/watch?v=Ko46fHonOP4)

## Installazione

### Installazione diretta

Cliccate qui per aprire il repository direttamente in HACS e premete «Download»: [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Elwinmage&repository=ha-reef-maintenance-component&category=integration)

### Cercare in HACS

Oppure cercate «reef-maintenance» in HACS.

## Come funziona

Una voce di configurazione per **marca**, un dispositivo per **attrezzatura**, quattro entità per **attività**:

| Entità | Ruolo |
|---|---|
| Pulsante | Registra il lavoro svolto e porta `days_left`, `overdue`, `interval_days`, `task_key`, `notify` come attributi |
| Numero | Intervallo, nell'unità naturale dell'attività (giorni, settimane o mesi) |
| Interruttore | Silenzia gli avvisi di scadenza per quell'attività |
| Data | Retrodata l'ultimo intervento |

L'entità data conta più di quanto sembri: senza di essa ogni attività parte da «mai fatta» il giorno in cui aggiungi l'attrezzatura, e scadono tutte lo stesso pomeriggio tre mesi dopo.

## Preset

| Marca | Modello | Attività |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | pompa, supporto magnetico, decalcificazione, parti di usura |
| Tunze | Turbelle nanostream | pompa, supporto magnetico, decalcificazione, parti di usura |
| Tunze | Silence / Silence PRO | filtro, pompa, decalcificazione, parti di usura |
| Jebao | SLW / MLW / SCP / SOW | pompa, supporto magnetico, decalcificazione, parti di usura |
| Jebao | DCP / MDP | filtro, pompa, decalcificazione, parti di usura |
| Generico | Pompa di movimento DC | pompa, supporto magnetico, decalcificazione, parti di usura |
| Generico | Pompa di risalita DC | filtro, pompa, decalcificazione, parti di usura |
| Generico | Schiumatoio a girante ad aghi | bicchiere, venturi, girante ad aghi, decalcificazione, parti di usura |
| Generico | Attrezzatura personalizzata | nessuna — scegli dalla libreria o scrivi la tua |

Gli intervalli seguono il produttore quando pubblica un dato (Tunze Turbelle: pompa e supporto magnetico ogni 1–2 mesi; Tunze Silence: pulizia completa almeno annuale; Jebao DCP: girante mensile; Jebao SLW: mensile o bimestrale) e la pratica di acquariofilia altrimenti. Sono tutti punti di partenza, modificabili per singola attrezzatura.

Le attività provengono da una libreria comune di 17 voci, tradotta in 8 lingue. Un preset si limita a referenziare chiavi della libreria e può ridefinire i limiti dell'intervallo — per questo aggiungere una marca di solito non costa alcuna nuova stringa di traduzione.

## Servizio

`reef_maintenance.reset` segna un'attività come svolta da un'automazione. Attacca un tag NFC vicino alla pompa, scansionalo a lavoro finito, e l'attività è confermata senza aprire una dashboard.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Sviluppo

`scripts/gen_readme.py` rigenera questa pagina e le sue sette traduzioni, e `scripts/gen_translations.py` rigenera `strings.json` e gli 8 file di lingua da un'unica tabella sorgente — oltre 800 stringhe composte da una formulazione per attività e per lingua. Eseguili dopo aver toccato la libreria delle attività e committa il risultato.

### Test

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

La suite copre interamente il pacchetto e la CI lo mantiene tale. Vale la pena sapere cosa protegge, perché la maggior parte è invisibile a runtime:

- **Chiavi e unità delle attività.** Una chiave finisce nell'`unique_id` dell'entità e nella chiave di archiviazione, quindi rinominarla perde lo storico dei reset. Un'unità sbagliata cambia in silenzio il significato di un cursore di intervallo.
- **`reef_role`.** L'attributo che ha-reef-card cerca. Se il suo prefisso cambia, la vista manutenzione resta vuota senza alcun errore.
- **Aritmetica dei giorni.** `compute_days_left` arrotonda allontanandosi da zero in entrambe le direzioni, e «mai reimpostata» è `None`, non scaduta. Tutti i consumatori leggono quei valori.
- **Collisioni di slug.** Due attività personalizzate le cui etichette si slugificano allo stesso modo condividerebbero un `unique_id`, e Home Assistant scarterebbe uno dei due set di entità senza dirlo.
