import time
import xmlrpc.client
from threading import Thread, Lock
from .src.influx_logger import InfluxLogger

from ..src.constants import KORUZA_MAIN_PORT
from ..src.config_manager import get_config

config = get_config()
link_config = config.get("link_config", {})
d2d_channel = link_config.get("channel", "local")  # default mode is local
mode = link_config.get(d2d_channel, {}).get("mode", "primary")  # if no mode is set, mode is primary by default

cloud_config = config.get("cloud_config", {})
DB_URL = cloud_config.get("url", "")
PORT = cloud_config.get("port", 8086)
DBNAME = cloud_config.get("dbname", "")
USERNAME = cloud_config.get("username", "")
PASSWORD = cloud_config.get("password", "")
logger = InfluxLogger(DB_URL, PORT, USERNAME, PASSWORD, DBNAME)
koruza_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{KORUZA_MAIN_PORT}", allow_none=True)

while True:
    
    ## PRIMARY UNIT DATA
    try:
        unit_id = koruza_proxy.get_unit_id()
    except Exception as e:
        unit_id = "Not Set"
    
    try:
        x, y = koruza_proxy.get_motors_position()
    except Exception as e:
        x = None
        y = None

    sfp_data = None
    try:
        sfp_data = koruza_proxy.get_sfp_diagnostics()
    except Exception as e:
        rx_dBm = None
    if sfp_data is not None:
        rx_dBm = sfp_data.get("sfp_0", {}).get("diagnostics", {}).get("rx_power_dBm", -40)

    primary_data = {"x": x, "y": y, "rx_power_dBm": rx_dBm}

    timestamp = time.time_ns()
    logger.save_influx_data(unit_id, primary_data, timestamp)

    if mode == "secondary":
        ## SECONDARY UNIT DATA
        try:
            motor_x, motor_y = koruza_proxy.issue_remote_command("get_motors_position", ())
        except Exception as e:
            x = None
            y = None
        
        sfp_data = None
        try:
            sfp_data = koruza_proxy.issue_remote_command("get_sfp_diagnostics", ())
        except Exception as e:
            rx_dBm = None
        if sfp_data is not None:
            rx_dBm = sfp_data.get("sfp_0", {}).get("diagnostics", {}).get("rx_power_dBm", -40)
            
        secondary_data = {"x": x, "y": y, "rx_power_dBm": rx_dBm}
        try:
            unit_id = koruza_proxy.issue_remote_command("get_unit_id", ())
        except Exception as e:
            unit_id = "Not Set"
        timestamp = time.time_ns()
        logger.save_influx_data(unit_id, secondary_data, timestamp)

    time.sleep(10)