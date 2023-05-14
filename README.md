# Lexoffice Invoice Upload

Upload your invoices from email attachements automatically to Lexoffice.

# Usage

## Usage with Docker

See [`docker-compose.yml`](docker-compose.yml) for an example configuration.

After starting the container once, it will generate a default `config.ini` in the volume `/app/config/`.
Alternatively you can copy the example [`config.ini`](config.ini) in this repository.
Change the settings in that file and then restart the container.
You can add as many configuration files as you like to this directory and also name them as you like. 
The program will iterate over all of them in alphabetical order.

### Tags

- Use the `latest` tag, to benefit from weekly updates for packages and security patches even between released versions.
- Use the version tags for fixed image states.

### Environment variables

You can adjust some options in the container with the following environment variables:

| Name | Description                                                                                                                | Default       |
|------|----------------------------------------------------------------------------------------------------------------------------|---------------|
| CRON | Defines the check schedule in a Cron-like expression.<br/>See [crontab.guru](https://crontab.guru/) for examples and help. | */5 * * * *   |
| TZ   | Defines the time zone in the container in TZ data format.                                                                  | Europe/Berlin |

## Usage on CLI

### Installation / Setup

1. Install requirements `pip install -r requirements.txt` (Also see [Requirements](#requirements) section below)
2. Specify your configuration in `config.ini` (you can generate a config file with `python3 main.py --generate`
   or `python3 main.py --generate --configfile /my/destination/mycustomconfig.conf`)
3. Run `python3 main.py`
4. Mails in specified maildir will automatically be searched for attachements with the configured file extension, then
   downloaded und uploaded to Lexoffice via their API.

### Requirements

- See [`requirements.txt`](requirements.txt)
- **pycurl**: The installation of pycurl can give you a hard time. Here is what worked for me on Windows, MacOS and Ubuntu.
    - **Windows**: If installation fails you can try to install from
      the [unofficial binary](https://www.lfd.uci.e~du/~gohlke/pythonlibs/#pycurl), see
      this  [stackoverflow comment](https://stackoverflow.com/a/53598619/6679493) for more details)
    - **MacOS**: Run the following
        ```bash
        brew install openssl
        export PYCURL_SSL_LIBRARY=openssl
        export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
        export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
        pip3 install --no-cache-dir --ignore-installed --compile --install-option="--with-openssl" pycurl
        ```
    - **Linux**:  (tested on Ubuntu 20.04)
        1. Install requirements:
            ```bash
            apt install libssl-dev libcurl4-openssl-dev libcurl4-gnutls-dev libgnutls-dev python3-dev
            ```
           If you get the error Package *libgnutls-dev* is not available, then instead of `libgnutls-dev`
           install `libgnutls28-dev`

           If this also doesn't work (or `apt` says you have unmet dependencies), try to install everything
           with `aptitude` instead of `apt`:
            ```bash
            aptitude install libssl-dev libcurl4-openssl-dev libcurl4-gnutls-dev python3-dev
            ```

        2. Then install `pycurl`:
            ```bash
            pip3 install pycurl
            ```

### CLI Arguments

- `-h`, `--help` show the help message
- `-f FILE`, `--configfile FILE` specify the config file to use. If nothing is specified, `./config.ini` will be used.
  Use `*` as wildcard to specify multiple config files (`config_*.ini`)
- `-q`, `--quiet` don't print status messages to stdout.
- `-g`, `--generate` generate a new configruation file, optionally specify path and filename with `--config` argument.
- `-l`, `--loop`, `--continuous` Enable loop/continuous mode. In this mode, the script runs through the given
  configuration(s) in an infinite loop. The default interval between each run is 120 seconds.
- `-c "m h dom mon dow"`, `--cron "m h dom mon dow"` specify the schedule in cron-style format (minute hour day-of-month
  month day-of-week). See https://crontab.guru/ for examples and help about schedule expressions. Only takes effect in
  loop/continuous mode. Default is 5 minutes.

### CLI with multiple config files

If you have more than one mailbox to check or want to separate you configurations, you can create multiple config files
and iterate/loop over them like with a simple bash script:

```bash
# Generate config files from template with specific destination and file name
python3 main.py --generate --configfile /path/to/config/mailbox_tom.ini
python3 main.py --generate --configfile /path/to/config/aws-invoices.ini
python3 main.py --generate --configfile /path/to/config/amazon_business.ini

# Run program with multiple configuration files
python3 main.py --configfile /path/to/config/config*.ini >> logfile.log
```
