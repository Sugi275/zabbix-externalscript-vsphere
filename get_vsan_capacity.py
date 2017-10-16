#!/usr/bin/python
# coding:utf-8

import atexit
import requests
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

import vmware_client
from tools import cli

from logging import getLogger,INFO,Formatter
from logging.handlers import RotatingFileHandler
import os
import sys


class GetVsanCapacity(object):

    def __init__(self):
	self._log_setting()

    # log出力設定 10MBの5世代保管
    def _log_setting(self):

        logpath = os.path.abspath(os.path.dirname(__file__))

        logpath = logpath + "/log_get_vsan_capacity.txt"
        self.logger = getLogger(__name__)
        handler = RotatingFileHandler(
            filename=logpath,
            maxBytes=10485760, # 10MB
            backupCount=4
        )

        handler.setLevel(INFO)
        formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.setLevel(INFO)
        self.logger.addHandler(handler)

    # 引数指定、取得
    def get_args(self):
        parser = cli.build_arg_parser()
        parser.add_argument('-n', '--name', required=False,
                        help="Name of the Datastore.")
        my_args = parser.parse_args()
        return cli.prompt_for_password(my_args)

    # vim_typeで指定したObjectをreturnする
    def get_obj(self, content, vim_type, name=None):
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vim_type, True)

        if name:
            for c in container.view:
                self.logger.info("container.name = " + str(c.name))
                if c.name == name:
                    obj = c
                    return [obj]
        else:
            return None



    def main(self):
        # 引数指定、取得
        args = self.get_args()

        self.logger.info("args = " + str(args)) 

        # vCenter Serverへ接続するための前準備
        client = vmware_client.VMwareClient(self.logger, args)

        service_instance = client.get_service_instance()

        content = service_instance.RetrieveContent()

        self.logger.info("content = " + str(content))

        # データストアの一覧を取得する。名前が指定された場合は、指定されたデータストアのみ取得する
        ds_obj_list = self.get_obj(content, [vim.Datastore], args.name)
        if ds_obj_list is not None:
            for ds in ds_obj_list:
                print (ds)
        else:
            self.logger.error("not found specified datastore. name = " + args.name)



if __name__ == '__main__':
    get_vsan_capacity = GetVsanCapacity()
    get_vsan_capacity.main()
