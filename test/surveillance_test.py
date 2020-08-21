#/usr/bin/env python3

from telethon import TelegramClient, events, utils
from telethon.extensions.markdown import parse
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.channels import GetChannelsRequest
from telethon.tl.functions.users import GetUsersRequest
from telethon.tl.types import *

from base64 import b64encode
from random import randint

import threading, json, sys, re, asyncio, time

client = ''
info = {}
admin = []
keywords = []
userlist = []
grouplist = []
speciallist = []
proxies = []
pmid = 1
first_run = True

def login():
    global client, info
    try:
        client = TelegramClient('anon', info['api_id'], info['api_hash'])
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
    ## Get all the channel, groups, chats id you have.
    ## To do: display those information at run time, like this:
    ## 1) archlinux-cn (2137098721)
    ## 2) manjarocn (987213681)
    ##    ...
    ## ?) name (id)

    global client

    # You can print all the dialogs/conversations that you are part of:
    #async for dialog in client.iter_dialogs():
    #   print(dialog.name, 'has ID', dialog.id)

    dialogs = await client.get_dialogs(limit=None)

    padding = 10
    result = "| ID           | Chat Name\n|==============|============================\n"
    for dialog in dialogs:
        chatid = str(dialog.entity.id)
        # separator = (padding - len(chatid)) * ' ' + ' | '
        item = "| {:12} | {}\r\n"
        result += item.format(chatid, str(dialog.name))
        # result += str(dialog.name) + ' | ' + str(dialog.entity.id) + '\r\n'
        # result += ' ' + chatid + separator + str(dialog.name) + '\r\n'
    with open("list.txt", "w") as f:
        f.write(result)
    print('[' + colour('+', 'green') +'] Information saved into list.txt')

def load():
    ## Load Basic information (api_id, api_hash, watchlist, etc) from data.json
    ## Keep information in info dict
    
    global info, keywords, grouplist, userlist, speciallist, admin
    data_file = "resources/data_test.json"
    keyword_file = "resources/keyword_test.txt"
    try:
        with open(data_file, 'r') as data:
            Data = data.read()
        info = json.loads(Data)

        print(info['admin'])
        print(info['api_id'])
        print(info['api_hash'])
        print(info['group_watchlist'])
        print(type(info['user_watchlist']))
        print(info['recv_channel'][0])

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
    # client = TelegramClient('espier', info['api_id'], info['api_hash'], loop=loop)
    client = TelegramClient('anon', info['api_id'], info['api_hash'])
    receiver = PeerChannel(info['recv_channel'][0])
    receiverch = info['recv_channel'][0]

    # Set Offline to keep operation covert.
    #await client(UpdateStatusRequest(offline=True))
    # If you like to transfer to more places, add accordingly


    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        global keyword, userlist, grouplist, speciallist

        def printer(event):
            print('==================== Income new message ====================')
            # print('time: ' + time.time())
            print('\033[1;32mSender:\033[0m    ' + str(sender))
            print('\033[1;31mReceiver:\033[0m  ' + str(to_id))
            if event.raw_text == '':
                print('\033[1;37mMessage:\033[0m   message does not contain text')
            else:
                #print('\033[1;37mMessage:\033[0m   ' + event.raw_text)
                print('\033[1;37mMessage:\033[0m   ' + str(event.raw_text).replace('\n', '\n           '))
            print('============================================================\n ')

        def logger(event):
            if event.raw_text == '':
                print('message does not contain text')
            else:
                print(event.raw_text)

        def sendMessage(compose, mtype):
            # user = """**Sender Name:** {1}\n**Sender ID:** [{0}](tg://user?id={0})\n""".format(compose[0][0], compose[0][1])
            # group = """**Group Name:** {1}\n**Group ID:** {0}\n""".format(compose[1][0], compose[1][1])

            user = """`User: {1} [`[{0}](tg://user?id={0})`]`""".format(compose[0][0], compose[0][1])
            group = """`Group: {1} [`{0}`]`\n""".format(compose[1][0], compose[1][1])

            result = ''

            if mtype == 'group':
                # Group Listener
                result = user
            elif mtype == 'user':
                # User Listener
                result = group
            else:
                result = user + '\r\n' + group

            return result

        async def compose(sender, to_id):
            user = await client(GetUsersRequest([sender]))
            user = user[0]
            name = ''
            if user.first_name is not None:
                name = name + user.first_name
            if user.last_name is not None:
                name = name + ' ' + user.last_name
            u = [user.id, name]
            group = await client(GetChannelsRequest([to_id]))
            group = group.chats[0]
            g = [group.id, group.title]
            return [u, g]

        def keywordScan(text):
            global keywords
            if text == None:
                return False
            try:
                for word in keywords:
                    if word in text:
                        return word
            except Exception as e:
                print(e)
            return False

        # if first_run:
        #   await client(UpdateStatusRequest(offline=True))
        #   await client.catch_up()
        #   remind = await client.send_message(receiver, 'Surveillance running!')
        #   await client.pin_message(receiver, remind, notify=True)
        #   first_run = False

        if 'hello' in event.raw_text:
            await event.reply('hi!')

        # print(client)
        await client.send_message('me', 'Hello, myself!')
        
        to_id = event.message.to_id
        sender = event.input_sender
        content = event.message.message

        print(to_id, sender, content)

        # Debug
        # printer(event)
        # logger(event)
        # print(event.message)

        """
        if int(sender.user_id) in userlist:
            printer(event)
            print(event.message)
            # logger(event)
        """

        # user = await client.get_entity(senderID)
        # print(utils.get_display_name(user))
        # group = await client.get_entity(chatID)
        # print(utils.get_display_name(group))

        # =================================================================
        # user = await client(GetUsersRequest([sender]))
        # user = user[0]
        # name = ''
        # if user.first_name is not None:
        #   name = name + user.first_name
        # if user.last_name is not None:
        #   name = name + ' ' + user.last_name
        # u = [user.id, name]
        # group = await client(GetChannelsRequest([to_id]))
        # group = group.chats[0]
        # g = [group.id, group.title]
        # composed = [u, g]
        composed = await compose(sender, to_id)
        # =================================================================

        check = keywordScan(content)
        if check:
            hint = "**Keyword:**  {}".format(check)
            message = sendMessage(composed, mtype='all')
            message = hint + "\n" + message
            await client.send_message(receiver, message, parse_mode='md')
            fwd = await client(ForwardMessagesRequest(from_peer=to_id, id=[event.message.id], to_peer=receiver))
            # message = sendMessage(composed, mtype='all')
            # await client.send_message(receiver, message, parse_mode='md')

        test = str(to_id)
        chat_id = re.search('\d+', test).group()

        ## Monitoring Telegram Login Code Message.
        ## senderID = event.message.from_id
        senderID = sender.user_id
        content = str(event.raw_text)

        if 'login code' in content.lower():
            print("----- Login code! -----")
            try:
                lCode = str(re.search("\d+", content).group())
                eCode = b64encode(lCode.encode()).decode()
                eCode = "`{}`".format(eCode)
                content = content.replace("login code:", "**Login code:**")
                content = content.replace(lCode, eCode)
                ding = await client.send_message(receiver, content, parse_mode='md', silent=False)
                #await client.pin_message(receiver, ding, notify=True)
            except Exception as err:
                print(err)
        
        # Group listener
        # Add more IF condition if you want to listen more event.
        # if to_id.channel_id in grouplist and event.out is False:
        #print(int(chat_id), sender.user_id)
        # print(grouplist)
        # print(to_id.channel_id)
        # print(event.input_sender.user_id)
        if int(to_id.channel_id) in grouplist and event.out is False:
            print("group")
            # FWD message to channel
            """
            fwd = await client(ForwardMessagesRequest(
                from_peer=event.message.to_id,  # who sent these messages?
                id=[event.message.id],  # which are the messages?
                to_peer=receiver  # who are we forwarding them to?
            ))
            """
            print(receiver, receiverch, event.message.id, event.message.to_id)
            # fwd = await client.forward_messages(entity=receiverch, messages=[event.message.id], from_peer=event.message.to_id)
            # print(fwd)
            message = sendMessage(composed, mtype='all')
            print(message)
            await client.send_message(receiver, message, parse_mode='md')

        elif int(event.input_sender.user_id) in userlist:
            print("user")
            fwd = await client(ForwardMessagesRequest(
                from_peer=event.message.to_id,  # who sent these messages?
                id=[event.message.id],  # which are the messages?
                to_peer=receiver  # who are we forwarding them to?
            ))
            message = sendMessage(composed, mtype='all')
            await client.send_message(receiver, message, parse_mode='md')

        target_id = int(event.input_sender.user_id)
        for i in speciallist:
            if str(target_id) in i:
                special_channel = int(i.split(":")[1])
                print("target")
                fwd = await client(ForwardMessagesRequest(
                    from_peer=event.message.to_id,  # who sent these messages?
                    id=[event.message.id],  # which are the messages?
                    to_peer=special_channel  # who are we forwarding them to?
                ))
                break
    
    print('[' + colour('+', 'green') +'] Running surveillance operation!')
    """
    with client:
        #client.loop.run_forever()
        client.run_until_disconnected()
    """

    @client.on(events.NewMessage(outgoing=True, pattern='!ping'))
    async def handler(event):
        # Say "!pong" whenever you send "!ping", then delete both messages
        m = await event.respond('!pong')
        await asyncio.sleep(5)
        await client.delete_messages(event.chat_id, [event.id, m.id])

    client.start()
    client.run_until_disconnected()

load()
# login()
surveillance()
