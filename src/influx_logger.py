import time
import random
import logging
from influxdb import InfluxDBClient

class InfluxLogger():
    def __init__(self, DB_URL, PORT, USERNAME, PASSWORD, DBNAME):
        """Initialize alignment engine"""

        self.client = InfluxDBClient(host=DB_URL, port=PORT, username=USERNAME, password=PASSWORD, database=DBNAME, timeout=5)
        self.dbname = DBNAME
        try:
            self.client.create_database(self.dbname)
        except Exception as e:
            print(e)

        #self.client.sw
        logging.getLogger("influxdb").disabled = True # disable influxdb logger
        logging.getLogger("urllib3").setLevel(logging.WARNING)


    def save_influx_data(self, dev_id, fields, timestamp):
        entry = {}
        entry["measurement"] = "koruza_internal"
        entry["tags"] = {"devId": dev_id}

        entry["fields"] = fields
        entry["time"] = timestamp

        try:
            self.client.write_points([entry], database=self.dbname, protocol="json")
        except Exception as e:
            print("Error encountered with InfluxDB: {}".format(e))
        return entry