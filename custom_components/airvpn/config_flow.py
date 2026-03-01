import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Air VPN Integration", data=user_input)

        schema = vol.Schema({
            vol.Required("api_key"): str
        })
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors={}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return AirVPNOptionsFlowHandler()

class AirVPNOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle AirVPN options."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
            }),
        )