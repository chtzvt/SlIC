# Please install the slackclient module either globally or into ./lib before running this bot
# Additionally, you should fill in the config.json with all of the appropriate keys, tokens, and IDs

import json, sys, socket, time
sys.path.insert(0, 'lib')
sys.dont_write_bytecode = True

from rtmctl import SlackBotController
from messageparser import MessageParser

with open('config.json', 'r') as cfg:
    config = json.load(cfg)

slackbot = SlackBotController(config=config, parser=MessageParser(config))

# Runs the bot and handles/retries on connection errors,
# implements an exponential backoff up to 256 seconds.
def retryLoop(func, sec):
    try:
        func()
    except Exception,e:
        sec = sec+1 if sec < 8 else 1
        print 'Connection error, retrying in '+ str(2**sec) +' seconds...'
        time.sleep(2**sec)
        retryLoop(func, sec)

retryLoop(slackbot.run, 0)
