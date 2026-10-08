import logging
import os
import sys
ISPACKED = getattr(sys,'frozen',False)


class Log:
    class Level:
        debug   = logging.DEBUG
        info    = logging.INFO
        warning = logging.WARNING
        error   = logging.ERROR
    instance = None
    def __init__(self):
        logPath = "mybridge.log"
        if ISPACKED:
            logPath = os.path.join(r"D:\ProgramData\mybridge", "mybridge.log")
            folder = os.path.dirname(logPath)
            if not os.path.exists(folder):
                os.makedirs(folder)
        self.loggers = []
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(logging.Formatter('%(name)-10s%(levelname)-5s:%(message)s'))

        self.filehandler = logging.FileHandler(logPath,encoding="utf-8")
        self.filehandler.setLevel(logging.DEBUG)
        self.filehandler.setFormatter(logging.Formatter('%(asctime)s:%(name)-10s:%(levelname)-5s:%(message)s'))

    def getLogger(self,name:str)->logging.Logger:
        logger = logging.getLogger(name)
        logger.addHandler(self.console_handler)
        logger.addHandler(self.filehandler)
        if logger not in self.loggers:
            self.loggers.append(logger)

        return logger
    def setConsoleHandlerLevel(self,level):
        self.console_handler.setLevel(level)
    def setFileHandlerLevel(self,level):
        if self.filehandler:
            self.filehandler.setLevel(level)
    @classmethod
    def get(cls)->"Log":
        if not cls.instance:
            cls.instance = cls()
        return cls.instance
