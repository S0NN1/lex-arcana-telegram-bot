# Lex Arcana Telegram Bot

<img src="https://res.cloudinary.com/s0nn1/image/upload/v1630483709/photo_2021-07-22_14-08-34_nnizhb.jpg" width=300 height=300 align="right"/>

Telegram bot implementing Lex Arcana using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library.

This bot was evaluated for the course "**Computer Engineering Project**" of Politecnico di Milano.

**Teacher**: [Giovanni Agosta](https://github.com/agosta).

**Final Score**: 30/30 cum laude.

**Bot username**: [@lex_arcana_bot](https://t.me/lex_arcana_bot)

Further information can be found in the bot description.

## Installation

### Requirements

- Python 3.8.10 o superiore.

### Procedure

In order to run and test the bot, clone the repo and install the dependencies through `pip` command:

```bash
git clone https://github.com/S0NN1/lex-arcana-telegram-bot.git

cd lex-arcana-telegram-bot

pip3 install -r requirements.txt

python3 main.py
```

If you want to create a service via `systemctl` to run the bot in the background you can use the provided configuration and change the paths in it:

```bash
[Unit]
Description=Lex Arcana

[Service]
Type=simple
Restart=always
RestartSec=5
ExecStart=/home/sonny/.pyenv/shims/python /home/sonny/master/main.py
WorkingDirectory=/home/sonny/master

[Install]
WantedBy=multi-user.target
```

Remember to create a `.env` file in the repo directory and insert the **BotFather** token like this:

```.env
TOKEN=<bot father token>
```

## Screenshots

![](https://res.cloudinary.com/s0nn1/image/upload/v1630568664/telegram-bot/image_2021-09-01_18-54-58_qn4c0w.png)

<p float="center">
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568665/telegram-bot/image_2021-09-01_18-56-20_jmgzsx.png" width="480" />
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568665/telegram-bot/image_2021-09-01_18-56-14_nhjbpq.png" width="480" /> 
</p>

<p float="center">
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568665/telegram-bot/image_2021-09-01_18-58-57_zstjev.png" width="480" />
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568665/telegram-bot/image_2021-09-01_18-59-41_sixzvw.png" width="480" /> 
</p>

<p float="center">
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568665/telegram-bot/image_2021-09-01_19-02-42_dona0w.png" width="480" />
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568664/telegram-bot/Telegram_WGWlLVrx7p_tbs5bv.png" width="480" /> 
</p>

<p float="center">
  <img src="https://res.cloudinary.com/s0nn1/image/upload/v1630568664/telegram-bot/image_2021-09-01_19-03-15_zazb0y.png" width="480" />
</p>
