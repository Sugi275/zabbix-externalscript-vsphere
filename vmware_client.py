#!/usr/bin/python
# coding:utf-8

import atexit
import ssl

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

from tools import cli

class VMwareClient(object):

    def __init__(self, logger, args):
        # log設定。呼び出し元で指定したログファイルに出力する
        # 呼び出し元で出力ファイルを変更することで、使い回しをしても任意のログファイルへ出力出来ることを意図した
        self.logger = logger
        self.connect_vmware(args)

    def connect_vmware(self, args):
        host = args.host
        user = args.user
        pwd = args.password
        port = int(args.port)

        try:
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_NONE

            self.logger.info("try connect vcenter. host=" + host + " user=" + user + " port=" + str(port))

            # vcenter server へ接続
            service_instance = connect.SmartConnect(host=host,
                                                    user=user,
                                                    pwd=pwd,
                                                    port=port,
                                                    sslContext=context)

            if not service_instance:
                self.logger.error("Could not connect to the specified host using specified "
                      "username and password")
                return -1

            atexit.register(connect.Disconnect, service_instance)

            self.service_instance = service_instance
            self.logger.info("successfly connect vcenter")


        except vmodl.MethodFault as e:
            self.logger.error("Caught vmodl fault : {}".format(e.msg))
            return -1

        self.service_instance = service_instance

    # service_instance を返却
    def get_service_instance(self):
        if self.service_instance is not None:
            return self.service_instance
        else:
            self.logger.error("service instance is None")
            return None
