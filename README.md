# Lexoffice Voucher Upload

Upload your vouchers/invoices from email attachements to Lexoffice.

# Requirements
See `requirements.txt`
- pycurl (If installation fails you can try to install from the [unofficial binary](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycurl), see this  [stackoverflow comment](https://stackoverflow.com/a/53598619/6679493) for more details)

# Usage
1. Install requirements `pip install -r /path/to/requirements.txt`
2. Specify your configuration in `config.ini`
3. run `python main.py` 
4. Mails in specified maildir will automatically be searched for attachements with the configured file extension, then downloaed und uploaded to Lexoffice via their API.