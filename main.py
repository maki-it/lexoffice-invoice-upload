#!/usr/bin/env python3

#Disable pycache
import sys
sys.dont_write_bytecode = True

import os
import signal
import tempfile
from argparse import ArgumentParser
from time import sleep
from glob import glob
from columnar import columnar
from datetime import datetime
from voucher import Config, AttachementCollector, LexofficeUpload


### Functions

def handle_sigterm(*args):
    raise KeyboardInterrupt()

def getArguments():
    """Prepare program arguments"""
    parser = ArgumentParser(description="Upload your vouchers/invoices from email attachements to Lexoffice.")
    parser.add_argument("-c", "--config", dest="filename",
                        help="specify the config file to use (or multiple). If nothing is specified, ./config.ini will be used. Use * as wildcard.", nargs='+', metavar="FILE", default="config.ini")
                        
    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose", default=True,
                        help="don't print status messages to stdout.")

    parser.add_argument("-g", "--generate",
                        action="store_true", dest="generateConfig", default=False,
                        help="generate a new configruation file, optionally specify path and filename with --config argument.")

    parser.add_argument("-l","--loop", "--continuous",
                        action="store_true", dest="runContinuously", default=False,
                        help="run this program continuously without exiting. See --intervall to change the default 120 seconds intervall.")

    parser.add_argument("-i", "--intervall", dest="intervall",
                        help="specify the intervall in seconds between each run. Only takes effect in loop/continuous mode. Default is 120 seconds.", metavar="SECONDS", default=120)

    parser.add_argument("--runonce",
                        action="store_true", dest="runOnce", default=False,
                        help="Only for debugging. Stops the loop in continuous mode.")

    return parser.parse_args()

def loadConfig(configFile = ''):
    """Prepare/Load program config"""
    config = Config()

    config.fileName = os.path.join(os.path.dirname(__file__), config.fileName)

    if configFile:
        if args.generateConfig:
            if config.createConfigIfMissing(configFile):
                print(f"New configuration file generated at {configFile}")
                exit()
            else:
                exit(f"{config.fileName} does already exist")
        else:
            return config.readConfig(configFile)
        
    else:
        # If program runs with default config
        if args.generateConfig:
            if config.createConfigIfMissing(config.fileName):
                exit(f"New configuration file generated at {config.fileName}")
            else:
                exit(f"{config.fileName} does already exist")
        else:
            return config.readConfig(config.fileName)

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main(config, runContinuously: bool = False):
    vouchercollector = AttachementCollector()
    voucherupload = LexofficeUpload(apiToken=str(config['Lexoffice']['accessToken']))
    collectedFiles = []
    foundFiles = []
    mailDirs = config['Mail']['maildir'].split(',')
    mailFilter = config['Mail']['filter']
    fileExtensionFilter = config['Mail']['extensionsToCheck'].lower().split(',')
    subjectFilter = config['Mail']['subjectsToCheck'].split(',')
    tmpDir = tempfile.TemporaryDirectory() # Create temporary directory for file attachements

    vouchercollector.login(config['Mail']['username'], config['Mail']['password'], config['Mail']['host'], config['Mail']['port'], config['Mail']['encryption'])

    for mailDir in mailDirs: 
        vouchercollector.select(mailDir)
        status, mails = vouchercollector.searchMails(mailFilter)
        foundFiles.append(vouchercollector.searchAttachements(mails, mailDir, tuple(fileExtensionFilter), tuple(subjectFilter)))

    # Merge sublists of each maildir into one list
    foundFiles = [x for sublist in foundFiles for x in sublist]

    if foundFiles:
        if args.verbose:
            fileCount = len(foundFiles)
            counter = 0
            print(f"\n⬇ Downloading {len(foundFiles)} files...") 

        for file in foundFiles:  

            if args.verbose:
                counter+=1
                print(f"{counter}/{fileCount} - {file[0]}")

            collectedFiles.append(
                vouchercollector.downloadAttachements(file, tmpDir.name)
            )

    if collectedFiles:
        if args.verbose:
            fileCount = len(collectedFiles)
            counter = 0
            print(f"\n⬆ Uploading {fileCount} files...")

        for file in collectedFiles:
            fileName = file[1]

            if args.verbose:
                counter+=1
                print(f"{counter}/{fileCount} - {fileName}")

            voucherupload.fileUpload(tmpDir.name, fileName)

        
        if args.verbose and config['Default']['showTable'].lower() == 'true':
            print("")
            print(f"SUMMARY - {counter} processed files")
            headers = ['Mail Directory', 'Filename', 'Mail Subject', 'Mail From', 'Mail  Send Date']
            table = columnar(collectedFiles, headers, no_borders=False, max_column_width=None)
            print(table)
    else:
        if args.verbose: #and not runContinuously:
            print("No new files found.")

    vouchercollector.logout()
    tmpDir.cleanup()


### Run

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    args = getArguments()

    try:
        if glob(args.filename[0]):
            fileNames = [glob(filename)[0] for filename in args.filename if glob(filename)]
        else:
            raise TypeError
    except TypeError:
        try:
            fileNames = args.filename.split()
        except AttributeError:
            fileNames = args.filename

    for path in fileNames:
        if(os.path.isdir(path)):
            fileNames = [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

    if args.runContinuously and fileNames:
        print(f"[{get_timestamp()}] Starting in continuous mode with {args.intervall} seconds intervall.")
        try:
            while True:
                for configFile in fileNames:
                    print(f"[{get_timestamp()}] Running {configFile}:")
                    main(loadConfig(configFile), args.runContinuously)

                if args.runOnce:
                    exit()

                sleep(int(args.intervall))
        except KeyboardInterrupt:
            exit()

    else:
        if fileNames:
            for configFile in fileNames:
                print(f"Running {configFile}:")
                main(loadConfig(configFile))
        else:
            main(loadConfig(fileNames))

exit()