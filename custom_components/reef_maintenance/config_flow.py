"""Config and options flow.

One config entry per brand (Tunze, Jebao, generic), each holding as many
equipments as needed. Equipments are added, edited and removed from the
options flow; every change rewrites `entry.options`, which reloads the entry
and rebuilds the entity set.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_BRAND,
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_NAME,
    CONF_PRESET,
    CONF_TASKS,
    DOMAIN,
)
from .presets import BRANDS, get_preset, presets_for_brand
from .storage import next_equipment_id
from .tasks import LIBRARY


def _brand_selector() -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=[
                SelectOptionDict(value=key, label=label)
                for key, label in BRANDS.items()
            ],
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


def _preset_selector(brand: str) -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=[
                SelectOptionDict(value=preset.id, label=preset.model)
                for preset in presets_for_brand(brand)
            ],
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


def _task_selector() -> SelectSelector:
    """Multi-select over the whole library.

    Presets preselect their own tasks, but the list stays complete so a user
    can add, say, a probe calibration to a pump — or build a device from
    scratch. Labels are the library keys: the translated wording lives in the
    entity names, and a selector cannot reach entity translations.
    """
    return SelectSelector(
        SelectSelectorConfig(
            options=sorted(LIBRARY),
            mode=SelectSelectorMode.DROPDOWN,
            multiple=True,
            translation_key="library_task",
        )
    )


def _custom_tasks_selector() -> TextSelector:
    return TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT, multiple=True))


class ReefMaintenanceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create one entry per brand."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            # Annotated: user_input is dict[str, Any], and an Any brand makes
            # the title below Any too, which hides real type errors.
            brand: str = user_input[CONF_BRAND]
            # One entry per brand keeps the device tree readable and makes
            # equipment ids (`tunze_1`, `tunze_2`) unique by construction.
            await self.async_set_unique_id(brand)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=BRANDS.get(brand) or brand.capitalize(),
                data={CONF_BRAND: brand},
                options={CONF_EQUIPMENTS: []},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_BRAND): _brand_selector()}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        # Parameter name matches the base class: Home Assistant calls it
        # positionally today, but a keyword call would break on a rename.
        return ReefMaintenanceOptionsFlow()


class ReefMaintenanceOptionsFlow(OptionsFlow):
    """Add, edit and remove the equipments of a brand."""

    def __init__(self) -> None:
        self._equipment_id: str | None = None
        # Carries the name/preset from the "add" step to the "tasks" step.
        self._pending: dict[str, Any] = {}

    @property
    def _brand(self) -> str:
        return self.config_entry.data[CONF_BRAND]

    @property
    def _equipments(self) -> list[dict[str, Any]]:
        return list(self.config_entry.options.get(CONF_EQUIPMENTS, []))

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        menu = ["add"]
        if self._equipments:
            menu += ["edit", "remove"]
        return self.async_show_menu(step_id="init", menu_options=menu)

    # ---- add -------------------------------------------------------------

    async def async_step_add(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick a preset and a name, then confirm the task list."""
        if user_input is not None:
            self._pending = user_input
            return await self.async_step_tasks()

        return self.async_show_form(
            step_id="add",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_PRESET): _preset_selector(self._brand),
                }
            ),
        )

    async def async_step_tasks(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm which tasks apply, and add free-text ones."""
        preset = get_preset(self._pending[CONF_PRESET])
        if user_input is not None:
            equipment = {
                CONF_ID: next_equipment_id(
                    dict(self.config_entry.options), self._brand
                ),
                CONF_NAME: self._pending[CONF_NAME],
                CONF_PRESET: self._pending[CONF_PRESET],
                CONF_TASKS: user_input.get(CONF_TASKS, []),
                CONF_CUSTOM_TASKS: user_input.get(CONF_CUSTOM_TASKS, []),
            }
            return self._save(self._equipments + [equipment])

        # Preselected, not imposed: Tunze asks for the pump and the magnet
        # holder at the same interval, and some users would rather acknowledge
        # a single task.
        preselected = [spec.key for spec in (preset.tasks if preset else ())]
        return self.async_show_form(
            step_id="tasks",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_TASKS, default=preselected): _task_selector(),
                    vol.Optional(
                        CONF_CUSTOM_TASKS, default=[]
                    ): _custom_tasks_selector(),
                }
            ),
            description_placeholders={"equipment": self._pending[CONF_NAME]},
        )

    # ---- edit ------------------------------------------------------------

    async def async_step_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose which equipment to edit."""
        if user_input is not None:
            self._equipment_id = user_input[CONF_ID]
            return await self.async_step_edit_equipment()
        return self.async_show_form(
            step_id="edit",
            data_schema=vol.Schema({vol.Required(CONF_ID): self._equipment_selector()}),
        )

    async def async_step_edit_equipment(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Rename an equipment and change its task list.

        Intervals are not editable here: they are entities, adjustable from
        the dashboard without reloading anything.
        """
        current = next(
            item for item in self._equipments if item[CONF_ID] == self._equipment_id
        )
        if user_input is not None:
            updated = [
                {**item, **user_input} if item[CONF_ID] == self._equipment_id else item
                for item in self._equipments
            ]
            return self._save(updated)

        return self.async_show_form(
            step_id="edit_equipment",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=current[CONF_NAME]): str,
                    vol.Optional(
                        CONF_TASKS, default=current.get(CONF_TASKS, [])
                    ): _task_selector(),
                    vol.Optional(
                        CONF_CUSTOM_TASKS, default=current.get(CONF_CUSTOM_TASKS, [])
                    ): _custom_tasks_selector(),
                }
            ),
            description_placeholders={"equipment": current[CONF_NAME]},
        )

    # ---- remove ----------------------------------------------------------

    async def async_step_remove(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Remove an equipment and all of its tasks."""
        if user_input is not None:
            keep = [
                item
                for item in self._equipments
                if item[CONF_ID] != user_input[CONF_ID]
            ]
            return self._save(keep)
        return self.async_show_form(
            step_id="remove",
            data_schema=vol.Schema({vol.Required(CONF_ID): self._equipment_selector()}),
        )

    # ---- helpers ---------------------------------------------------------

    def _equipment_selector(self) -> SelectSelector:
        return SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value=item[CONF_ID], label=item[CONF_NAME])
                    for item in self._equipments
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        )

    def _save(self, equipments: list[dict[str, Any]]) -> ConfigFlowResult:
        """Write the new equipment list; the update listener reloads the entry."""
        return self.async_create_entry(
            data={**self.config_entry.options, CONF_EQUIPMENTS: equipments}
        )
