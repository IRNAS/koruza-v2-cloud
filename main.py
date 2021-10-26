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
INTERVAL = cloud_config.get("interval", 10)

logger = InfluxLogger(DB_URL, PORT, USERNAME, PASSWORD, DBNAME)
koruza_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{KORUZA_MAIN_PORT}", allow_none=True)

while True:
    
    ## local unit data
    try:
        local_unit_id = koruza_proxy.get_unit_id()
    except Exception as e:
        local_unit_id = "Not Set"
    
    try:
        local_motor_x, local_motor_y = koruza_proxy.get_motors_position()
    except Exception as e:
        local_motor_x = None
        local_motor_y = None

    sfp_data = None
    try:
        sfp_data = koruza_proxy.get_sfp_diagnostics()
    except Exception as e:
        local_rx_dBm = None
    if sfp_data is not None:
        local_rx_dBm = float(sfp_data.get("sfp_0", {}).get("diagnostics", {}).get("rx_power_dBm", -40.0))

    local_data = {"x": local_motor_x, "y": local_motor_y, "rx_power_dBm": local_rx_dBm}

    timestamp = time.time_ns()
    logger.save_influx_data(local_unit_id, local_data, timestamp)

    if mode == "primary":
        ## send secondary unit data as well
        try:
            remote_unit_id = koruza_proxy.issue_remote_command("get_unit_id", ())
        except Exception as e:
            remote_unit_id = "Not Set"

        remote_motor_x = None
        remote_motor_y = None
        try:
            remote_motor_x, remote_motor_y = koruza_proxy.issue_remote_command("get_motors_position", ())
        except Exception as e:
            remote_motor_x = None
            remote_motor_y = None
        
        sfp_data = None
        try:
            sfp_data = koruza_proxy.issue_remote_command("get_sfp_diagnostics", ())
        except Exception as e:
            remote_rx_dBm = None
        if sfp_data is not None:
            remote_rx_dBm = float(sfp_data.get("sfp_0", {}).get("diagnostics", {}).get("rx_power_dBm", -40.0))
            
        remote_data = {"x": remote_motor_x, "y": remote_motor_y, "rx_power_dBm": remote_rx_dBm}
        timestamp = time.time_ns()
        logger.save_influx_data(remote_unit_id, remote_data, timestamp)

    time.sleep(INTERVAL)