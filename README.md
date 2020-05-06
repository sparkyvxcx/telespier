# Teleepier

A Simple Telegram Surveillance Tools

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```bash
$ python3 -m pip install telethon
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```bash
$ git clone https://github.com/sparkyvxcx/Teleespier
```

And test run
```bash
$ python3 espier.py
```

```
Usage:  python3 espier.py [Option]

        -h Show help info.
        -l Login into the account and get all the uid of all the dialogs.
        -b Only start the handler bot mode.
        -s Only start the surveillance mode.
        -d Deploy both the surveillance and handler bot.
```

End with an example of getting some data out of the system or using it for a little demo

## Running pre-operation configuration

1. Obtain your Telegram API id and API key by follow the procedures from [here](https://core.telegram.org/api/obtaining_api_id).

Usage Example:

```json
{
  "admin": [
    admin_id1,
    admin_id2
  ],
  "api_id": 777000,
  "api_hash": "1234213718rh4660f1a99208f289h9224g0124c7323fe",
  "bot_token": "Your_Bot_Token",
  "recv_channel": [
    receiver_channel_id
  ],
  "special_watchlist": [
        "userid:channleid"
  ],
  "group_watchlist": [
    gourp_id
  ],
  "user_watchlist": [
    user_id1,
    user_id2,
    user_id3
  ]
}
```

2. Create and obtain Telegram Bot token by follow the instructions from [here](https://core.telegram.org/bots).

Usage Example:

```json
{
  "admin": [
    admin_id1,
    admin_id2
  ],
  "api_id": 777000,
  "api_hash": "1234213718rh4660f1a99208f289h9224g0124c7323fe",
  "bot_token": "777000:YUW8-GCHQY1nry9p0RUc7Xvivv97z14cGM,
  "recv_channel": [
    receiver_channel_id
  ],
  "special_watchlist": [
        "userid:channleid"
  ],
  "group_watchlist": [
    gourp_id
  ],
  "user_watchlist": [
    user_id1,
    user_id2,
    user_id3
  ]
}
```

3. Create your receiver channle for logging purpose.

### Pull chat info from your account

```
$ python3 espier.py -l
```

Wait for query to complete, the result will be saved into `list.txt`,  with the format like `chat_id | char_name`.

Example:

```tex
 1316798278 | Fail2Hack
 1133183679 | Machine Learning
 1285896924 | 612 Reminder
 822294332  | HowToFind Bot
 777000     | Telegram
 784868894  | TEST
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Telethon](https://github.com/LonamiWebs/Telethon) - Pure Python 3 MTProto API Telegram client library

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration [telegram-recorder](https://github.com/abusetelegram/telegram-recorder)
* etc
