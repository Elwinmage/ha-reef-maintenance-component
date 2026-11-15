"""Config and options flow.

One config entry per brand (from the catalog: Tunze, Jebao, Eheim, generic…),
each holding as many equipments as needed. An equipment references a catalog
item or category; its tasks are resolved from the catalog. Equipments are
added, edited and removed from the options flow; every change rewrites
`entry.options`, which reloads the entry and rebuilds the entity set.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

from .catalog import (
    CATALOG_UNIQUE_ID,
    CONF_CATALOG,
    async_catalog_view,
    brands,
    choices,
    is_catalog_entry,
    model_label,
    resolve_equipment_tasks,
)
from .const import (
    CONF_BRAND,
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_MODEL,
    CONF_NAME,
    CONF_SOURCE,
    CONF_TASKS,
    DOMAIN,
)
from .storage import next_equipment_id

# Home Assistant validates with probatio, voluptuous being only an alias of it
# at runtime (2026.9), and types its flow helpers with probatio schemas since
# 2026.10. Older versions only have voluptuous.
if TYPE_CHECKING:
    import probatio as vol
else:
    try:
        import probatio as vol
    except ImportError:  # pragma: no cover - depends on the installed HA version
        import voluptuous as vol


def _dropdown(options: list[SelectOptionDict]) -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
    )


def _task_selector(options: list[SelectOptionDict]) -> SelectSelector:
    """Multi-select over the tasks the chosen equipment would get.

    Preselected, not imposed: a user can drop a task they do not care about, or
    add a catalog task the model does not list by editing later.
    """
    return SelectSelector(
        SelectSelectorConfig(
            options=options, mode=SelectSelectorMode.DROPDOWN, multiple=True
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
        view = await async_catalog_view(self.hass)
        labels = brands(view)
        if user_input is not None:
            # Annotated: user_input is dict[str, Any], and an Any brand makes
            # the title below Any too, which hides real type errors.
            brand: str = user_input[CONF_BRAND]
            # One entry per brand keeps the device tree readable and makes
            # equipment ids (`tunze_1`, `tunze_2`) unique by construction.
            await self.async_set_unique_id(brand)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=labels.get(brand) or brand.capitalize(),
                data={CONF_BRAND: brand},
                options={CONF_EQUIPMENTS: []},
            )

        options = [
            SelectOptionDict(value=key, label=label) for key, label in labels.items()
        ]
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_BRAND): _dropdown(options)}),
        )

    async def async_step_catalog(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the single, hidden equipment-catalog entry on request."""
        await self.async_set_unique_id(CATALOG_UNIQUE_ID)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="ReefTech equipment catalog", data={CONF_CATALOG: True}
        )

    @classmethod
    @callback
    def async_supports_options_flow(cls, config_entry: ConfigEntry) -> bool:
        # The catalog entry has no equipments to manage. Base method is a
        # classmethod, so this override must be one too.
        return not is_catalog_entry(config_entry)

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
        # Carries the name/source from the "add" step to the "tasks" step.
        self._pending: dict[str, Any] = {}

    @property
    def _brand(self) -> str:
        return self.config_entry.data[CONF_BRAND]

    @property
    def _lang(self) -> str:
        return self.hass.config.language

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
        """Pick a model (catalog item or generic category) and a name."""
        if user_input is not None:
            self._pending = user_input
            return await self.async_step_tasks()

        view = await async_catalog_view(self.hass)
        options = [
            SelectOptionDict(value=value, label=label)
            for value, label in choices(view, self._brand, self._lang)
        ]
        return self.async_show_form(
            step_id="add",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_SOURCE): _dropdown(options),
                }
            ),
        )

    async def async_step_tasks(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm which tasks apply, and add free-text ones."""
        view = await async_catalog_view(self.hass)
        source = self._pending[CONF_SOURCE]
        resolved = resolve_equipment_tasks(view, source, self._lang)
        if user_input is not None:
            equipment = {
                CONF_ID: next_equipment_id(
                    dict(self.config_entry.options), self._brand
                ),
                CONF_NAME: self._pending[CONF_NAME],
                CONF_SOURCE: source,
                CONF_MODEL: model_label(view, source, self._lang),
                CONF_TASKS: user_input.get(CONF_TASKS, []),
                CONF_CUSTOM_TASKS: user_input.get(CONF_CUSTOM_TASKS, []),
            }
            return self._save(self._equipments + [equipment])

        options = [
            SelectOptionDict(value=task_id, label=name)
            for task_id, (_task, name) in resolved.items()
        ]
        return self.async_show_form(
            step_id="tasks",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_TASKS, default=list(resolved)): _task_selector(
                        options
                    ),
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

        view = await async_catalog_view(self.hass)
        resolved = resolve_equipment_tasks(
            view, current.get(CONF_SOURCE, ""), self._lang
        )
        options = [
            SelectOptionDict(value=task_id, label=name)
            for task_id, (_task, name) in resolved.items()
        ]
        return self.async_show_form(
            step_id="edit_equipment",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=current[CONF_NAME]): str,
                    vol.Optional(
                        CONF_TASKS, default=current.get(CONF_TASKS, [])
                    ): _task_selector(options),
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
        return _dropdown(
            [
                SelectOptionDict(value=item[CONF_ID], label=item[CONF_NAME])
                for item in self._equipments
            ]
        )

    def _save(self, equipments: list[dict[str, Any]]) -> ConfigFlowResult:
        """Write the new equipment list; the update listener reloads the entry."""
        return self.async_create_entry(
            data={**self.config_entry.options, CONF_EQUIPMENTS: equipments}
        )
