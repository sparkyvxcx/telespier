from telethon import TelegramClient, events
from random import randint
import asyncio, json

bot_id = <bot-id>
api_id = <bot-id>
api_hash = "<bot-hash>"
bot_token = "<bot-token>"

admins = [0000000, 1111111]
info = {}
keywords = []
userlist = []
grouplist = []

handler = TelegramClient('handler', api_id, api_hash).start(bot_token=bot_token)

async def eavesdropper(event):
    global handler
    try:
        suid = event.input_sender.user_id
        if suid not in whitelist:
            fwd = await handler.forward_messages(
                entity=receiver,                # forwarding destination (group id)?
                messages=[event.message.id],    # message content
                from_peer=event.message.to_id,  # who send these message?
                silent=True
                )
            hint = 'User ID: [{0}](tg://user?id={0})'.format(suid)
            await handler.send_message(receiver, hint , parse_mode='md', silent=True)
            print(str(event.input_sender))
    except Exception as error:
        print(error)
        return 0

def auth(sid):
    global admins
    if sid in admins:
        return True
    else:
        return False

    # if auth(senderID):
    #     pass
    # else:
    #     pass

@handler.on(events.NewMessage(pattern='/start'))
async def start(event):
    ## Send a message when the command /start is issued.
    ## Randomly respond with a Hi! in 8 languages.

    sayHi = ['Hi! 😊', 'Good day! 😂', 'Bonjour! 😄', 'Hola! 🥰', 'السلام عليكم! 😘', 'Привет! 😎', 'こんにちは! 😍', 'Guten Tag! 😋']
    chatID = event.message.chat_id
    senderID = event.message.from_id
    if auth(senderID):
        pass
    else:
        debug_info = "[{}] {} {}".format(colour('*', 'blue'), colour('User ID:', 'green'), senderID)
        print(debug_info)
    i = randint(0, 8)
    async with handler.action(chatID, 'typing'):
        await asyncio.sleep(2)
        await event.respond(sayHi[i])
    raise events.StopPropagation

@handler.on(events.NewMessage(pattern='/help'))
async def send_welcome(event):
    ## Send a message when the command /help is issued.

    #await eavesdropper(event)
    to_id = event.message.chat_id

    async with handler.action(to_id, 'typing'):
        await asyncio.sleep(3)
        await event.reply("Howdy, how y'all doing?")
    raise events.StopPropagation

@handler.on(events.NewMessage(pattern='/add'))
async def add(event):
    global userlist, grouplist, keywords
    senderID = event.message.from_id
    if auth(senderID):
        pass
    input_cmd = event.message.message

    parameters = input_cmd.split(' ')
    pl = len(parameters)
    if pl == 3:
        t, v = parameters[1], parameters[2]
        if t == 'keyword':
            if v in keywords:
                # send message!
                message = 'Looks like {} `{}` is already in the watchlist, stay tune!'.format(str(t).title(), v)
            else:
                keywords.append(v)
                message = 'Tada! {} `{}` is in the watchlist now.'.format(str(t).title(), v)
        elif t == 'user':
            try:
                v = int(v)
            except ValueError:
                # invalid input
                message = 'Seems like `{}` is not a valid input for **{}** watchlist!'.format(v, t)
            else:
                if v in userlist:
                    # send message!
                    message = 'Opps, {} `{}` is already in the watchlist, stay tune!'.format(str(t).title(), v)
                else:
                    userlist.append(v)
                    message = 'OK, {} `{}` is in the watchlist now.'.format(str(t).title(), v)
        elif t == 'group':
            try:
                v = int(v)
            except ValueError:
                # invalid input
                message = 'Seems like `{}` is not a valid input for **{}** watchlist!'.format(v, t)
            else:
                if v in grouplist:
                    # send message!
                    message = 'Opps, {} `{}` is already in the watchlist, stay tune!'.format(str(t).title(), v)
                else:
                    grouplist.append(v)
                    message = 'OK, {} `{}` is in the watchlist now.'.format(str(t).title(), v)
    else:
        message = 'Dude! What the heck you talk in about?'
    await event.respond(message)
    raise events.StopPropagation

@handler.on(events.NewMessage(pattern='/del'))
async def remove(event):
    global userlist, grouplist, keywords
    senderID = event.message.from_id
    if auth(senderID):
        pass
    input_cmd = event.message.message

    parameters = input_cmd.split(' ')
    pl = len(parameters)
    if pl == 3:
        t, v = parameters[1], parameters[2]
        if t == 'keyword':
            if v not in keywords:
                # send message!
                message = 'Looks like {} `{}` is not in the watchlist, stay tune!'.format(str(t).title(), v)
            else:
                keywords.remove(v)
                message = 'Tada! {} `{}` is removed from the watchlist now.'.format(str(t).title(), v)
        elif t == 'user':
            try:
                v = int(v)
            except ValueError:
                # invalid input
                message = 'Seems like `{}` is not a valid value for **{}** watchlist!'.format(v, t)
            else:
                if v not in userlist:
                    # send message!
                    message = 'Opps, {} `{}` is not in the watchlist, stay tune!'.format(str(t).title(), v)
                else:
                    userlist.remove(v)
                    message = 'OK, {} `{}` is removed from the watchlist now.'.format(str(t).title(), v)
        elif t == 'group':
            try:
                v = int(v)
            except ValueError:
                # invalid input
                message = 'Seems like `{}` is not a valid value for **{}** watchlist!'.format(v, t)
            else:
                if v not in grouplist:
                    # send message!
                    message = 'Opps, {} `{}` is not in the watchlist, stay tune!'.format(str(t).title(), v)
                else:
                    grouplist.remove(v)
                    message = 'OK, {} `{}` is removed from the watchlist now.'.format(str(t).title(), v)
    else:
        message = 'Dude! What the heck you talk in about?'
    await event.respond(message)
    raise events.StopPropagation

@handler.on(events.NewMessage(pattern='/show'))
async def show(event):
    global grouplist, userlist
    senderID = event.message.from_id
    if auth(senderID):
        pass
    # output = '== **Watchlist** ==\nUser:\n'
    # for i in range(len(userlist)):
    #   uid = userlist[i]
    #   if i < 9:
    #       index = '  {}'.format(str(i+1))
    #   else:
    #       index = str(i+1)
    #   text = "{0}. [{1}](tg://user?id={1})\n".format(index, uid)
    #   output = output + text

    # output = output + '\nGroup:\n'
    # for i in range(len(grouplist)):
    #   uid = grouplist[i]
    #   if i < 9:
    #       index = '  {}'.format(str(i+1))
    #   else:
    #       index = str(i+1)
    #   text = "{0}. [{1}](tg://user?id={1})\n".format(index, uid)
    #   output = output + text
    tables = """
| Index |    User ID    | Comment |
|-------|---------------|---------|
|   1   |   527033069   |  $1600  |
|   2   |   527033069   |    $12  |
|   3   |   527033069   |     $1  |
"""
    output = """
`
---------------------
Index |   User ID   
-------|-------------
"""
    for i in range(len(userlist)):
        uid = userlist[i]
        if i < 9:
            index = ' {}'.format(str(i+1))
        else:
            index = str(i+1)
        suid = str(uid)
        space = (11 - len(suid)) * ' '
        x = "|   1   |   527033069   | Comment |"
        text = "  {0}   |  {1}\n".format(index, uid)
        #text = "{0}. [{1}](tg://user?id={1})\n".format(index, uid)
        output = output + text
    output = output + '---------------------`'
    await event.respond(output)
    raise events.StopPropagation

@handler.on(events.NewMessage(pattern='/save'))
async def save(event):
    senderID = event.message.from_id
    if auth(senderID):
        pass
    dump()
    await event.respond("Don't worry, Watchlist saved!")
    raise events.StopPropagation

def load():
    ## Load Basic configuration (api_id, api_hash, watchlist, etc) from data.json.
    ## Keep configuration in info a dict object.
    
    global info, keywords, grouplist, userlist
    data_file = "./data.json"
    keyword_file = "./keyword.txt"
    try:
        with open(data_file, 'r') as data:
            Data = data.read()
        info = json.loads(Data)

        # print(info['admin'])
        # print(info['api_id'])
        # print(info['api_hash'])
        # print(info['group_watchlist'])
        # print(type(info['user_watchlist']))
        # print(info['recv_channel'][0])

        grouplist = info['group_watchlist']
        userlist = info['user_watchlist']
    except Exception as err:
        print('[{}] Failed! :( [ERROR] {}'.format(colour('-', 'red'), err))
    else:
        print('[{}] Load Configuration'.format(colour('*', 'blue')))
    try:
        with open(keyword_file, 'r') as data:
            Data = data.readlines()
        for i in Data:
            keywords.append(i.strip())
    except Exception as err:
        print('[{}] Failed! :( [ERROR] {}'.format(colour('-', 'red'), err))
    else:
        print('[{}] Load keyword list'.format(colour('*', 'blue')))
    return 0

def dump():
    global info, userlist, grouplist, keywords
    info['user_watchlist'] = userlist
    info['group_watchlist'] = grouplist
    data_file = "./data.json"
    cache_object = open("./data.json", 'w')
    json.dump(info, cache_object)

    keyword_file = "./keyword.txt"
    try:
        with open(keyword_file, 'r') as data:
            for i in keywords:
                data.write(i + '\n')
    except Exception as err:
        print('[{}] Failed! :( [ERROR] {}'.format(colour('-', 'red'), err))

def colour(s, hue):
    palette = {
        'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
        'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37,
    }
    return "\033[{}m{}\033[0m".format(palette[hue], s)

def main():
    ## Start the bot.

    load()
    print('[' + colour('+', 'green') + '] Running Handler Operation')
    handler.run_until_disconnected()

if __name__ == '__main__':
    main()
