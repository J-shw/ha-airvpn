# <img src="images/airVPN_icon.png" alt="AirVPN App Icon" width="100"> ha-airvpn
View your [AirVPN](https://airvpn.org/) stats in Home Assistant

This custom integration allows you to view your AirVPN user and session statistics directly in Home Assistant. It polls the AirVPN API every 10 minutes (600 seconds) to provide up-to-date information on your account and active VPN sessions.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=J-shw&repository=ha-airvpn&category=Integration)

### Features

-   **User Stats**: View your account's premium status, connected status, and expiration date.
-   **Session Details**: For each active VPN session, a separate device is created in Home Assistant with a set of sensors for details like server name, IP addresses, country, and data transfer rates.

### Installation

1.  Copy the `airvpn` folder from this repository into your Home Assistant's `custom_components` directory.
2.  Restart Home Assistant.

### Configuration

The AirVPN integration is configured via the Home Assistant UI.

1.  Go to **Settings** > **Devices & Services**.
2.  Click the **Add Integration** button.
3.  Search for **AirVPN**.
4.  Enter your AirVPN API key when prompted. You can find your API key on your AirVPN client page, then [API](https://airvpn.org/apisettings/) 

### Sensors

The integration creates the following sensors:

#### AirVPN User Device

A device named after your AirVPN username is created with the following sensors:

-   `sensor.airvpn_expiration_days`: Days until your account expires.
-   `sensor.airvpn_credits`: Number of credits on your account.
-   `binary_sensor.airvpn_connected`: State of your VPN connection (on/off).
-   `binary_sensor.airvpn_premium`: Your account's premium status (on/off).

#### AirVPN Session Devices

For each active VPN session, a device is created with the name of the connected device.

-   `sensor.airvpn_session_server_name`: The name of the server you are connected to.
-   `sensor.airvpn_session_vpn_ip`: The assigned VPN IP address.
-   `sensor.airvpn_session_server_country`: The country of the server.
-   `sensor.airvpn_session_bytes_read`: Total bytes read from the connection.
-   `sensor.airvpn_session_bytes_written`: Total bytes written to the connection.
-   `sensor.airvpn_session_read_speed`: Current download speed.
-   `sensor.airvpn_session_write_speed`: Current upload speed.