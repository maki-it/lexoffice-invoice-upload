import pycurl
from urllib import parse


class LexofficeUpload:
    """
    A class for uploading invoice documents
    """

    def __init__(self, apiToken: str) -> None:
        self.apiUrl = 'https://api.lexoffice.io/v1/files'
        self.apiToken = apiToken

    def fileUpload(self, tmpFile, fileName: str):
        """
        Upload a file to a Lexoffice Account 
        """

        tmpFile.seek(0)  # Go back to beginning of file to read from tmpFile after writing

        try:
            c = pycurl.Curl()
            c.setopt(c.URL, self.apiUrl)
            c.setopt(c.POST, 1)
            c.setopt(c.HTTPPOST, [
                ("file", (
                     c.FORM_FILE, tmpFile.name,
                     c.FORM_FILENAME, parse.quote(fileName)
                 )
                 ),
                ("type", "voucher")
            ])
            c.setopt(pycurl.HTTPHEADER, [
                f"Authorization: Bearer {self.apiToken}",
                "Content-Type: multipart/form-data",
                "Accept: application/json"
            ])
            response = c.perform_rs()
            c.close()
            return response

        except Exception as e:
            exit("Error: File upload failed\n\n" + str(e))
