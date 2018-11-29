AffinityForQuotes
	https://github.com/jwcain/AffinityForQuotes
	Written: July 2018 - Present
Author:
	Justin Cain
	jwcain@mtu.edu
	@AffinityForFun
	jwcain.github.io

Purpose/Theory:
	Over the summer of 2018, I was in a discord chat room discussing a joke someone posted about an AI auto generating
	Seinfeld episodes. I had the idea that it would be funny to see randomly generated messages from users in the chat
	room, so I set out to build it. Some cursory research showed that you could develop discord bots in python, so I
	set out to build it.
	
	The bot is developed in Python 3.6. It uses a runtime generated Markov chain to simulate the speech of a user. The
	last 10 thousand messages in each channel is searched for messages by the target user(s) and is use to generate the
	Markov chain.
	
Structure:
	The bot is contained in one file, in the root folder. 
	
Setup:
	The bot requires Python 3.6, and the discord packaged to be installed.
	You must register for a discord bot and save the bot-client token in a file called 'keyfile' in the same directory.
	Then you execute the python file in python. It will boot up and access any server that that bot-client ID has been 
	added to.
	
Use:
	!genquote <@mention> [@mention]*
		Output:
			A generated quote from all messages by the target user(s) within the last 10k per channel.
	!goodbot
		Output:
			Congratulates the bot for performing well. It graciously accepts.
	!badbot
		Output:
			Admonishes the bot for performing poorly. It apologizes.
	!sexybot
		Output:
			By community demand, the bot is embarrassed by your compliment.
			
Example:
	Examples can be found in the examples.pdf
	
Technical Implementation Explanation:
	The first step was to setup the discord interaction and add hooks for the appropriate commands. Following the API
	and some tutorials gave me the first simple layout of a bot.
	
	The next step was to learn how to scan messages from the user. This was done by requesting logs from discords server.
	
	In a more type strict language, the Markov Chain would take the form of a Dictionary<String,Dictionary<String, Float>>.
	The first string can be any word, the second is the word immediately following it, and the float is the calculated 
	likelihood the first word is followed by the second. This is calculated by scanning all messages and counting the rate
	at which all word-pairs appear. The start of a sentence and the end of a sentence are treated as words. Because of this,
	we can select a random word in the follow set of start-of-sentence and use that, then roll probability and use the result
	to grab a random word to follow it. This continues until the end-of-sentence word is reached.
	
	The generated sentence is then occasionally spiced up with extra punctuation, emoticons, and text modification effects
	(like bold, italics, strike through, etc.).
	
	After that, the but was functioning at the base level.
	
	After use in the community, other commands where added as I saw how users wanted to interact with the bot.
	
	I also edited the code to first send a message to the user telling them it was generating a quote, and then modifying
	that message later to put the message in place. This allowed for better tracking of message origins in a busy server.
	
	I also ran into an issue where the bot would attempt to request records of channels it did not have access to, so I
	added checking for the bot to not attempt to read or write in channels it did not have permission for. This also included
	a channel blacklist, so the user can ignore conversation in channels that are 'boring'.
	
	I very quickly did my best to desync operations of reading from the discord logs and generating messages. The speed of 
	acquiring discord logs is quite slow, so they are only grabbed once an hour. The next addition I would like to make for
	this is to add a timer to update those logs every hour instead of when a user sends a message after an hour.
	
	
	
	