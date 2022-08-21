from setuptools import setup

setup(
   name='lexoffice-voucher-upload',
   version='0.1',
   description='Upload your vouchers/invoices from email attachements to Lexoffice.',
   author='Maki IT - Kim Oliver Drechsel',
   author_email='kontakt@maki-it.de',
   packages=['lexoffice-voucher-upload'],  # would be the same as name
   install_requires=['wheel', 'bar', 'greek'], #external packages acting as dependencies
)