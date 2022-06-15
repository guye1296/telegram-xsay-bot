# Telegram XSay Bot

An `xcowsay`-like telegram bot`


## Commands

```
/random - Generate a random image
```


## Installation

- [Create a telegram bot](https://t.me/botfather) and obtain an uniqute Telegram API Token 

```bash
git clone https://github.com/guye1296/telegram-xsay-bot.git <CLONE_DIR>
cd <CLONE_DIR>
python -m pip install -e .
```

When installing the `run_xsay_telegram_bot` script is installed on your system.


## Running the Bot

Run the Bot via the `run_xsay_telegram_bot` scripts:

```
usage: run_xsay_telegram_bot [-h] api_token image_templates_file_path phrase_file_path

positional arguments:
  api_token             Telegram API token. Get one from @BotFather
  image_templates_file_path
                        Path to the image templates file
  phrase_file_path      Path to a file containing sentences to display

optional arguments:
  -h, --help            show this help message and exit
```

Both the `image_templates_file_path` and `phrase_file_path` arguments have a sample file available at [samples](samples/).