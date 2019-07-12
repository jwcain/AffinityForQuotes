# AffinityForQuotes
Written: July 2018 - Present
## Author
- Justin Cain
- jwcain@mtu.edu
- @AffinityForFun
- jwcain.github.io/Portfolio

## Process
Over the summer of 2018, I was in a discord chat room discussing an AI capable of generating Seinfeld episodes. I then thought it would be funny to see randomly generated messages from users in the chat room, so I set out to build it.

I was familiar with AI in Python due to a college course I took and, fortunately, the Python API for Discord is quite robust, so I was able to focus my development time working on the AI. 

After weighing a few different options, I decided a Markov Chain had the highest power-to-cost ratio. I construct the Markov Chain in two parts:

(IMAGE MISSING)

The first part processes chat history to develop three pieces of data: 1) The frequency of word-pair appearance (pairingCount), 2) the frequency a word appears (wordCount), and 3) maintains a dictionary that maps a word to a list of words that can follow it (mapping).

(IMAGE MISSING)

The second part calculates the transition probabilities between words. For example, the word-pair ‘the‘ and ‘time’ appears once in this paragraph and the word ‘the’ appears 6 times, so we assume that ‘time’ follows ‘the’ 16.6% of the time.

(IMAGE MISSING)

Out of the data, an implicit Markov Chain emerges. From a randomly selected starting word, I add words using the word-pair probabilities calculated earlier. This continues until it reaches the end-of-sentence mark and a quote is complete.
	
## Structure
The bot is contained in one file, in the root folder. 
	
## Setup
The bot requires Python 3.6, and the discord packaged to be installed. You must register for a discord bot and save the bot-client token in a file called 'keyfile' in the same directory. Then you execute the python file in python. It will boot up and access any server that that bot-client ID has been added to.
	
## Use
```
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
```
			
## Example
(IMAGE MISSING)
(IMAGE MISSING)
(IMAGE MISSING)	
	
