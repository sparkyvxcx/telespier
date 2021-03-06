![logo](https://raw.githubusercontent.com/sparkyvxcx/telespier/master/img/logo.png)

**A Simple Telegram Surveillance Tool**

The purpose of this tool is to conduct OSINT ops for me. It is free software so that you can use it and modify it for your needs. Please file a bug report if something does not work as documented or expected.

## Getting Started

By exploit normal user account's ability to forward and logging group chat or channel, this simple tool forward messages from a targeted user in a specific group chat with a normal user account, not a bot, hence a smaller chance to get caught. These instructions will get you a copy of the project up and running on your local machine or Cloud Host for intel gathering and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project use telethon api library to interact with Telegram api, install telethon library before procced to deploy.

```shell
$ python3 -m pip install telethon
```

### Installing

Clone or download the project:

```shell
$ git clone https://github.com/sparkyvxcx/telespier
```

Test run:

```shell
$ python3 espier.py
```

```shell
Usage:  python3 espier.py [Option]

        -h Show help info.
        -l Login into the account and get all the uid of all the dialogs.
        -b Only start the handler bot mode.
        -s Only start the surveillance mode.
        -d Deploy both the surveillance and handler bot.
```

## Running pre-operation configuration

#### 1. Obtain your Telegram API id and API key by follow the procedures from [here](https://core.telegram.org/api/obtaining_api_id)

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
        "userid:channelid"
  ],
  "group_watchlist": [
    group_id
  ],
  "user_watchlist": [
    user_id1,
    user_id2,
    user_id3
  ]
}
```

#### 2. Create and obtain Telegram Bot token by follow the instructions from [here](https://core.telegram.org/bots)

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
        "userid:channelid"
  ],
  "group_watchlist": [
    group_id
  ],
  "user_watchlist": [
    user_id1,
    user_id2,
    user_id3
  ]
}
```

#### 3. Create your receiver channel

E.g. set a receiver channel named: `Eavesdroping`

For specific user monitoring, say you have a specific targeted user, you should create another channel for this user. After obtain this user's uid, hardcode it with id of the channel you created for this special user in a format like `user_id:channelid` into the `special_watchlist` field.

Example:

- tango1's uid: `12345678`

- Receiver channel for tango1: `87654321` and so on

```json
...
  "special_watchlist": [
        "12345678:87654321"
  ],
...
```

### Pull chat info from your account

**Note:** In order to gather more reasonable and useful chat info from start, user better join some groups he/she wanna to watch(spying) xD.

Query all the chat list (Groups, Channles, Chats, etc) from your account:

```shell
$ python3 espier.py -l
```

Wait for query to complete, the result will be saved into `list.txt`,  with the format like `chat_id | chat_name`.

Example:

```shell
 1316798278 | Fail2Hack
 1133183679 | Machine Learning
 1285896924 | 612 Reminder
 822294332  | HowToFind Bot
 777000     | Telegram
 784868894  | TEST
 123456789  | Eavesdroping <= Your receiver channel
```

Now obtain the id of receiver channel from `list.txt`, open `data.json` and replace placeholder `receiver_channel_id` with your receiver channel id, so do `group_id` and `user_id`. `admin_id` shouldb be your account uid or other sockpuppet account uid under your control. It is okay to leave `admin` array and `user_watchlist` array empty. 

Example config file ready to rock: 

```json
{
  "admin": [
  ],
  "api_id": 777000,
  "api_hash": "1234213718rh4660f1a99208f289h9224g0124c7323fe",
  "bot_token": "777000:YUW8-GCHQY1nry9p0RUc7Xvivv97z14cGM,
  "recv_channel": [
    receiver_channel_id
  ],
  "special_watchlist": [
        "userid:channelid"
  ],
  "group_watchlist": [
    1316798278
  ],
  "user_watchlist": [
  ]
}
```

## Deployment

Deploy logging "bot":

```shell
$ python3 espier.py -s
```

Without handler bot, we cannnot update user and group watchlist on the fly, but user is cool to modifiy `data.json` to update user and group watchlist. After update `data.json` file, user need to restart the application to reload `data.json`.

Deploy logging "bot" and handler bot:

```shell
$ python3 espier.py -d
```

With handler bot running, we are capable of updating user or group watchlist on the fly by interacting with handler bot.

Bot command (You can add more features or commands as your will):

- `/add target_type target_id`
- `/del target_type target_id`
- `/dig target_type target_id`
- `/show`
- `/save`

Example:

![bot-command](https://raw.githubusercontent.com/sparkyvxcx/telespier/master/img/ss1.png)

Add keyword `Expolit`, `CVE`, `Hacker`, and test it out:

![add-keyword](https://raw.githubusercontent.com/sparkyvxcx/telespier/master/img/ss2.png)

Receiver channel:

![forward-message](https://raw.githubusercontent.com/sparkyvxcx/telespier/master/img/ss3.png)

This is an ad-hoc toy project, not meant for real-world scenario. For a better solution, I recommend [informer](https://github.com/paulpierre/informer) 👋.



## Built With

* [Telethon](https://github.com/LonamiWebs/Telethon) - Pure Python 3 MTProto API Telegram client library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration [telegram-recorder](https://github.com/abusetelegram/telegram-recorder)
* etc
