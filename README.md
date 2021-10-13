# koruza-v2-cloud

## Description
This module is used to store KORUZA v2 Pro data to a cloud hosted [InfluxDB](https://www.influxdata.com/) timeseries database. Stored data can be displayed using various analytics and data visualization platforms, such as [Grafana](https://grafana.com/).

Stored data is used for device health, status and operation monitoring and analysis.

## Usage
In order for the KORUZA v2 Pro unit to transmit data, set the InfluxDB settings correctly.
To do so, edit the `cloud_config` part of the `./config/config.json` according to your InfluxDB configuration:
```
"cloud_config": {
    "url": "www.sample.com/koruza",  // url of your InfluxDB host
    "port": 8086,  // port to your database
    "dbname": "koruzaDb",  // name of your database
    "username": "user123",  // username of account with write permissions
    "password": "user123pass",  // password of above user
    "interval": 10  // reporting interval
}
```

To disable cloud data reporting use `sudo systemctl disable koruza_cloud`.

## License
Firmware and software originating from KORUZA v2 Pro project, including KORUZA v2 Pro Cloud, is licensed under GNU General Public License v3.0.

Open-source licensing means the hardware, firmware, software and documentation may be used without paying a royalty, and knowing one will be able to use their version forever. One is also free to make changes, but if one shares these changes, they have to do so under the same conditions they are using themselves. KORUZA, KORUZA v2 Pro and IRNAS are all names and marks of IRNAS LTD. These names and terms may only be used to attribute the appropriate entity as required by the Open Licence referred to above. The names and marks may not be used in any other way, and in particular may not be used to imply endorsement or authorization of any hardware one is designing, making or selling.