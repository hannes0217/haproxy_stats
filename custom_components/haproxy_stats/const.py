DOMAIN = "haproxy_stats"

CONF_NAME = "name"
CONF_URL = "url"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_VERIFY_SSL = "verify_ssl"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DATA_SIZE_UNIT = "data_size_unit"

DEFAULT_NAME = "HAProxy"
DEFAULT_VERIFY_SSL = False
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_URL = "http://192.168.1.1:8822/haproxy?stats;csv"
DEFAULT_DATA_SIZE_UNIT = "MB"

DATA_SIZE_UNITS: tuple[str, ...] = ("B", "kB", "MB", "GB", "TB")

DATA_SIZE_UNIT_FACTORS: dict[str, float] = {
    "B": 1.0,
    "kB": 1_000.0,
    "MB": 1_000_000.0,
    "GB": 1_000_000_000.0,
    "TB": 1_000_000_000_000.0,
}
