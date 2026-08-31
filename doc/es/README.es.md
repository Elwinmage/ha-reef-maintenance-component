# Reef maintenance 🐙
> Parte del [**ecosistema ReefTech**](https://elwinmage.github.io/reeftank/)
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

# Idiomas disponibles: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) [<img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/fr/README.fr.md) [<img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/de/README.de.md) <img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/> [<img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/it/README.it.md) [<img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/nl/README.nl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pl/README.pl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pt/README.pt.md)

Integración de Home Assistant que sigue las tareas de limpieza y desgaste del equipo de acuario que Home Assistant **no puede consultar** — bombas de movimiento, bombas de retorno, skimmers, reactores, todo lo que se limpia a mano.

Publica el mismo contrato de entidades `reef_role` que las dos integraciones de dispositivos conectados, así que sus tareas aparecen en la vista de mantenimiento de la tarjeta junto al equipo conectado, sin configuración del lado de la tarjeta.

<!-- ecosystem:start -->

## Proyectos relacionados

Los proyectos ReefTech encajan entre sí: las integraciones traen tu equipo a Home Assistant, la tarjeta lo muestra y lo controla, y el respaldo lo mantiene en marcha durante un corte. Cada uno funciona también por su cuenta.

<table>
  <tr>
    <th width="100px"></th>
    <th>Proyecto</th>
    <th>Función</th>
    <th>Funciona con</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Dispositivos Red Sea ReefBeat, controlados localmente sin cloud: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun y ReefWave.<br />blueprint de alertas para modos anómalos, calibraciones y batería baja. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Bombas Aqua Medic a través de la API cloud Gizwits: bombas de movimiento EcoDrift y SmartDrift, bombas DC Runner de retorno y de skimmer.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td><b>ha-reef-maintenance-component</b><br /><i>(este repositorio)</i></td>
    <td>Seguimiento de limpieza y desgaste del equipo que Home Assistant no puede consultar: bombas de movimiento, bombas de retorno, skimmers, reactores, todo lo que mantienes a mano.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Vista gráfica interactiva de cada dispositivo en tu panel, y la única forma de editar programaciones avanzadas. Lee las tres integraciones mediante el contrato <code>reef_role</code> común, sin configuración del lado de la tarjeta.</td>
    <td>las tres integraciones</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-blueprints/main/icon.png" width="64" alt="ha-reef-blueprints" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-blueprints"><b>ha-reef-blueprints</b></a></td>
    <td>Blueprints de notificación comunes a todo el ecosistema: mantenimientos vencidos encontrados por el contrato <code>reef_role</code>, y dispositivos que dejaron de responder. Ocho idiomas.</td>
    <td>las tres integraciones</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Respaldo por batería ante cortes de luz. Un pack 24V LiFePO₄ gobernado por una Raspberry Pi, con degradación progresiva de la velocidad de las bombas según el estado de carga.</td>
    <td>por su cuenta, o junto a ha-reefbeat-component</td>
  </tr>
</table>

Todos están documentados juntos en la [página del proyecto ReefTech](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## Con ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

La vista de mantenimiento de [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) reúne todas las tareas de esta integración junto a las de los dispositivos conectados. Ordena por equipo o por vencimiento, las vencidas primero; pulsa una fila y el trabajo queda registrado.

Nada que configurar en la tarjeta: encuentra las tareas por el atributo `reef_role`, así que un equipo añadido aquí aparece allí en la siguiente actualización.

Las tareas vencidas también pueden llegar a su móvil: el blueprint [Reef maintenance watch](https://github.com/Elwinmage/ha-reef-blueprints) las encuentra por ese mismo atributo `reef_role` y respeta los interruptores de notificación por tarea.

[![Ver el vídeo](https://img.youtube.com/vi/__A_DEFINIR__/0.jpg)](https://www.youtube.com/watch?v=__A_DEFINIR__)

## Cómo funciona

Una entrada de configuración por **marca**, un dispositivo por **equipo**, cuatro entidades por **tarea**:

| Entidad | Función |
|---|---|
| Botón | Registra el trabajo hecho y lleva `days_left`, `overdue`, `interval_days`, `task_key`, `notify` como atributos |
| Número | Intervalo, en la unidad natural de la tarea (días, semanas o meses) |
| Interruptor | Silencia los avisos de vencimiento de esa tarea |
| Fecha | Retrodata la última intervención |

La entidad de fecha importa más de lo que parece: sin ella cada tarea arranca en «nunca hecha» el día que añades el equipo, y todas vencen la misma tarde tres meses después.

## Preajustes

| Marca | Modelo | Tareas |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | bomba, soporte magnético, descalcificar, piezas de desgaste |
| Tunze | Turbelle nanostream | bomba, soporte magnético, descalcificar, piezas de desgaste |
| Tunze | Silence / Silence PRO | filtro, bomba, descalcificar, piezas de desgaste |
| Jebao | SLW / MLW / SCP / SOW | bomba, soporte magnético, descalcificar, piezas de desgaste |
| Jebao | DCP / MDP | filtro, bomba, descalcificar, piezas de desgaste |
| Genérico | Bomba de movimiento DC | bomba, soporte magnético, descalcificar, piezas de desgaste |
| Genérico | Bomba de retorno DC | filtro, bomba, descalcificar, piezas de desgaste |
| Genérico | Skimmer de rotor de agujas | vaso, venturi, rotor de agujas, descalcificar, piezas de desgaste |
| Genérico | Equipo personalizado | ninguna — elige de la biblioteca o escribe la tuya |

Los intervalos siguen al fabricante cuando publica una cifra (Tunze Turbelle: bomba y soporte magnético cada 1–2 meses; Tunze Silence: limpieza completa al menos anual; Jebao DCP: rotor mensual; Jebao SLW: mensual a bimestral) y la práctica del arrecife en los demás casos. Todos son puntos de partida modificables por equipo.

Las tareas vienen de una biblioteca común de 17 entradas, traducida a 8 idiomas. Un preajuste solo referencia claves de la biblioteca y puede redefinir los límites del intervalo — por eso añadir una marca no suele costar ninguna cadena de traducción nueva.

## Servicio

`reef_maintenance.reset` marca una tarea como hecha desde una automatización. Pega una etiqueta NFC junto a la bomba, léela al terminar, y la tarea queda reconocida sin abrir un panel.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Desarrollo

`scripts/gen_readme.py` regenera esta página y sus siete traducciones, y `scripts/gen_translations.py` regenera `strings.json` y los 8 archivos de idioma desde una única tabla fuente — más de 800 cadenas compuestas a partir de una redacción por tarea e idioma. Ejecútalos tras tocar la biblioteca de tareas y confirma el resultado.

### Pruebas

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

La suite cubre el paquete por completo y la CI lo mantiene así. Vale la pena saber qué protege, porque casi todo es invisible en ejecución:

- **Claves y unidades de tarea.** Una clave acaba en el `unique_id` de la entidad y en la clave de almacenamiento, así que renombrarla pierde el historial de reinicios. Una unidad equivocada cambia en silencio el significado de un deslizador de intervalo.
- **`reef_role`.** El atributo que busca ha-reef-card. Si cambia su prefijo, la vista de mantenimiento se queda vacía sin ningún error.
- **Aritmética de días.** `compute_days_left` redondea alejándose de cero en ambos sentidos, y «nunca reiniciada» es `None`, no vencida. Todos los consumidores leen esos valores.
- **Colisiones de slug.** Dos tareas personalizadas cuyas etiquetas se convierten al mismo slug compartirían un `unique_id`, y Home Assistant descartaría uno de los dos conjuntos de entidades sin decirlo.
