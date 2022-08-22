import configparser
from voucher.collector import AttachementCollector
from voucher.uploader import LexofficeUpload

class Config:
    def __init__(self):
        self.config = configparser.RawConfigParser()

    def readconfig(self, filename='./config.ini'):
        self.config.read(filename)
        for topic in self.config:
            for field in topic:
                if field == '':
                    exit(f"Error: ['{topic}']['{field}'] must not be empty!")

        return self.config



