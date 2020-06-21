#/usr/bin/env python3

import threading
import asyncio
import json
import time
import sys
import re

from base64 import b64encode
from random import randint

from telethon import TelegramClient, events, utils
from telethon.extensions.markdown import parse
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.channels import GetChannelsRequest
from telethon.tl.functions.users import GetUsersRequest
from telethon.tl.types import *

client = ''
info = {}
admin = []
keywords = []
userlist = []
grouplist = []
speciallist = []
proxies = []
pmid = 1

def login():
    """
    Log into operating telegram account and fetch chatlist from this account.
    """

    global client, info
    try:
        client = TelegramClient('espier', info['api_id'], info['api_hash'])
        print('[' + colour('*', 'blue') +'] If you have 2FA password, please enter it now.')
        password = input(colour(' ➜  ', 'green'))
    
        if password != '':
            client.start(password=password)
        else:
            client.start()
    except KeyboardInterrupt:
        print()
        print("[\033[1;31m-\033[0m] Operation abort! >_<")
        return False
    else:
        print('[' + colour('+', 'green') +'] Login successed!')

        loop = asyncio.get_event_loop()
        with client:
            client.loop.run_until_complete(get_id())
        return True

def colour(s, hue):
    palette = {
        'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
        'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37,
    }
    return "\033[{}m{}\033[0m".format(palette[hue], s)

async def get_id():
    """
    Get all the channel, groups, chats id you have.

    To do: display those information at run time, like this:
           1) archlinux (2137098721)
           2) manjaroen (987213681)
              ...
           ?) name (id)
    """

    global client

    dialogs = await client.get_dialogs(limit=None)

    result = "| ID           | Chat Name\n"
    for dialog in dialogs:
        chatid = str(dialog.entity.id)
        # Note: Currently, the length of telegram uid is 10, change it accordingly for future growth.
        item = "| {:10} | {}\r\n"  
        result += item.format(chatid, str(dialog.name))
    with open("list.txt", "w") as f:
        f.write(result)
    print('[' + colour('+', 'green') +'] Information saved into list.txt')

def load():
    """
    Load Basic information (api_id, api_hash, watchlist, etc) from data.json
    Save all that information in info dict
    """
    
    global info, keywords, grouplist, userlist, speciallist, admin
    data_file = "./data.json"
    keyword_file = "./keyword.txt"
    try:
        with open(data_file, 'r') as data:
            Data = data.read()
        info = json.loads(Data)

        speciallist = info['special_watchlist']
        grouplist = info['group_watchlist']
        userlist = info['user_watchlist']
        admin = info['admin']
    except Exception as err:
        print('[{}] Load Configuration Failed! :( \n[ERROR] {}'.format(colour('-', 'red'), err))
        return False
    else:
        print('[{}] Load Configuration'.format(colour('*', 'blue')))
    try:
        with open(keyword_file, 'r') as data:
            Data = data.readlines()
        for i in Data:
            keywords.append(i.strip())
    except Exception as err:
        print('[{}] Load keyword list Failed! :(\n[ERROR] {}'.format(colour('-', 'red'), err))
    else:
        print('[{}] Load keyword list'.format(colour('*', 'blue')))
    return True

def dump():
    """
    Dump current watchlists into disk
    """

    global info, userlist, grouplist, speciallist, keywords
    info['user_watchlist'] = userlist
    info['group_watchlist'] = grouplist
    info['special_watchlist'] = speciallist
    data_file = "./data.json"
    cache_object = open("./data.json", 'w')
    json.dump(info, cache_object)

    keyword_file = "./keyword.txt"
    try:
        with open(keyword_file, 'w') as data:
            for i in keywords:
                data.write(i + '\n')
    except Exception as err:
        print('[{}] Failed! :( [ERROR] {}'.format(colour('-', 'red'), err))

def surveillance():
    global info
    loop = asyncio.new_event_loop()
    client = TelegramClient('espier', info['api_id'], info['api_hash'], loop=loop)
    receiver = PeerChannel(info['recv_channel'][0])

    @client.on(events.NewMessage(incoming=True))
    async def event_handler(event):
        global keyword, userlist, grouplist, speciallist

        # Debbug printer
        def printer(event):
            print('==================== Income new message ====================')
            print('\033[1;32mSender:\033[0m ' + str(sender))
            print('\033[1;31mReceiver:\033[0m  ' + str(to_id))
            if event.raw_text == '':
                print('\033[1;37mMessage:\033[0m   message does not contain text')
            else:
                print('\033[1;37mMessage:\033[0m   ' + str(event.raw_text).replace('\n', '\n           '))
            print('============================================================\n ')

        # Logger
        def logger(event):
            if event.raw_text == '':
                print('message does not contain text')
            else:
                print(event.raw_text)

        # Based on message type (mtype) to format message to send
        def sendMessage(compose, mtype):
            user = """`Sender: {1} [`[{0}](tg://user?id={0})`]`""".format(compose[0][0], compose[0][1])
            group = """`Group:  {1} [`{0}`]`\n""".format(compose[1][0], compose[1][1])

            result = ''

            if mtype == 'group':
                # Group Listener
                result = group
            elif mtype == 'user':
                # User Listener
                result = user
            else:
                result = user + '\r\n' + group

            return result

        # Format user info and group info
        async def compose(sid, rid):
            user = await client(GetUsersRequest([sid]))
            user = user[0]
            name = ''
            if user.first_name is not None:
                name = name + user.first_name
            if user.last_name is not None:
                name = name + ' ' + user.last_name
            u = [user.id, name]
            group = await client(GetChannelsRequest([rid]))
            group = group.chats[0]
            g = [group.id, group.title]
            return [u, g]

        async def proxyScan(text):
            global proxies, pmid

            pattern = "(?:[a-zA-Z.:/]+)(?:proxy\?server=(?:[a-zA-Z0-9\.-_~]+)(?:&port=[0-9]{1,5}&secret=[a-zA-Z0-9]+))"
            title = "`Telegram MTProto Proxy`"
            field = "\n[🚀 {} {}]({})"
            sline = "\n`----------------------`"
            items = ""
            proxyList = re.findall(pattern, text)
            if len(proxyList) == 0:
                return
            proxies = proxies + proxyList
            for i in range(len(proxies)):
                items = items + field.format("Proxy", i+1, proxies[i])
            sline = "{2}{0}{1}{0}".format(sline, items, title)
            print(sline)
            try:
                if pmid == 1:
                    pMessage = await client.send_message(receiver, sline, parse_mode='md')
                    pmid = pMessage.id
                else:
                    pMessage = await client.edit_message(receiver, pmid, sline, parse_mode='md')
                    pmid = pMessage.id
            except Exception as err:
                pMessage = await client.send_message(receiver, sline, parse_mode='md')
                pmid = pMessage.id
            return

        # Keyword scanner
        def keywordScan(text):
            global keywords
            if text is None:
                return False
            try:
                for word in keywords:
                    if word in text:
                        return word
            except Exception as e:
                print(e)
            return False

        to_id = event.message.to_id
        sender = event.input_sender
        content = event.message.message

        # Keyword check
        check = keywordScan(content)
        if check:
            hint = "**Keyword:**  {}".format(check)
            composed = await compose(sender, to_id)
            message = sendMessage(composed, mtype='all')
            message = hint + "\n" + message
            await client.send_message(receiver, message, parse_mode='md')
            fwd = await client(ForwardMessagesRequest(from_peer=to_id, id=[event.message.id], to_peer=receiver))
            # print("Keyword hit!")

        # Group check
        # Add more IF condition accordingly if you want to listen more event.
        if int(to_id.channel_id) in grouplist and event.out is False:
            # Forword message to receiver channel
            fwd = await client(ForwardMessagesRequest(
                from_peer=event.message.to_id,  # sender of this intercepted message
                id=[event.message.id],          # id of this intercepted messages
                to_peer=receiver                # receiver channel id
            ))
            composed = await compose(sender, to_id)
            message = sendMessage(composed, mtype='all')
            await client.send_message(receiver, message, parse_mode='md')
            # print("Group hit!")
        # User check
        elif int(event.input_sender.user_id) in userlist:
            # Forword message to receiver channel
            fwd = await client(ForwardMessagesRequest(
                from_peer=event.message.to_id,  # sender of this intercepted message
                id=[event.message.id],          # id of this intercepted messages
                to_peer=receiver                # receiver channel id
            ))
            composed = await compose(sender, to_id)
            message = sendMessage(composed, mtype='all')
            await client.send_message(receiver, message, parse_mode='md')
            # print("User hit!")

        # Special targeted user check
        target_id = int(event.input_sender.user_id)
        for i in speciallist:
            if str(target_id) in i:
                special_channel = int(i.split(":")[1])
                fwd = await client(ForwardMessagesRequest(
                    from_peer=event.message.to_id,  # sender of this intercepted message
                    id=[event.message.id],          # id of this intercepted messages
                    to_peer=special_channel         # receiver channel id
                ))
                # print("Target hit!")
                break
    
    print('[' + colour('+', 'green') +'] Running surveillance operation!')
    with client:
        client.run_until_disconnected()

def operationHandler():
    """
    handle add, delte, dig, operation using telegram bot
    Todo: currently qurey, add, delete function are ad hoc solution, not efficient nor readible for sure.
          1. refactory CURD functions.
          2. detailed help information when legitimate user calling /help.
          3. able to show detailed information for targeted user, group.
          4. add SQL database for further data persistence.
    """

    global info

    loop = asyncio.new_event_loop()
    handler = TelegramClient('handler', info['api_id'], info['api_hash'], loop=loop).start(bot_token=info['bot_token'])

    # Check a given user id is admin or not
    def auth(sid):
        global admin
        if sid in admin:
            return True
        else:
            return False

    @handler.on(events.NewMessage(pattern='/start'))
    async def start(event):
        """
        Send a message when the command /start is issued.
        Randomly respond with a Hi!
        """

        sayHi = [
                'Hi! 😊',
                'Good day! 😂',
                'Bonjour! 😄',
                'Hola! 🥰',
                'السلام عليكم! 😘',
                'Привет! 😎',
                'こんにちは! 😍',
                'Guten Tag! 😋'
                ]
        chatID = event.message.chat_id
        senderID = event.message.from_id
        try:
            if auth(senderID):
                pass
            else:
                debug_info = "[{}] {} {}".format(colour('*', 'blue'), colour('User ID:', 'green'), senderID)
                print(debug_info)
        except Exception as e:
            print(e)
        i = randint(0, 8)
        async with handler.action(chatID, 'typing'):
            await asyncio.sleep(2)
            await event.respond(sayHi[i])
        raise events.StopPropagation

    @handler.on(events.NewMessage(pattern='/help'))
    async def send_welcome(event):
        """
        Send a message when the command /help is issued.
        """

        to_id = event.message.chat_id

        senderID = event.message.from_id
        if auth(senderID):
            async with handler.action(to_id, 'typing'):
                await asyncio.sleep(3)
                await event.reply("Howdy, how y'all doing?")
        raise events.StopPropagation

    @handler.on(events.NewMessage(pattern='/add'))
    async def add(event):
        global userlist, grouplist, keywords

        # Admin authentication
        senderID = event.message.from_id
        if not auth(senderID):
            raise events.StopPropagation
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
        """
        Handle remove request for group, user, keyword list when /del is issued.
        """

        global userlist, grouplist, keywords
        senderID = event.message.from_id
        if not auth(senderID):
            raise events.StopPropagation
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

    @handler.on(events.NewMessage(pattern='/dig'))
    async def query(event):
        global userlist, grouplist, keywords

        senderID = event.message.from_id
        if not auth(senderID):
            raise events.StopPropagation
        input_cmd = event.message.message
    
        parameters = input_cmd.split(' ')
        pl = len(parameters)
        if pl == 3:
            t, v = parameters[1], parameters[2]
            if t == 'keyword':
                if v in keywords:
                    # send message!
                    message = '{} `{}` is already in the watchlist, stay tune!'.format(str(t).title(), v)
                else:
                    message = '{} `{}` is not in the watchlist, stay tune!'.format(str(t).title(), v)
            elif t == 'user':
                try:
                    v = int(v)
                except ValueError:
                    # invalid input
                    message = 'Seems like `{}` is not a valid input for **{}** watchlist!'.format(v, t)
                else:
                    try:
                        intel = ''
                        user = await handler.get_entity(v)
                        name = ''
                        if user.first_name is not None:
                            name = name + user.first_name
                        if user.last_name is not None:
                            name = name + ' ' + user.last_name
                    except Exception as e:
                        pass
                    else:
                        intel = "\nName: {1}  ([{0}](tg://user?id={0}))".format(v, name)
                    if v in userlist:
                        # send message!
                        message = 'Opps, {0} [{1}](tg://user?id={1}) is already in the watchlist, stay tune!'.format(str(t).title(), v)
                        message = message + intel
                    else:
                        message = 'Opps, {0} [{1}](tg://user?id={1}) is not in the watchlist.'.format(str(t).title(), v)
                        message = message + intel
            elif t == 'group':
                try:
                    v = int(v)
                except ValueError:
                    # invalid input
                    message = 'Seems like `{}` is not a valid input for **{}** watchlist!'.format(v, t)
                else:
                    try:
                        intel = ''
                        groupPeer = await handler.get_input_entity(v)
                        group = await handler(GetUsersRequest([groupPeer]))
                        group = group.chats[0]
                        g = [group.id, group.title]
                    except:
                        pass
                    else:
                        intel = "\nName: {1}  (`{0}`)\n".format(v, g[1])
                    user = await handler(GetUsersRequest([v]))
                    if v in grouplist:
                        # send message!
                        message = 'Opps, {} `{}` is already in the watchlist, stay tune!'.format(str(t).title(), v)
                        message = message + intel
                    else:
                        message = 'Opps, {} `{}` is not in the watchlist.'.format(str(t).title(), v)
                        message = message + intel
        else:
            message = 'Dude! What the heck you talk in about?'
        await event.respond(message)
        raise events.StopPropagation

    @handler.on(events.NewMessage(pattern='/show'))
    async def show(event):
        """
        Provide detailed information for group, user, keyword list when /show is issued.
        Todo: information should split into three different type, which are user, group, keyword.
              1. `/show user` should server detailed user information from user watchlist
              2. `/show group` should server detailed group information from group watchlist
              3. `/show keyword` should server detailed keyword information from keyword watchlist
        """

        global grouplist, userlist, keywords

        pUsers = """
**WATCHLIST**
User watchlist`
-------+-------------
 Index |   User ID   
-------+-------------
"""
        pGroups = """
**WATCHLIST**
Group watchlist`
-------+-------------
 Index |  Group ID   
-------+-------------
"""
        pKeywords = """
**WATCHLIST**
Keyword watchlist`
-------+-------------
 Index |   Keyword   
-------+-------------
"""
        input_cmd = event.message.message
        parameters = input_cmd.split(' ')

        senderID = event.message.from_id
        if not auth(senderID):
            raise events.StopPropagation

        async def userLink():
            output = '== **Watchlist** ==\nUserlink:\n'
            for i in range(len(userlist)):
                uid = userlist[i]
                if i < 9:
                    index = '  {}'.format(str(i+1))
                else:
                    index = str(i+1)
                text = "{0}. [{1}](tg://user?id={1})\n".format(index, uid)
                output = output + text
            await event.respond(output)
    
        async def groupLink():
            output = output + '\nGroup:\n'
            for i in range(len(grouplist)):
                uid = grouplist[i]
                if i < 9:
                    index = '  {}'.format(str(i+1))
                else:
                    index = str(i+1)
                text = "{0}. [{1}](tg://user?id={1})\n".format(index, uid)
                output = output + text
            await event.respond(output)

        async def summaryBuilder(watchlist, output):
            for i in range(len(watchlist)):
                content = watchlist[i]
                if i < 9:
                    index = ' {}'.format(str(i+1))
                else:
                    index = str(i+1)
                content = str(content)
                space = (11-len(content)) * ' '
                text = "  {0}   |  {1}\n".format(index, content)
                output = output + text
            output = output + '-------+-------------`'
            await event.respond(output)

        await summaryBuilder(userlist, pUsers)    # send user watchlist summary
        await summaryBuilder(grouplist, pGroups)  # send group watchlist summary
        await summaryBuilder(keywords, pKeywords) # send keyword watchlist summary
            
        raise events.StopPropagation

    @handler.on(events.NewMessage(pattern='/save'))
    async def save(event):
        # Save all of the watchlists into disk on the fly
        senderID = event.message.from_id
        if not auth(senderID):
            raise events.StopPropagation
        dump()
        await event.respond("Don't worry, Watchlist saved!")
        raise events.StopPropagation

    print('[' + colour('+', 'green') + '] Running handler operation!')
    handler.run_until_disconnected()

def deploy():
    """
    Deploy both survilance and handler function
    """

    tasks = []

    task1 = threading.Thread(target=surveillance)
    task2 = threading.Thread(target=operationHandler)
    tasks.append(task1)
    tasks.append(task2)
    try:
        for eachtask in tasks:
            eachtask.daemon=True
            eachtask.start()
        for eachtask in tasks:
            eachtask.join()
    except KeyboardInterrupt:
        print('\n[' + colour('-', 'red') + '] Operation shut down!')

def usage():
    logo = '''
         _           _            _        _          _            _      
        /\ \        / /\         /\ \     /\ \       /\ \         /\ \    
       /  \ \      / /  \       /  \ \    \ \ \     /  \ \       /  \ \   
      / /\ \ \    / / /\ \__   / /\ \ \   /\ \_\   / /\ \ \     / /\ \ \  
     / / /\ \_\  / / /\ \___\ / / /\ \_\ / /\/_/  / / /\ \_\   / / /\ \_\ 
    / /_/_ \/_/  \ \ \ \/___// / /_/ / // / /    / /_/_ \/_/  / / /_/ / / 
   / /____/\      \ \ \     / / /__\/ // / /    / /____/\    / / /__\/ /  
  / /\____\/  _    \ \ \   / / /_____// / /    / /\____\/   / / /_____/   
 / / /______ /_/\__/ / /  / / /   ___/ / /__  / / /______  / / /\ \ \     
/ / /_______\\ \/___/ /  / / /   /\__\/_/___\/ / /_______\/ / /  \ \ \    
\/__________/ \_____\/   \/_/    \/_________/\/__________/\/_/    \_\/    
'''
    instruction = '''
Usage:  python3 espier.py [Option]

        -h Show help info.
        -l Login into the account and get all the uid of all the dialogs.
        -b Only start the handler bot mode.
        -s Only start the surveillance mode.
        -d Deploy both the surveillance and handler bot.
'''
    print(logo)
    print(instruction)

def main():
    # Todo: command line option handle need refactory in a more reasonable way

    Options = {"-h": usage, "-l": login, "-b": operationHandler, "-s": surveillance, "-d": deploy}
    try:
        option = sys.argv[1]
    except IndexError:
        usage()
        return 0

    option = option.lower()
    if option not in Options.keys():
        print("[\033[1;31mx\033[0m] Invalid option! :/")
        usage()
        return 0
    elif option == '-h':
        usage()
    else:
        if not load():
            return 0
        try:
            Options[option]()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
