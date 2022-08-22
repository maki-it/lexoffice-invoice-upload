#Disable pycache
import sys
sys.dont_write_bytecode = True

import tempfile
from columnar import columnar
from voucher import Config, AttachementCollector, LexofficeUpload

config = Config()
config = config.readconfig()

collectedFiles = []
mailDirs = config['Mail']['maildir'].split(',')
fileExtensionFilter = config['Mail']['extensionsToCheck'].lower().split(',')
subjectFilter = config['Mail']['subjectsToCheck'].split(',')
tmpDir = tempfile.TemporaryDirectory() # Create temporary directory for file attachements

vouchercollector = AttachementCollector(config=config)
voucherupload = LexofficeUpload(apiToken=str(config['Lexoffice']['accessToken']))

vouchercollector.login()

for maildir in mailDirs: 
    vouchercollector.select(maildir)
    status, mails = vouchercollector.search()
    collectedFiles.append(
        vouchercollector.download_attachements(mails, tmpDir.name, tuple(fileExtensionFilter), tuple(subjectFilter))
    )

# Merge sublists of each maildir into one list
collectedFiles = [x for sublist in collectedFiles for x in sublist]

if collectedFiles:
    print("\n⬆ Uploading files...")
    for file in collectedFiles:
        fileName = file[1]
        print(fileName)
        voucherupload.fileUpload(tmpDir.name, fileName)

    if config['Default']['showTable'].lower() == 'true':
        print("")
        print("Processed mails and files:")
        headers = ['Mail Directory', 'Filename', 'Mail Subject', 'Mail From', 'Mail  Send Date']
        table = columnar(collectedFiles, headers, no_borders=True)
        print(table)
else:
    print("No new files found.")

vouchercollector.logout()
tmpDir.cleanup()
exit()