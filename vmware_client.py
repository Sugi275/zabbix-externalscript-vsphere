#!/usr/bin/python
# coding:utf-8

from tools import cli

from logging import getLogger,INFO,Formatter
from logging.handlers import RotatingFileHandler

class VMwareClient(object):

    def __init__(self):
        args = cli.get_args()
        print (args.host)
        print ("hello")
