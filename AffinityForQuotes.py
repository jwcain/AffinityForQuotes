#AffinityForQuotes
#Python 3.6 Discord Bot
#Author: Justin Cain, @AffinityForFun

import discord
from discord import game
import asyncio
from collections import defaultdict
import random
import time


client = discord.Client() #alias for discord client
messageReadAmount = 10000 #Amount of messages to read within a channel
channelBlackList = ['features', 'bugs', 'socialmedia', 'cardcondition'] #Customizable channel read blacklist
wordBlackList = ['www.', '.com', 'http', '@'] #Text that is not allowed to appear in source messages
storedMessages = defaultdict(lambda: []) #stored messages from a server
storedTimes = defaultdict(lambda: -10) #Timestamps from data read for each server
hourInSeconds = 3600 #the amount of seconds in an hour

#Fetches the data for a specific user. If the data is not up to date it will update it first.
async def Fetch_Data(message, botInstance):
    cTime = time.time() #Get the current time
    #if too much time has passed, generate a new table.
    if abs(storedTimes[message.channel.server.id] - cTime) > hourInSeconds:
        print('gathering new data')
        for channel in message.channel.server.channels:
            print(channel.name)
            #Dont read from our blacklist
            if channel.name in channelBlackList:
                continue
            #Do not attempt a read if it is a voice channel or if we do not have permission.
            if channel.type != discord.ChannelType.text or channel.permissions_for(botInstance).read_messages == False:
                continue
            #Reset the data
            #storedMessages[message.channel.server.id] = []
            #Get the log from Discord servers, with a set amount of messages
            async for logMessage in client.logs_from(channel, messageReadAmount):
                storedMessages[message.channel.server.id].append(logMessage)

        #update the time that we have read from this server
        storedTimes[message.channel.server.id] = cTime
        print('Data Gathered')
    
    #Return the stored messages for this server
    return storedMessages[message.channel.server.id]

#Gets the sender's name for a message. Attempts to use nickname first.
def GetName(message):
    #Temp value for name return
    tName = ''
    #Use the nickname if we can, otherwise use default
    if message.author is discord.User or message.author.nick is None:
        tName = message.author.name
    else:
        tName = message.author.nick
    return tName

#Generates a fake quote based on the command within the passed message
async def GenQuote(message, speak):
    #Get our instance within this message's server
    botInstance = message.channel.server.get_member(client.user.id)

    #If we do not have write permission in this channel, ignore this command
    if message.channel.permissions_for(botInstance).send_messages == False:
        return

    #change our presence to 'Reading Data'
    await client.change_presence(game=discord.Game(name='Reading Data'))

    #Update our console
    print('Reading Data')

    #Strip the message down to just the @mentions
    userTarget = message.content[10:]

    #Send a message to the server to serve as both an update to users as well as a message placeholder
    waitingMessage = await client.send_message(message.channel, 'Gathering data...')

    #Get the raw messages data for this server
    rawMessages = await Fetch_Data(message, botInstance)

    #Update our placehoder message with `Generating a quote`
    await client.edit_message(waitingMessage, 'Generating a quote...')

    #track found messages
    foundMessages = []
    #Track the names of targets we've found (so we can gather their nicknames)
    persons = []
    #Go through the raw messages
    for logMessage in rawMessages:
        #Get the @menetion text for this messages author and make sure that it is within our target mentions string. And dont read messages that are commands 
        if str(logMessage.author.mention) in userTarget and logMessage.content.startswith('!') == False:
            #get the name of the author
            tName = GetName(logMessage)
            #if we have not stored this name before, store it
            if tName not in persons:
                persons.append(tName)
            #Add this message as a valid message for the table
            foundMessages.append(logMessage.content)
    
    #If we haven't found at least one message.
    if len(foundMessages) == 0:
        #Let the user know that this isnt valid
        await client.edit_message(waitingMessage, message.author.name + ', that person hasn\'t said anything recently! They need to talk more.')
        print('Early exit by not enough messages to operate.')
        #switch back to idle
        await client.change_presence(game=discord.Game(name='Idle'))
        return
    
    #Update our status to quote generation
    await client.change_presence(game=discord.Game(name='Generating Quote'))
    #Update the console
    print('Generating Quote')
    #Count of how often a word shows up
    wordCount = defaultdict(lambda: 0)
    #count of all pairs of words (how often a word follows another)
    pairingCount = defaultdict(lambda: 0)
    #A mapping of what words follow others
    mapping = defaultdict(lambda: [])
    #loop through all found messages
    for fMessage in foundMessages:
        #Track the previous word we looked at
        lastWord = '' #Start with nothing, or start of sentence
        wordCount[''] = wordCount[''] + 1 #increase the count of nothing, or start of sentence
        #Read each word individually
        for word in fMessage.split():
            #skip this word if it on the blacklist
            continueflag = False
            for blackItem in wordBlackList:
                if blackItem in word:
                    continueflag = True
            if continueflag == True:
                continue
            #This word follows the previous word, add it to the mapping
            if word not in mapping[lastWord]:
                mapping[lastWord].append(word)
            #increase the count of this word
            wordCount[word] = wordCount[word] + 1
            #increase the count of this pair
            pairingCount[(lastWord, word)] = pairingCount[(lastWord, word)] + 1
            #set this word as the last word
            lastWord = word
        
        #Add a mapping for the last word to the end of sentence
        if '' not in mapping[lastWord]:
            mapping[lastWord].append('')
        pairingCount[(lastWord, '')] = pairingCount[(lastWord, '')] + 1
    
    #Caluclate the probability of each pair
    probabilityForPairs = defaultdict(lambda: float(0))
    for keyTuple in pairingCount:
        #Calculate how often this word follows the next
        probabilityForPairs[keyTuple] = pairingCount[keyTuple] / wordCount[keyTuple[0]]
        #Reduce the chance that we end a sentence to make it more rambly
        if keyTuple[1] == '':
            probabilityForPairs[keyTuple] = probabilityForPairs[keyTuple] * 0.6
    
    #Report that the needed information for a quote has been calculated
    print('Tables Generated')
    #A Table of randomized punctuation
    punctuation = ['?','?','?','?', ',', ',', ',',',',',','.', '!','!','!', '.', '.', '.', '?', '?', '.', '!', '.', '.', '.', '?', '?!?!?!?!', '...', '?', '.', '!', '.', '.', '.', '?', ' :heart:']
    #Start the Quote
    quote = ''
    #Calculate how many sequences we are going to add to the quote
    numGenerations = random.randint(1,4)
    #Start an iterator to prevent infinite loops
    protectionIter = 0
    while protectionIter < 50 and (numGenerations > 0 or quote == ''):
        #Increase the protection iter
        protectionIter = protectionIter + 1
        #Decreaset the number of generatiojns remaining
        numGenerations = numGenerations - 1
        #Start calculating the sub quote
        subQuote = ''
        #Track a flag for if we are done creating the sub quote
        doneflag = False
        #Get a random starting word from the ''->word mapping (start of sentence mapping)
        currentWord = random.choice(mapping[''])
        #While we have not hit an end of string or hit an early exit
        while currentWord != '' and doneflag == False:
            #Randomely check if we want to add modifiers to this word, otherwise just add it to the subquote with a space
            if 0.99 < random.random():
                wordModifiers = ['*','**','***','__', '~~']
                wordModifier = random.choice(wordModifiers)
                subQuote = subQuote + ' ' + wordModifier + currentWord + wordModifier
            else:
                subQuote = subQuote + ' ' + currentWord
            
            #Get a random number from 0-1
            randomNum = random.random()
            testingWord = ''
            while randomNum > 0:
                
                #Randomly choose words and subtract their probability until we reach 0
                testingWord = random.choice(mapping[currentWord])
                randomNum -= pairingCount[(currentWord, testingWord)]
                #Exit sequence if we have hit the end of sentence
                if testingWord == '':
                    doneflag = True
                    break
                
                currentWord = testingWord
        #Check if this sub quote already has punctuation
        hasPunc = False
        for p in punctuation:
            if p in subQuote:
                hasPunc = True
        #Add subquote
        quote = quote + subQuote
        #Add punctionation only if we do not alreay have punctuation and if we are actually adding info
        if hasPunc == False and len(subQuote) > 0:
            quote = quote + random.choice(punctuation)


    #print a custom message if we are quoting ourselves
    if client.user.mention == userTarget:
        quote = '`I shouldn\'t quote myself...`\n' + quote
    else:
        #Create a stirng using the names we gathered
        mentionString = ''
        for person in persons:
            mentionString = mentionString + person + ', '
        #Add a header to our quote depending on weather or not we have more than one target user
        if len(persons) == 1:
            quote = '`' +  mentionString +'has totally said:` \n' + quote
        else:
            quote = '`' + mentionString  +'have totally talked about:` \n' + quote
    #Update the console on our progress
    print('sending quote')
    #Update our message and our status
    await client.change_presence(game=discord.Game(name='Idle'))
    await client.edit_message(waitingMessage, quote + '\n')
    
    #if speak == True:
    #   ttsMessage = await client.send_message(message.channel, quote + '\n', tts=True)
    #   await client.delete_message(ttsMessage)


#Executes on every message sent in the server
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!genquote help'):
        await client.send_message(message.channel, 'Type `!genquote @target ...` (@mention one ore more person). Hit enter and let it go!')
    elif message.content.startswith('!genquote info'):
        await client.send_message(message.channel, 'I read recent chat history and generate a quote based on everything someone has said!')
    elif message.content.startswith('!goodbot'):
        await client.send_message(message.channel, 'Thank you, ' + GetName(message) + '!')
    elif message.content.startswith('!badbot'):
        await client.send_message(message.channel, 'I\'m sorry, ' + GetName(message) + '. I\'ll try better next time :(')
    elif message.content.startswith('!sexybot'):
        await client.send_message(message.channel, 'owo, ' + GetName(message) + '-chan.')
    elif message.content.startswith('!genquote') or message.content.startswith('!quotegen'):
        await GenQuote(message, False)
    elif message.content.startswith('!speakquote') or message.content.startswith('!quotespeak'):
        await GenQuote(message, True)


#Setup for when the bot is live
@client.event
async def on_ready():
    await client.login(TOKEN)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='Idle'))

#Initialize the bot
TOKEN = ''
file = open("keyfile", "r") #read the token from a file named keyfile
TOKEN = file.read()
client.run(TOKEN)
