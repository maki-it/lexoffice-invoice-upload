import imaplib
import os
import email
from sys import exit


class AttachmentCollector:
    """
    A class for downloading mail attachements.
    """
    def __init__(self) -> None:
        self.downloadStarted = False

    def login(self, username: str, password: str, host: str, port: int, encryptionMethod: str) -> None:
        """
        Login to mail server with either SSL or STARTTLS\n
        Set the port accordingly. Normally it is:
        - 993 for SSL (recommended -> explicit TLS)
        - 143 for STARTTLS
        """

        if encryptionMethod.lower() == 'ssl':
            self.imap = imaplib.IMAP4_SSL(host, port)
        
        elif encryptionMethod.lower() == 'starttls':
            from ssl import create_default_context
            tls_context = create_default_context()
            self.imap = imaplib.IMAP4(host, port)
            self.imap.starttls(ssl_context=tls_context)
        
        else:
            exit("Error: ['Mail']['encryption'] in config must be set to either SSL or STARTTLS")

        try:
            self.imap.login(username, password)
        except self.imap.error as e:
            if "AUTHENTICATIONFAILED" in str(e):
                exit("Error: Authentication to mailbox failed")
            else:
                exit("Error: ", str(e))

    def logout(self) -> None: 
        """Safely close the connection and logout of mail server"""
        self.imap.close()
        self.imap.logout()

    def select(self, maildir: str = 'Inbox') -> tuple[str, list[bytes | None]]:
        """Select mail directory on mail server"""
        return self.imap.select(maildir)

    def searchMails(self, filter: str) -> tuple[str, list[bytes | None]]:
        """Search for mails in selected mail directory with filter"""
        try:
            return self.imap.search(None, filter)
        except self.imap.error as e:
            print("Error with ['Mail']['filter'] configuration:")
            raise SystemExit(e)

    def searchAttachements(self, mails: list, mailDir: str, fileExtensionFilter: tuple = (".pdf"), subjectFilter: tuple = ()) -> list:
        """Search given mails for attachements with applied filter"""

        foundFiles = []
        
        for num in mails[0].split():
            # Fetch found mail from selected maildir 
            returnvalue, data = self.imap.fetch(num, '(RFC822)' )

            # Set mail as seen
            self.imap.store(mails[0].decode('utf-8').replace(' ',','), '+FLAGS', '\Seen')

            rawEmail = data[0][1]

            # converts byte literal to string removing b''
            rawEmailString = rawEmail.decode('utf-8', 'ignore')
            emailMessage = email.message_from_string(rawEmailString)

            # If subjectFilter is empty or subjectFilter contains a word in email subject
            if not all(subjectFilter) or any(substring in emailMessage['subject'] for substring in subjectFilter):
                # download attachments from mail 
                for part in emailMessage.walk():

                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    fileName = part.get_filename()

                    if bool(fileName):
                        # Check if fileName ending matches list of fileextensions from config
                        if fileName.lower().endswith(fileExtensionFilter):
                            foundFiles.append((fileName, mailDir, emailMessage, part))
                        
        return foundFiles

    def downloadAttachements(self, file: list, tmpDir: str) -> list:
        """"Download attachements with specified file extensions from mail"""
        fileName, mailDir, emailMessage, part = file
        filePath = os.path.join(tmpDir, file[0])

        # Check if file doesn't already exist before download
        if not os.path.isfile(filePath):
            fp = open(filePath, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
            return [mailDir, fileName, emailMessage['subject'], emailMessage['from'], emailMessage['date']]
        else:
            return None

            
        

