# Work with Python 3.6
import discord
from discord import game
import asyncio
from collections import defaultdict
import random
import time
TOKEN = ''

client = discord.Client()

storedMessages = defaultdict(lambda: [])
storedTimes = defaultdict(lambda: -10)
hourInSeconds = 3600

async def Fetch_Data(message, botMember):
    cTime = time.time()
    channelBlackList = ['features', 'bugs', 'socialmedia', 'cardcondition']
    if abs(storedTimes[message.channel.server.id] - cTime) > hourInSeconds:
        print('gathering new data')
        for channel in message.channel.server.channels:
            print(channel.name)
            if channel.name in channelBlackList:
                continue
            if channel.type != discord.ChannelType.text or channel.permissions_for(botMember).read_messages == False:
                continue
            async for logMessage in client.logs_from(channel, 10000):
                storedMessages[message.channel.server.id].append(logMessage)
        storedTimes[message.channel.server.id] = cTime
        print('Data Gathered')
    return storedMessages[message.channel.server.id]
   
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
        
    if message.content.startswith('!genquote help'):
        await client.send_message(message.channel, 'Type `!genquote @target` (@mention someone). Hit enter and let it go!')
    elif message.content.startswith('!genquote info'):
        await client.send_message(message.channel, 'I read recent chat history and generate a quote based on everything someone has said!')
    elif message.content.startswith('!goodbot'):
        tName = ''
        if message.author.nick is None:
            tName = message.author.name
        else:
            tName = message.author.nick
        await client.send_message(message.channel, 'Thank you, ' + tName + '!')
    elif message.content.startswith('!badbot'):
        tName = ''
        if message.author.nick is None:
            tName = message.author.name
        else:
            tName = message.author.nick
        await client.send_message(message.channel, 'I\'m sorry, ' + tName + '. I\'ll try better next time :(.')
    elif message.content.startswith('!sexybot'):
        tName = ''
        if message.author.nick is None:
            tName = message.author.name
        else:
            tName = message.author.nick
        await client.send_message(message.channel, 'oWo, ' + tName + '-chan.')
    elif message.content.startswith('!genquote') or message.content.startswith('!quotegen'):
        print(client.user.id)
        botMember = message.channel.server.get_member(client.user.id)
        if message.channel.permissions_for(botMember).send_messages == False:
            return
        await client.change_presence(game=discord.Game(name='Reading Data'))
        print('Reading Data')
        userTarget = message.content[10:]
        waitingMessage = await client.send_message(message.channel, 'Gathering data...')
        rawMessages = await Fetch_Data(message, botMember)
        await client.edit_message(waitingMessage, 'Generating a quote...')
        foundMessages = []
        persons = []
        for logMessage in rawMessages:
            if str(logMessage.author.mention) in userTarget and logMessage.content.startswith('!') == False:
                tName = ''
                if logMessage.author is discord.User or logMessage.author.nick is None:
                    tName = logMessage.author.name
                else:
                    tName = logMessage.author.nick
                if tName not in persons:
                    persons.append(tName)
                foundMessages.append(logMessage.content)
        if len(foundMessages) == 0:
            await client.edit_message(waitingMessage, message.author.name + ', that person hasn\'t said anything recently! They need to talk more.')
            print('Early exit')
            await client.change_presence(game=discord.Game(name='Idle'))
            return
        
        await client.change_presence(game=discord.Game(name='Generating Quote'))
        
        print('Generating Quote')
        
        wordCount = defaultdict(lambda: 0)
        pairingCount = defaultdict(lambda: 0)
        mapping = defaultdict(lambda: [])
        blackList = ['www.', '.com', 'http', '@']
        for fMessage in foundMessages:
            lastWord = ''
            wordCount[''] = wordCount[''] + 1
            for word in fMessage.split():
                continueflag = False
                for blackItem in blackList:
                    if blackItem in word:
                        continueflag = True
                if continueflag == True:
                    continue
                mapping[lastWord].append(word)
                wordCount[word] = wordCount[word] + 1
                pairingCount[(lastWord, word)] = pairingCount[(lastWord, word)] + 1
                lastWord = word
            mapping[lastWord].append('')
            pairingCount[(lastWord, '')] = pairingCount[(lastWord, '')] + 1
        
        probabilityForPairs = defaultdict(lambda: float(0))
        for keyTuple in pairingCount:
            #print('[' + keyTuple[0] + ' | ' + keyTuple[1] + '] ' + str(pairingCount[keyTuple]) + ' ' + str(wordCount[keyTuple[0]]))
            probabilityForPairs[keyTuple] = pairingCount[keyTuple] / wordCount[keyTuple[0]]
            if keyTuple[1] == '':
                probabilityForPairs[keyTuple] = probabilityForPairs[keyTuple] * 0.6
                
        print('Tables Generated')
        punctuation = ['?','?','?','?', ',', ',', ',',',',',','.', '!','!','!', '.', '.', '.', '?', '?', '.', '!', '.', '.', '.', '?', '?!?!?!?!', '...', '?', '.', '!', '.', '.', '.', '?', ' :heart:']
        quote = ''
        numGenerations = random.randint(1,4)
        protectionIter = 0
        while protectionIter < 20 and (numGenerations > 0 or quote == ''):
            protectionIter = protectionIter + 1
            subQuote = ''
            numGenerations = numGenerations - 1
            doneflag = False
            currentWord = random.choice(mapping[''])
            while currentWord != '' and doneflag == False:
                if 0.99 < random.random():
                    wordModifiers = ['*','**','***','__', '~~']
                    wordModifier = random.choice(wordModifiers)
                    subQuote = subQuote + ' ' + wordModifier + currentWord + wordModifier
                else:
                    subQuote = subQuote + ' ' + currentWord
                randomNum = random.random()
                testingWord = ''
                while randomNum > 0:
                    
                    #print('['+currentWord + '] ' + str(mapping[currentWord]))
                    testingWord = random.choice(mapping[currentWord])
                    randomNum -= pairingCount[(currentWord, testingWord)]
                    if testingWord == '':
                        if 0.99 < random.random():
                            testingWord = random.choice(mapping[''])
                        doneflag = True
                        break
                    currentWord = testingWord
            hasPunc = False
            for p in punctuation:
                if p in subQuote:
                    hasPunc = True
            quote = quote + subQuote      
            if hasPunc == False and len(subQuote) > 0:
                quote = quote + random.choice(punctuation)

                

        if client.user.mention == userTarget:
            quote = '`S-Senpai, I shouldn\'t quote myself... oWo` \n' + quote
        else:
            mentionString = ''
            for person in persons:
                mentionString = mentionString + person + ', '
            if len(persons) == 1:
                quote = '`' +  mentionString +'has totally said:` \n' + quote
            else:
                quote = '`' + mentionString  +'have totally talked about:` \n' + quote
        
        print('sending quote')
        await client.edit_message(waitingMessage,quote + '\n')
        await client.change_presence(game=discord.Game(name='Idle'))


@client.event
async def on_ready():
    await client.login(TOKEN)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='Idle'))
file = open("keyfile", "r")
TOKEN = file.read()
client.run(TOKEN)