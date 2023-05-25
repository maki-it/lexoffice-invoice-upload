#!/usr/bin/env python3

# Disable pycache
import sys
sys.dont_write_bytecode = True

import os
import signal
from tempfile import NamedTemporaryFile as CreateTemporaryFile
from cron_validator import CronScheduler, CronValidator
from argparse import ArgumentParser
from time import sleep
from glob import glob
from columnar import columnar
from datetime import datetime
from invoice import Config, AttachmentCollector, LexofficeUpload


### Functions

def handle_sigterm(*args):
    raise KeyboardInterrupt()


def getArguments():
    """Prepare program arguments"""
    parser = ArgumentParser(
        prog="Lexoffice Invoice Upload", 
        description="Upload your invoices from email attachements to Lexoffice.", 
        epilog="For more informations see https://github.com/Maki-IT/lexoffice-invoice-upload"
        )

    parser.add_argument("-f", "--configfile", dest="filename",
                        help="Specify the config file to use (or multiple). If nothing is specified, ./config.ini will be used. Use * as wildcard.", nargs='+', metavar="FILE", default="config.ini")

    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose", default=True,
                        help="Don't print status messages to stdout.")

    parser.add_argument("--run-once",
                        action="store_true", dest="runOnce", default=False,
                        help="Only for debugging. Stops the loop in continuous mode.")

    parser.add_argument("-g", "--generate",
                        action="store_true", dest="generateConfig", default=False,
                        help="Generate a new configruation file, optionally specify path and filename with --configfile argument.")

    parser.add_argument("-l", "--loop", "--continuous",
                        action="store_true", dest="runContinuously", default=False,
                        help="Run this program continuously without exiting. See --cron to change the default 5 min intervall.")

    parser.add_argument("-c", "--cron", dest="cronSchedule",
                        help="Specify the schedule in cron-style format (minute hour day-of-month month day-of-week). See https://crontab.guru/ for examples and help about schedule expressions. Only takes effect in loop/continuous mode. Default is 5 minutes.",
                        metavar='"m h dom mon dow"',
                        default='*/5 * * * *')

    return parser.parse_args()


def loadConfig(configFile=''):
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


def get_configfiles(filenameList):
    try:
        if glob(filenameList[0]):
            fileNames = [glob(filename)[0] for filename in filenameList if glob(filename)]
        else:
            raise TypeError
    except TypeError:
        try:
            fileNames = filenameList.split()
        except AttributeError:
            fileNames = filenameList

    filenameList = []
    for path in fileNames:
        if os.path.isdir(path):
            # if value in --configfile arg is a directory return list of files in that directory
            filenameList.extend([os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))])
        else:
            # if value in --configfile arg is a filepath return it
            filenameList.append(path)

    return filenameList


def main(config):
    invoicecollector = AttachmentCollector()
    invoiceupload = LexofficeUpload(apiToken=str(config['Lexoffice']['accessToken']))
    collectedFiles = []
    foundFiles = []
    mailDirs = config['Mail']['maildir'].split(',')
    mailFilter = config['Mail']['filter']
    fileExtensionFilter = config['Mail']['extensionsToCheck'].lower().split(',')
    subjectFilter = config['Mail']['subjectsToCheck'].split(',')

    invoicecollector.login(config['Mail']['username'], config['Mail']['password'], config['Mail']['host'], config['Mail']['port'], config['Mail']['encryption'])

    for mailDir in mailDirs:
        # Remove trailing slash from mailDir string if exists to avoid maillib error with unknown directory path
        if mailDir.endswith('/') or mailDir.startswith('/'):
            print("Warning! Paths in ['Mail']['maildir'] should not start or end with a slash, so it will be removed from the path:", mailDir)
            mailDir = mailDir.lstrip('/').rstrip('/')
        invoicecollector.select(mailDir)
        status, mails = invoicecollector.searchMails(mailFilter)
        foundFiles.append(invoicecollector.searchAttachements(mails, mailDir, tuple(fileExtensionFilter), tuple(subjectFilter)))

    # Merge sublists of each maildir into one list
    foundFiles = [x for sublist in foundFiles for x in sublist]

    if foundFiles:
        if args.verbose:
            fileCount = len(foundFiles)
            counter = 0
            print(f"\n⬇ Downloading {len(foundFiles)} files...") 

        for file in foundFiles:
            tmpFile = CreateTemporaryFile()

            if args.verbose:
                counter += 1
                print(f"{counter}/{fileCount} - {file[0]}")

            collectedFiles.append(
                invoicecollector.downloadAttachements(file, tmpFile)
            )

    if collectedFiles:
        if args.verbose:
            fileCount = len(collectedFiles)
            counter = 0
            print(f"\n⬆ Uploading {fileCount} files...")

        fileNames = []
        for index, file in enumerate(collectedFiles):
            tmpFile = file[1]
            fileName = file[0][1]
            fileNames.append(fileName)

            if args.verbose:
                counter+=1
                print(f"{counter}/{fileCount} - {fileName}")

            invoiceupload.fileUpload(tmpFile, fileName)
            tmpFile.close()
            collectedFiles[index] = file[0]

        if args.verbose and config['Default']['showTable'].lower() == 'true':
            print("")
            print(f"SUMMARY - {counter} processed files")
            headers = ['Mail Directory', 'Filename', 'Mail Subject', 'Mail From', 'Mail  Send Date']
            table = columnar(collectedFiles, headers, no_borders=False, max_column_width=None)
            print(table)

            print("Done. Waiting for next cycle.")
    else:
        if args.verbose:
            print(f"[{get_timestamp()}] No new files found.")

    invoicecollector.logout()


### Run

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    args = getArguments()

    configFiles = get_configfiles(args.filename)

    if configFiles:
        # Run  in loop
        if args.runContinuously:
            cron_schedule_string = args.cronSchedule.replace('"', '').replace("'", "")
            try:
                # Validate cron schedule expression
                CronValidator.parse(cron_schedule_string)
            except ValueError as e:
                exit(f"Error: Cron schedule expression is invalid ({cron_schedule_string}). {str(e)}")

            cron_scheduler = CronScheduler(cron_schedule_string)

            print(f"[{get_timestamp()}] Starting in continuous mode with cron schedule: {cron_schedule_string}")
            try:
                for configFile in get_configfiles(args.filename):
                    print(f"[{get_timestamp()}] Checking {configFile}:")
                    main(loadConfig(configFile))

                while True:
                    if cron_scheduler.time_for_execution():
                        for configFile in get_configfiles(args.filename):
                            print(f"[{get_timestamp()}] Checking {configFile}:")
                            main(loadConfig(configFile))

                        # runOnce is for debugging/testing the continuous-mode
                        if args.runOnce:
                            exit()

                        # Wait before next cron-schedule check
                        sleep(60)

                    else:
                        # Wait before next cron-schedule check
                        sleep(15)
            except KeyboardInterrupt:
                exit()

        # Run once
        else:
            for configFile in configFiles:
                print(f"Running {configFile}:")
                main(loadConfig(configFile))

    else:
        try:
            main(loadConfig())
        except Exception:
            print("No config files founds.")
            exit(1)

exit()
