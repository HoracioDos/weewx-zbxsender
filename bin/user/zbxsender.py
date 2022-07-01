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

from datetime import datetime
import os
from distutils.version import StrictVersion

import weewx
import weeutil.weeutil
from weewx.units import ValueTuple, Formatter, Converter, ValueHelper
from weewx.engine import StdService

from subprocess import Popen, PIPE, STDOUT

ZBX_SENDER_VERSION = "0.0.1"
REQUIRED_WEEWX_VERSION = "3.9.0"

if StrictVersion(weewx.__version__) < StrictVersion(REQUIRED_WEEWX_VERSION):
    msg = "%s requires WeeWX %s or greater, found %s" % (''.join(('zbxsender ', ZBX_SENDER_VERSION)),
                                                         REQUIRED_WEEWX_VERSION,
                                                         weewx.__version__)
    raise weewx.UnsupportedFeature(msg)

# import/setup logging, WeeWX v3 is syslog based but WeeWX v4 is logging based,
# try v4 logging and if it fails use v3 logging

try:
    # WeeWX4 logging
    import logging
    from weeutil.logger import log_traceback
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

    # log_traceback() generates the same output but the signature and code is
    # different between v3 and v4. We only need log_traceback at the log.error
    # level so define a suitable wrapper function.
    def log_traceback_error(prefix=''):
        log_traceback(log.error, prefix=prefix)

except ImportError:
    # WeeWX legacy (v3) logging via syslog
    import syslog
    from weeutil.weeutil import log_traceback

    def logmsg(level, msg):
        syslog.syslog(level, 'zbxsender: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

    # log_traceback() generates the same output but the signature and code is
    # different between v3 and v4. We only need log_traceback at the log.error
    # level so define a suitable wrapper function.
    def log_traceback_error(prefix=''):
        log_traceback(prefix=prefix, loglevel=syslog.LOG_ERR)

class zbxsender(StdService):

    def __init__(self, engine, config_dict):
        super(zbxsender, self).__init__(engine, config_dict)

        conf = config_dict['zbxsender']

        self.zabbix_sender = conf.get('zbx_sender_pth', '/usr/bin/zabbix_sender')
        self.prefix = conf.get('prefix', 'weewx_')
        self.server = conf.get('server', '127.0.0.1')
        self.host = conf.get('host', 'weewx-host')
        self.config = conf.get('config', '/etc/zabbix/zabbix_agentd.conf')
        self.unit_system = conf.get('unit_system', 'USUnits')
        self.data_binding = conf.get('data_binding', 'wx_binding')
        self.binding = conf.get('binding', 'loop').lower()

        if self.binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        else:
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)

        loginf("service version: %s" % ZBX_SENDER_VERSION)
        loginf("zbx_sender_pth: %s" % self.zabbix_sender)
        loginf("prefix: %s" % self.prefix)
        loginf("zbx_server: %s" % self.server)
        loginf("zbx_host_name: %s" % self.host)
        loginf("zbx_agent_cfg_file: %s" % str(self.config))
        loginf("unit_system: %s" % str(self.unit_system))
        loginf("data_binding: %s" % str(self.data_binding))
        loginf("binding: %s" % str(self.binding))

    def handle_new_loop(self, event):
        """Process a new loop packet."""
        self.handle_data(event.packet)

    def handle_new_archive(self, event):
        """Process a new archive record."""
        self.handle_data(event.record)

    def handle_data(self, event_data):
        # wrap in a try..except in case anything goes wrong
        try:
            # obtain the data required for the weather packet file
            data = self.send_data(event_data)
        except Exception as e:
            # an exception occurred, log it and continue
            log_traceback_error(prefix='zbxsender: **** ')

    def send_data(self, packet):
         pu = packet.get(self.unit_system)
         s = ""
         f = Formatter()
         for key,value in packet.items():
             if key == 'windDir':
                vt = ValueTuple(value, 'degree_compass', 'group_direction')
                new_value = f.to_ordinal_compass(vt)
             elif key == 'windGustDir':
                vt = ValueTuple(value, 'degree_compass', 'group_direction')
                new_value = f.to_ordinal_compass(vt)
             else:
                new_value = str(value)
             l=self.host + " " + self.prefix+key + " " + new_value + "\n"
             s+=l
             if weewx.debug >= 1:
                logdbg(l)

         c = [self.zabbix_sender, "-c", self.config, "-z", self.server, "-i", "-"]
         if weewx.debug >= 1:
            logdbg("cmd line : " + str(c))
         p = Popen(c, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
         sender_stdout = p.communicate(input=s.encode())[0]
         loginf(' '.join(sender_stdout.decode().split()))

if __name__ == "__main__":

        try:
           # WeeWX V4 logging
           weeutil.logger.setup('zbxsender', {})
        except NameError:
           # WeeWX V3 logging
           syslog.openlog('zbxsender', syslog.LOG_PID | syslog.LOG_CONS)
           syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
