HAProxy Integration for Home Assistant
====================================

Custom Home Assistant integration to monitor HAProxy via its Stats (CSV) endpoint.

This integration is designed for local monitoring and automations and works with
HAProxy installations on OPNsense, Linux, Docker and similar environments.


FEATURES
--------

- Monitor HAProxy components:
  - Backend status (UP / DOWN / MAINT)
  - Server status
  - Active sessions
  - Queues and connection counters (depending on HAProxy stats)

- Suitable for:
  - Home Assistant dashboards
  - Automations (e.g. notifications when a backend goes DOWN)

- Lightweight polling using the HAProxy CSV stats endpoint
- Configurable data-size unit for traffic counters (B, kB, MB, GB, TB)
- No cloud or external services required


REQUIREMENTS
------------

- Home Assistant version 2023.12.0 or newer
- HAProxy with enabled Stats endpoint
- Optional: HTTP Basic Authentication on the stats endpoint


INSTALLATION VIA HACS
---------------------

1. Open HACS in Home Assistant
2. Go to Integrations
3. Open the menu (three dots, top right)
4. Select "Custom repositories"
5. Add this repository URL
6. Select category: Integration
7. Install "HAProxy Integration"
8. Restart Home Assistant


MANUAL INSTALLATION
-------------------

1. Copy the integration folder from this repository:

   custom_components/haproxy_stats

2. Paste it into your Home Assistant configuration directory:

   /config/custom_components/haproxy_stats

3. Restart Home Assistant


CONFIGURATION
-------------

OPTION A: UI CONFIGURATION (RECOMMENDED)

If the integration supports Config Flow:

1. Go to Settings -> Devices & Services
2. Click "Add integration"
3. Search for "HAProxy"
4. Enter:
   - Stats URL
   - Username (optional)
   - Password (optional)

Example stats URL:

http://192.168.1.1:8404/stats;csv


OPTION B: YAML CONFIGURATION (IF SUPPORTED)

Add the following to configuration.yaml:

haproxy:
  url: "http://192.168.1.1:8404/stats;csv"
  username: "statsuser"
  password: "statspassword"

Restart Home Assistant after editing the file.


HAPROXY STATS ENDPOINT EXAMPLE
------------------------------

Minimal HAProxy configuration example:

listen stats
  bind :8404
  mode http
  stats enable
  stats uri /stats
  stats refresh 10s
  stats auth statsuser:statspassword

The CSV endpoint is usually available at:

http://<host>:8404/stats;csv


AUTOMATION EXAMPLE
------------------

Notify when a backend goes DOWN (adjust entity name as needed):

alias: HAProxy Backend Down
trigger:
  - platform: state
    entity_id: sensor.haproxy_backend_example_status
    to: "DOWN"
action:
  - service: notify.notify
    data:
      message: "HAProxy backend example is DOWN"


DEBUGGING
---------

Enable debug logging in Home Assistant:

logger:
  default: info
  logs:
    custom_components.haproxy: debug

Logs can be found under:
Settings -> System -> Logs


TROUBLESHOOTING
---------------

Problem: No entities created
- Check if the stats URL is reachable from Home Assistant
- Verify that the URL ends with ";csv"
- Check Home Assistant logs

Problem: 401 / 403 errors
- Verify username and password
- Check HAProxy "stats auth" configuration
- Ensure authentication is enabled on the stats endpoint


CONTRIBUTING
------------

Contributions are welcome.
Please open an issue or pull request on GitHub.


LICENSE
-------

MIT License

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hannes0217/haproxy_stats&type=date&legend=top-left)](https://www.star-history.com/#hannes0217/haproxy_stats&type=date&legend=top-left)
