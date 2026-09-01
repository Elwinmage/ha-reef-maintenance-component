# Reef maintenance 🐙
> Część [**ekosystemu ReefTech**](https://elwinmage.github.io/reeftank/)
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

# Dostępne języki: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) [<img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/fr/README.fr.md) [<img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/de/README.de.md) [<img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/es/README.es.md) [<img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/it/README.it.md) [<img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/nl/README.nl.md) <img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/> [<img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pt/README.pt.md)

Integracja Home Assistant śledząca zadania czyszczenia i zużycia sprzętu akwariowego, z którym Home Assistant **nie może się komunikować** — pompy cyrkulacyjne, pompy obiegowe, odpieniacze, reaktory, wszystko co czyścisz ręcznie.

Publikuje ten sam kontrakt encji `reef_role` co dwie integracje urządzeń podłączonych, więc jej zadania pojawiają się w widoku konserwacji karty obok sprzętu podłączonego, bez konfiguracji po stronie karty.

<!-- ecosystem:start -->

## Powiązane projekty

Projekty ReefTech uzupełniają się: integracje wprowadzają sprzęt do Home Assistant, karta go wyświetla i steruje nim, a zasilanie awaryjne utrzymuje go w ruchu podczas przerwy w zasilaniu. Każdy działa również samodzielnie.

<table>
  <tr>
    <th width="100px"></th>
    <th>Projekt</th>
    <th>Rola</th>
    <th>Współpracuje z</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td>🐠<br /><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Urządzenia Red Sea ReefBeat, sterowane lokalnie bez chmury: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun i ReefWave.<br />blueprint alertów dla nietypowych trybów, kalibracji i niskiego poziomu baterii. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td>🌊<br /><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Pompy Aqua Medic przez chmurowe API Gizwits: pompy cyrkulacyjne EcoDrift i SmartDrift, pompy DC Runner obiegowe i do odpieniacza.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td>🐙<br /><b>ha-reef-maintenance-component</b><br /><i>(to repozytorium)</i></td>
    <td>Śledzenie czyszczenia i zużycia sprzętu, do którego Home Assistant nie ma dostępu: pompy cyrkulacyjne, pompy obiegowe, odpieniacze, reaktory, wszystko co obsługujesz ręcznie.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td>🪸<br /><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Interaktywny widok graficzny każdego urządzenia na pulpicie i jedyny sposób edycji zaawansowanych harmonogramów. Odczytuje trzy integracje przez wspólny kontrakt <code>reef_role</code>, bez konfiguracji po stronie karty.</td>
    <td>wszystkie trzy integracje</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-blueprints/main/icon.png" width="64" alt="ha-reef-blueprints" /></td>
    <td>🐬<br /><a href="https://github.com/Elwinmage/ha-reef-blueprints"><b>ha-reef-blueprints</b></a></td>
    <td>Blueprinty powiadomień wspólne dla całego ekosystemu: zaległe konserwacje znajdowane przez kontrakt <code>reef_role</code> oraz urządzenia, które przestały odpowiadać. Osiem języków.</td>
    <td>wszystkie trzy integracje</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td>⚡<br /><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Zasilanie awaryjne na wypadek przerw w zasilaniu. Pakiet 24V LiFePO₄ sterowany przez Raspberry Pi, ze stopniowym obniżaniem prędkości pomp zależnie od stanu naładowania.</td>
    <td>samodzielnie lub razem z ha-reefbeat-component</td>
  </tr>
</table>

Wszystkie są udokumentowane razem na [stronie projektu ReefTech](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## Z ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

Widok konserwacji [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) zbiera wszystkie zadania tej integracji obok zadań urządzeń podłączonych. Sortuj według sprzętu lub terminu, zaległe najpierw; naciśnij wiersz, a praca zostanie zapisana.

Po stronie karty nie ma nic do ustawienia: znajduje zadania przez atrybut `reef_role`, więc sprzęt dodany tutaj pojawi się tam przy następnym odświeżeniu.

Zaległe zadania mogą też trafić na telefon: blueprint [Reef maintenance watch](https://github.com/Elwinmage/ha-reef-blueprints) znajduje je przez ten sam atrybut `reef_role` i respektuje przełączniki powiadomień poszczególnych zadań.

[![Obejrzyj wideo](https://img.youtube.com/vi/Ko46fHonOP4/0.jpg)](https://www.youtube.com/watch?v=Ko46fHonOP4)

## Instalacja

### Bezpośrednia instalacja

Kliknij tutaj, aby otworzyć repozytorium bezpośrednio w HACS i kliknij «Pobierz»: [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Elwinmage&repository=ha-reef-maintenance-component&category=integration)

### Szukaj w HACS

Lub wyszukaj «reef-maintenance» w HACS.

## Jak to działa

Jeden wpis konfiguracji na **markę**, jedno urządzenie na **sprzęt**, cztery encje na **zadanie**:

| Encja | Rola |
|---|---|
| Przycisk | Zapisuje wykonanie pracy i niesie `days_left`, `overdue`, `interval_days`, `task_key`, `notify` jako atrybuty |
| Liczba | Interwał, w naturalnej jednostce zadania (dni, tygodnie lub miesiące) |
| Przełącznik | Wycisza powiadomienia o zaległości tego zadania |
| Data | Wstecznie datuje ostatnią interwencję |

Encja daty znaczy więcej, niż się wydaje: bez niej każde zadanie startuje od „nigdy nie wykonano" w dniu dodania sprzętu, a wszystkie stają się wymagalne tego samego popołudnia trzy miesiące później.

## Ustawienia wstępne

| Marka | Model | Zadania |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | pompa, uchwyt magnetyczny, odkamienianie, części zużywalne |
| Tunze | Turbelle nanostream | pompa, uchwyt magnetyczny, odkamienianie, części zużywalne |
| Tunze | Silence / Silence PRO | sitko, pompa, odkamienianie, części zużywalne |
| Jebao | SLW / MLW / SCP / SOW | pompa, uchwyt magnetyczny, odkamienianie, części zużywalne |
| Jebao | DCP / MDP | sitko, pompa, odkamienianie, części zużywalne |
| Generyczne | Pompa cyrkulacyjna DC | pompa, uchwyt magnetyczny, odkamienianie, części zużywalne |
| Generyczne | Pompa obiegowa DC | sitko, pompa, odkamienianie, części zużywalne |
| Generyczne | Odpieniacz z wirnikiem igiełkowym | kubek, venturi, wirnik igiełkowy, odkamienianie, części zużywalne |
| Generyczne | Sprzęt własny | brak — wybierz z biblioteki lub wpisz własne |

Interwały idą za producentem tam, gdzie podaje liczbę (Tunze Turbelle: pompa i uchwyt magnetyczny co 1–2 miesiące; Tunze Silence: pełne czyszczenie co najmniej raz w roku; Jebao DCP: wirnik co miesiąc; Jebao SLW: co miesiąc do co dwa miesiące), a poza tym za praktyką rafową. Wszystkie są punktami wyjścia, zmiennymi dla każdego sprzętu.

Zadania pochodzą ze wspólnej biblioteki 17 pozycji, przetłumaczonej na 8 języków. Ustawienie wstępne tylko odwołuje się do kluczy biblioteki i może nadpisać granice interwału — dlatego dodanie marki zwykle nie kosztuje żadnego nowego ciągu tłumaczenia.

## Usługa

`reef_maintenance.reset` oznacza zadanie jako wykonane z poziomu automatyzacji. Przyklej tag NFC przy pompie, zeskanuj go po zakończeniu, a zadanie zostanie potwierdzone bez otwierania pulpitu.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Rozwój

`scripts/gen_readme.py` generuje tę stronę i jej siedem tłumaczeń, a `scripts/gen_translations.py` generuje `strings.json` i 8 plików językowych z jednej tabeli źródłowej — ponad 800 ciągów złożonych z jednego sformułowania na zadanie i język. Uruchom je po zmianie biblioteki zadań i zatwierdź wynik.

### Testy

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

Zestaw pokrywa pakiet w całości, a CI tego pilnuje. Warto wiedzieć, czego strzeże, bo większość jest niewidoczna w działaniu:

- **Klucze i jednostki zadań.** Klucz trafia do `unique_id` encji i do klucza magazynu, więc zmiana nazwy gubi historię resetów. Zła jednostka po cichu zmienia znaczenie suwaka interwału.
- **`reef_role`.** Atrybut, którego szuka ha-reef-card. Jeśli zmieni się jego przedrostek, widok konserwacji pozostanie pusty bez żadnego błędu.
- **Arytmetyka dni.** `compute_days_left` zaokrągla w obie strony od zera, a „nigdy nie zresetowano" to `None`, a nie zaległość. Wszyscy odbiorcy czytają te wartości.
- **Kolizje slugów.** Dwa własne zadania, których etykiety dają ten sam slug, dzieliłyby jeden `unique_id`, a Home Assistant bez słowa porzuciłby jeden z dwóch zestawów encji.
