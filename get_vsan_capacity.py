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

        parser.add_argument('-n', '--name', required=True,
                        help="Name of the Datastore.")
        parser.add_argument('-c', '--column', required=False, default="all",
                        help="Specify output column name.")

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

    def print_datastore_info(self, ds_obj, column):
        summary = ds_obj.summary
        #self.logger.info("summary = " + str(summary))

        datastore = {}
        datastore["name"] = summary.name

        capacity_bytes = summary.capacity
        datastore["capacity_bytes"] = capacity_bytes

        freespace_bytes = summary.freeSpace
        datastore["freespace_bytes"] = freespace_bytes

        uncommitted_bytes = summary.uncommitted if summary.uncommitted else 0
        datastore["uncommitted_bytes"] = uncommitted_bytes

        provisioned_bytes = capacity_bytes - freespace_bytes + uncommitted_bytes
        datastore["provisioned_bytes"] = provisioned_bytes

        # オーバーコミットしていない場合は、マイナスは出さずに0bytesとする
        overprovisioned_bytes = provisioned_bytes - capacity_bytes
        overprovisioned_bytes = overprovisioned_bytes if overprovisioned_bytes >= 0 else 0
        datastore["overprovisioned_bytes"] = overprovisioned_bytes

        # 実量量と消費量が同一の場合を100%とする。つまり、100%を超えるとオーバーコミットとなっていると判断できる
        overprovisioned_pct = (provisioned_bytes * 100) / capacity_bytes
        datastore["overprovisioned_pct"] = overprovisioned_pct

        self.logger.info("datastore value = " + str(datastore))

        # -c の引数が何もない場合は、すべてのvalueを出力する
        # 何らかの名前を指定した場合は、それに対応するvalueを出力する
        if column == "all":
            for key in datastore:
                print str(key) + ":" + str(datastore[key])
        else:
            print datastore[column]


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
                self.print_datastore_info(ds, args.column)                
        else:
            self.logger.error("not found specified datastore. name = " + args.name)



if __name__ == '__main__':
    get_vsan_capacity = GetVsanCapacity()
    get_vsan_capacity.main()
