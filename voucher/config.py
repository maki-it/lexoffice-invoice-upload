import os
import shutil
import configparser


class Config:
    """Class for parsing the configuration file with fileparser"""

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.fileName = 'config.ini'

    def readConfig(self, fileName: str = '') -> configparser.RawConfigParser:
        """Read program configuration from config file"""
        if not fileName:
            fileName = self.fileName

        if not os.path.isfile(fileName):
            exit(f"Error: config file '{fileName}' not found")
        else:
            self.config.read(fileName)
            for topic in self.config:
                for field in topic:
                    if field == '':
                        exit(f"Error: ['{topic}']['{field}'] must not be empty")

            return self.config

    def createConfigIfMissing(self, fileName: str = '') -> bool:
        """Create default configuration file if missing"""
        if not fileName:
            fileName = self.fileName

        if not os.path.isfile(fileName):
            templateConfigFile = os.path.join(os.path.dirname(__file__) ,'templateConfig.ini')
            try:
                shutil.copyfile(templateConfigFile, fileName)
            except IsADirectoryError:
                exit("Error: no file name specified")
            return True
        else:
            return False
