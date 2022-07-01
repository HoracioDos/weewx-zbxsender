# weewx-zbxsender
A WeeWX service to send loop or record data to zabbix using zabbix_sender

![dashboard](https://raw.githubusercontent.com/HoracioDos/weewx-zabbixsender/main/images/dashboard.png)
### Dependencies
This plug-in requires `zabbix_sender` command installed in Weewx server.
### Build the package, or get it from [here](https://github.com/HoracioDos/weewx-zbxsender/releases/latest)
```
mkdir -p ~/git/ && cd ~/git && git clone https://github.com/HoracioDos/weewx-zbxsender.git
cd weewx-zbxsender
./gen-tar.sh
```
## Install the weewx extension
sudo wee_extension --install weewx-zbxsender.tgz
```
# Parameters for extension 'zbxsender'
[zbxsender]
   log_success = False
   log_failure = True
   zbx_sender_pth = /usr/bin/zabbix_sender
   prefix = weewx_
   server = 192.168.1.XX
   host = weewxserver
   config = /etc/zabbix/zabbix_agent2.conf
   unit_system = USUnits
   data_binding = wx_binding
   binding = archive
```
# ToDo
* Send data in JSON format with only one master Item key.
* Modify zabbix template with dependent Item keys
 
