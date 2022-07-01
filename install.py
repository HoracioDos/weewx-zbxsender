"""
A WeeWX service to send loop or record data to zabbix using zabbix_sender

Based on WeeWx zabbix service copyright (C) Marc Pignat marc<at>pignat.org
https://github.com/RandomReaper/weewx-zabbix
Based on WeeWx aprx service Copyright (C) 2020-2021 Gary Roderick gjroderick<at>gmail.com
https://github.com/gjr80/weewx-aprx

Copyright (C) 2022 Horacio Dos rosendeh<at>gmail.com

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see https://www.gnu.org/licenses/."""

import weewx

from distutils.version import StrictVersion
from setup import ExtensionInstaller

REQUIRED_WEEWX_VERSION = "3.9.0"
ZBX_SENDER_VERSION = "0.0.1"

def loader():
    return zbxsenderInstaller()

class zbxsenderInstaller(ExtensionInstaller):
    def __init__(self):
        if StrictVersion(weewx.__version__) < StrictVersion(REQUIRED_WEEWX_VERSION):
            msg = "%s requires WeeWX %s or greater, found %s" % (''.join(('zbxsender ', ZBX_SENDER_VERSION)),
                                                                 REQUIRED_WEEWX_VERSION,
                                                                 weewx.__version__)
            raise weewx.UnsupportedFeature(msg)

        super(zbxsenderInstaller, self).__init__(
            version=ZBX_SENDER_VERSION,
            name='zbxsender',
            description='A WeeWX service to send loop or record data to zabbix using zabbix_sender',
            author='HoracioDos',
            author_email='rosendeh@gmail.com',
            process_services='user.zbxsender.zbxsender',
            files=[('bin/user', ['bin/user/zbxsender.py'])],
            config={
                'zbxsender': {
                    'zbx_sender_pth': '/usr/bin/zabbix_sender',
                    'prefix': 'weewx_',
                    'server': '192.168.1.10',
                    'host': 'weewx-host',
                    'config': '/etc/zabbix/zabbix_agent2.conf',
                    'data_binding': 'wx_binding',
                    'binding': 'archive'
                }
            }
        )
