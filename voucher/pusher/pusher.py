from urllib import response
import pycurl


class LexofficePush:
    """
    Class to upload voucher files 
    """
    def __init__(self, apiToken: str) -> None:
        self.apiUrl = 'https://api.lexoffice.io/v1/files'
        self.apiToken = apiToken

    def fileUpload(self, fileDir: str, fileName: str):
        """
        Upload a file to a Lexoffice Account 
        """

        try:
            c = pycurl.Curl()
            c.setopt(c.URL, self.apiUrl)
            c.setopt(c.POST, 1)
            c.setopt(c.HTTPPOST, [
                ("file", (c.FORM_FILE, f"{fileDir}/{fileName}")),
                ("type", "voucher")
            ])
            c.setopt(pycurl.HTTPHEADER, [
                f"Authorization: Bearer {self.apiToken}",
                "Content-Type: multipart/form-data",
                "Accept: application/json"
            ])
            c.perform()
            c.close()
            print()
        except Exception as e:
            exit("Error: File upload failed.\n" + e)
