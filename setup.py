from setuptools import setup

setup(
   name='lexoffice-invoice-upload',
   version='0.1',
   description='Upload your invoices from email attachements to Lexoffice.',
   author='Maki IT - Kim Oliver Drechsel',
   author_email='kontakt@maki-it.de',
   packages=['lexoffice-invoice-upload'],
   install_requires=['configparser~=5.3.0', 'columnar~=1.4.1', 'pycurl~=7.45.1'],
)