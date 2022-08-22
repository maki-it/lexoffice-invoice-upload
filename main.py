#!/usr/bin/env python3

#Disable pycache
import sys
sys.dont_write_bytecode = True

import tempfile
from argparse import ArgumentParser
from columnar import columnar
from voucher import Config, AttachementCollector, LexofficeUpload


parser = ArgumentParser(description="Upload your vouchers/invoices from email attachements to Lexoffice.")
parser.add_argument("-c", "--config", dest="filename",
                    help="specify the config file to use. If nothing is specified, ./config.ini will be used.", metavar="FILE")
parser.add_argument("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout.")
args = parser.parse_args()

config = Config()
if args.filename:
    config = config.readconfig(filename=args.filename)
else:
    config = config.readconfig()


collectedFiles = []
foundFiles = []
mailDirs = config['Mail']['maildir'].split(',')
mailFilter = config['Mail']['filter']
fileExtensionFilter = config['Mail']['extensionsToCheck'].lower().split(',')
subjectFilter = config['Mail']['subjectsToCheck'].split(',')
tmpDir = tempfile.TemporaryDirectory() # Create temporary directory for file attachements

vouchercollector = AttachementCollector(config=config)
voucherupload = LexofficeUpload(apiToken=str(config['Lexoffice']['accessToken']))

vouchercollector.login()

for mailDir in mailDirs: 
    vouchercollector.select(mailDir)
    status, mails = vouchercollector.searchMails(mailFilter)
    foundFiles.append(vouchercollector.searchAttachements(mails, mailDir, tuple(fileExtensionFilter), tuple(subjectFilter)))

# Merge sublists of each maildir into one list
foundFiles = [x for sublist in foundFiles for x in sublist]

if foundFiles:
    if args.verbose:
        fileCount = len(foundFiles)
        counter = 1
        print(f"⬇ Downloading {len(foundFiles)} files...") 

    for file in foundFiles:  

        if args.verbose:
            
            print(f"{counter}/{fileCount} - {file[0]}")
            counter+=1

        collectedFiles.append(
            vouchercollector.downloadAttachements(file, tmpDir.name)
        )

if collectedFiles:
    if args.verbose:
        fileCount = len(collectedFiles)
        counter = 1
        print(f"\n⬆ Uploading {fileCount} files...")

    for file in collectedFiles:
        fileName = file[1]

        if args.verbose:
            print(f"{counter}/{fileCount} - {fileName}")
            counter+=1

        voucherupload.fileUpload(tmpDir.name, fileName)

    
    if args.verbose and config['Default']['showTable'].lower() == 'true':
        print("")
        print(f"SUMMARY - {counter} processed files")
        headers = ['Mail Directory', 'Filename', 'Mail Subject', 'Mail From', 'Mail  Send Date']
        table = columnar(collectedFiles, headers, no_borders=True)
        print(table)
else:
    if args.verbose:
        print("No new files found.")

vouchercollector.logout()
tmpDir.cleanup()
exit()