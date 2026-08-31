# Reef maintenance 🐙
> Parte do [**ecossistema ReefTech**](https://elwinmage.github.io/reeftank/)
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

# Idiomas disponíveis: [<img src="https://flagicons.lipis.dev/flags/4x3/gb.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/README.md) [<img src="https://flagicons.lipis.dev/flags/4x3/fr.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/fr/README.fr.md) [<img src="https://flagicons.lipis.dev/flags/4x3/de.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/de/README.de.md) [<img src="https://flagicons.lipis.dev/flags/4x3/es.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/es/README.es.md) [<img src="https://flagicons.lipis.dev/flags/4x3/it.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/it/README.it.md) [<img src="https://flagicons.lipis.dev/flags/4x3/nl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/nl/README.nl.md) [<img src="https://flagicons.lipis.dev/flags/4x3/pl.svg" width="5%"/>](https://github.com/Elwinmage/ha-reef-maintenance-component/blob/main/doc/pl/README.pl.md) <img src="https://flagicons.lipis.dev/flags/4x3/pt.svg" width="5%"/>

Integração Home Assistant que acompanha as tarefas de limpeza e desgaste do equipamento de aquário que o Home Assistant **não consegue interrogar** — bombas de circulação, bombas de retorno, escumadores, reatores, tudo o que limpa à mão.

Publica o mesmo contrato de entidades `reef_role` que as duas integrações de aparelhos ligados, por isso as suas tarefas aparecem na vista de manutenção do cartão ao lado do equipamento ligado, sem configuração do lado do cartão.

<!-- ecosystem:start -->

## Projetos relacionados

Os projetos ReefTech encaixam-se entre si: as integrações trazem o seu equipamento para o Home Assistant, o cartão mostra-o e comanda-o, e o backup mantém-no a funcionar durante um corte. Cada um funciona também sozinho.

<table>
  <tr>
    <th width="100px"></th>
    <th>Projeto</th>
    <th>Função</th>
    <th>Funciona com</th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/main/icon.png" width="64" alt="ha-reefbeat-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reefbeat-component"><b>ha-reefbeat-component</b></a></td>
    <td>Aparelhos Red Sea ReefBeat, comandados localmente sem cloud: ReefATO+, ReefControl, ReefControl-Power, ReefDose, ReefLed, ReefMat, ReefRun e ReefWave.<br />blueprint de alertas para modos anómalos, calibrações e bateria fraca. <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Elwinmage/ha-reefbeat-component/refs/heads/main/blueprints/automation/redsea_alerts.en.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled." /></a></td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-aquamedic-component/main/icon.png" width="64" alt="ha-aquamedic-component" /></td>
    <td><a href="https://github.com/Elwinmage/ha-aquamedic-component"><b>ha-aquamedic-component</b></a></td>
    <td>Bombas Aqua Medic através da API cloud Gizwits: bombas de circulação EcoDrift e SmartDrift, bombas DC Runner de retorno e do escumador.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-maintenance-component/main/icon.png" width="64" alt="ha-reef-maintenance-component" /></td>
    <td><b>ha-reef-maintenance-component</b><br /><i>(este repositório)</i></td>
    <td>Acompanhamento da limpeza e do desgaste do equipamento que o Home Assistant não consegue interrogar: bombas de circulação, bombas de retorno, escumadores, reatores, tudo o que trata à mão.</td>
    <td>ha-reef-card</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-card/main/icon.png" width="64" alt="ha-reef-card" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-card"><b>ha-reef-card</b></a></td>
    <td>Vista gráfica interativa de cada aparelho no seu painel, e a única forma de editar os programas avançados. Lê as três integrações através do contrato <code>reef_role</code> comum, sem configuração do lado do cartão.</td>
    <td>as três integrações</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/ha-reef-blueprints/main/icon.png" width="64" alt="ha-reef-blueprints" /></td>
    <td><a href="https://github.com/Elwinmage/ha-reef-blueprints"><b>ha-reef-blueprints</b></a></td>
    <td>Blueprints de notificação comuns a todo o ecossistema: manutenções em atraso encontradas pelo contrato <code>reef_role</code>, e aparelhos que ficaram inacessíveis. Oito idiomas.</td>
    <td>as três integrações</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Elwinmage/reefbeatEnergyBackup/main/icon.png" width="64" alt="reefbeatEnergyBackup" /></td>
    <td><a href="https://github.com/Elwinmage/reefbeatEnergyBackup"><b>reefbeatEnergyBackup</b></a></td>
    <td>Backup por bateria em caso de corte. Um pack 24V LiFePO₄ comandado por um Raspberry Pi, com degradação progressiva da velocidade das bombas conforme o estado de carga.</td>
    <td>sozinho, ou a par do ha-reefbeat-component</td>
  </tr>
</table>

Estão todos documentados em conjunto na [página do projeto ReefTech](https://elwinmage.github.io/reeftank/).

<!-- ecosystem:end -->

## Com o ha-reef-card

<p align="center">
  <img src="https://github.com/Elwinmage/ha-reef-card/raw/main/doc/img/maintenance/overview.png" width="90%"/>
</p>

A vista de manutenção do [ha-reef-card](https://github.com/Elwinmage/ha-reef-card) reúne todas as tarefas desta integração ao lado das dos aparelhos ligados. Ordene por equipamento ou por prazo, as vencidas primeiro; prima uma linha e o trabalho fica registado.

Nada a configurar do lado do cartão: encontra as tarefas pelo atributo `reef_role`, por isso um equipamento aqui adicionado aparece lá na atualização seguinte.

As tarefas em atraso também podem chegar ao seu telemóvel: o blueprint [Reef maintenance watch](https://github.com/Elwinmage/ha-reef-blueprints) encontra-as pelo mesmo atributo `reef_role` e respeita os interruptores de notificação por tarefa.

[![Ver o vídeo](https://img.youtube.com/vi/__A_DEFINIR__/0.jpg)](https://www.youtube.com/watch?v=__A_DEFINIR__)

## Como funciona

Uma entrada de configuração por **marca**, um aparelho por **equipamento**, quatro entidades por **tarefa**:

| Entidade | Função |
|---|---|
| Botão | Regista o trabalho feito e transporta `days_left`, `overdue`, `interval_days`, `task_key`, `notify` como atributos |
| Número | Intervalo, na unidade natural da tarefa (dias, semanas ou meses) |
| Interruptor | Silencia os avisos de atraso dessa tarefa |
| Data | Retroage a última intervenção |

A entidade de data conta mais do que parece: sem ela cada tarefa começa em «nunca feita» no dia em que adiciona o equipamento, e todas vencem na mesma tarde três meses depois.

## Predefinições

| Marca | Modelo | Tarefas |
|---|---|---|
| Tunze | Turbelle stream / stream 3 | bomba, suporte magnético, descalcificar, peças de desgaste |
| Tunze | Turbelle nanostream | bomba, suporte magnético, descalcificar, peças de desgaste |
| Tunze | Silence / Silence PRO | filtro, bomba, descalcificar, peças de desgaste |
| Jebao | SLW / MLW / SCP / SOW | bomba, suporte magnético, descalcificar, peças de desgaste |
| Jebao | DCP / MDP | filtro, bomba, descalcificar, peças de desgaste |
| Genérico | Bomba de circulação DC | bomba, suporte magnético, descalcificar, peças de desgaste |
| Genérico | Bomba de retorno DC | filtro, bomba, descalcificar, peças de desgaste |
| Genérico | Escumador de rotor de agulhas | copo, venturi, rotor de agulhas, descalcificar, peças de desgaste |
| Genérico | Equipamento personalizado | nenhuma — escolha da biblioteca ou escreva a sua |

Os intervalos seguem o fabricante sempre que publica um valor (Tunze Turbelle: bomba e suporte magnético a cada 1–2 meses; Tunze Silence: limpeza completa pelo menos anual; Jebao DCP: rotor mensal; Jebao SLW: mensal a bimestral) e a prática de recife nos restantes casos. São todos pontos de partida, alteráveis por equipamento.

As tarefas vêm de uma biblioteca comum de 17 entradas, traduzida em 8 idiomas. Uma predefinição apenas referencia chaves da biblioteca e pode redefinir os limites do intervalo — daí que acrescentar uma marca não costume custar qualquer nova cadeia de tradução.

## Serviço

`reef_maintenance.reset` marca uma tarefa como feita a partir de uma automação. Cole uma etiqueta NFC junto à bomba, leia-a quando terminar, e a tarefa fica confirmada sem abrir um painel.

```yaml
action: reef_maintenance.reset
target:
  entity_id: button.brassage_gauche_nettoyer_le_rotor_et_la_chambre_de_pompe
```

## Desenvolvimento

`scripts/gen_readme.py` regenera esta página e as suas sete traduções, e `scripts/gen_translations.py` regenera `strings.json` e os 8 ficheiros de idioma a partir de uma única tabela de origem — mais de 800 cadeias compostas a partir de uma redação por tarefa e por idioma. Execute-os depois de mexer na biblioteca de tarefas e faça commit do resultado.

### Testes

```bash
pip install -r requirements.test.txt
pytest -q --cov=custom_components.reef_maintenance --cov-config=.coveragerc \
       --cov-report=term-missing
```

A suite cobre o pacote por completo e a CI mantém-no assim. Vale a pena saber o que protege, porque a maior parte é invisível em execução:

- **Chaves e unidades das tarefas.** Uma chave acaba no `unique_id` da entidade e na chave de armazenamento, por isso renomeá-la perde o histórico de reinícios. Uma unidade errada muda em silêncio o significado de um cursor de intervalo.
- **`reef_role`.** O atributo que o ha-reef-card procura. Se o seu prefixo mudar, a vista de manutenção fica vazia sem qualquer erro.
- **Aritmética dos dias.** `compute_days_left` arredonda afastando-se de zero nos dois sentidos, e «nunca reiniciada» é `None` e não vencida. Todos os consumidores leem esses valores.
- **Colisões de slug.** Duas tarefas personalizadas cujas etiquetas dão o mesmo slug partilhariam um `unique_id`, e o Home Assistant descartaria um dos dois conjuntos de entidades sem o dizer.
