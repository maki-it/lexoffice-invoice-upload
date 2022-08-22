import imaplib
import os
import email
import string
from sys import exit

class AttachementCollector:
    """
    A class for downloading mail attachements.
    """
    def __init__(self, config) -> None:
        self.config = config
        self.downloadStarted = False

    def login(self) -> None:
        """
        Login to mail server with either SSL or STARTTLS\n
        Set the port accordingly. Normally it is:
        - 993 for SSL (recommended -> explicit TLS)
        - 143 for STARTTLS
        """

        if self.config['Mail']['encryption'].lower() == 'ssl':
            self.imap = imaplib.IMAP4_SSL(self.config['Mail']['host'], self.config['Mail']['port'])
        
        elif self.config['Mail']['encryption'].lower() == 'starttls':
            from ssl import create_default_context
            tls_context = create_default_context()
            self.imap = imaplib.IMAP4(self.config['Mail']['host'], self.config['Mail']['port'])
            self.imap.starttls(ssl_context=tls_context)
        
        else:
            exit("Error: ['Mail']['method'] in config must be set to either SSL or STARTTLS!")

        self.imap.login(self.config['Mail']['username'], self.config['Mail']['password'])

    def logout(self) -> None: 
        """Safely close the connection and logout of mail server"""
        self.imap.close()
        self.imap.logout()

    def select(self, maildir='Inbox') -> tuple[str, list[bytes | None]]:
        """Select mail directory on mail server"""
        self.maildir = maildir
        return self.imap.select(self.maildir)

    def search(self) -> tuple[str, list[bytes | None]]:
        return self.imap.search(None, self.config['Mail']['filter'])

    def download_attachements(self, mails: list, tmpDir: string, fileExtensionFilter: tuple = (".pdf"), subjectFilter: tuple = ()) -> list:
        """"
        Download attachements with specified file extensions from mail
        """
        collectedFiles = []

        # For found mails in maildir 
        for num in mails[0].split():
            # Fetch found mail from maildir 
            returnvalue, data = self.imap.fetch(num, '(RFC822)' )

            # Set mail as seen
            self.imap.store(mails[0].decode('utf-8').replace(' ',','), '+FLAGS', '\Seen')

            rawEmail = data[0][1]

            # converts byte literal to string removing b''
            rawEmailString = rawEmail.decode('utf-8')
            emailMessage = email.message_from_string(rawEmailString)

            # If subjectFilter is empty or subjectFilter contains a word in email subject
            if not all(subjectFilter) or any(substring in emailMessage['subject'] for substring in subjectFilter):
                # download attachments from mail
                if not self.downloadStarted:
                    print("⬇ Downloading files...")
                    self.downloadStarted = True
                    
                for part in emailMessage.walk():

                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    fileName = part.get_filename(tmpDir)

                    if bool(fileName):
                        # Check if fileName ending matches list of fileextensions from config
                        if fileName.lower().endswith(fileExtensionFilter):
                            filePath = os.path.join(tmpDir, fileName)

                            # Check if file doesn't already exists
                            if not os.path.isfile(filePath):
                                fp = open(filePath, 'wb')
                                fp.write(part.get_payload(decode=True))
                                fp.close()
                                collectedFiles.append([self.maildir, fileName, emailMessage['subject'], emailMessage['from'], emailMessage['date']])

                                # Show last downloaded file as status indicactor
                                print(f"{fileName}")
        
        return collectedFiles
            
        

