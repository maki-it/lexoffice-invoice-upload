from setuptools import setup

setup(
   name='lexoffice-voucher-upload',
   version='0.1',
   description='Upload your vouchers/invoices from email attachements to Lexoffice.',
   author='Maki IT - Kim Oliver Drechsel',
   author_email='kontakt@maki-it.de',
   packages=['lexoffice-voucher-upload'],
   install_requires=['configparser~=5.3.0', 'columnar~=1.4.1', 'pycurl~=7.45.1'],
)