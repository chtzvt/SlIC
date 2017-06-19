import json
from commandmap import CommandMap

"""
    MessageParser class.

    An instance of this class is passed to the SlackIRCController constructor.
    SlackIRCController will then use it to parse any incoming messages.

    Given a message, this class will strip everything out of it except for the
    message content. Then, it will:

        1) Check to see whether it was @mentioned in the channel,

        2) If so, parse the message and pull out the command/arguments within

        3) Compare the command sent against the list of available commands in
        config.json to see if there's anything for it to do,

        4) If the command is valid, call the appropriate method from CommandMap (which
        is defined in config.json) with the arguments recieved.

        5) Report back with the results (success/failure)

    When a message is recieved, the MessageParser class will check whether it contains any
    available command in config.json. If it does, then MessageParser calls the appropriate
    method within the CommandMap class to handle the message. Each method in this class should
    correspond with a method entry for a command in the config.json file.

    Example:
    	"commands": {
    	  "hello": {
    			"method": "sayHello",
    			"help": "says hello"
    		},
         }

    When the bot recieves the message @nickname hello, then MessageParser will call the sayHello
    method of the CommandMap class.
"""

class MessageParser(object):
    def __init__(self, config):

        if isinstance(config, dict):
            self.config = config
        else:
            with open(config, 'r') as cfg:
                self.config = json.load(cfg)

        self.command_map = CommandMap(self.config)

    """
        The parse method, which is called by the message read/eval loop
        in the SlackIRCController class.
    """
    def parse(self, message):
        if self.checkForMention(message['text']) and self.checkAuthorization(message['user']):
            # Compare the command sent against the configured list
            command = self.findCommand(message['text'])
            if command is not None:
                # If we found it, then figure out what method to call
                method = self.findMethod(command)
                # Remove the command name from the message, leaving only the arguments
                args = self.stripCommand(command, message['text'])
                # Call the appropriate method in the CommandMap class, and return
                # the response text it generates.
                return self.formatResponse(getattr(self.command_map, method)(args), message)
            else:
		return self.formatResponse('Couldn\'t find a command in: `'+ message['text'] +'`', message)

    """
        Checks for either @botID or nickname in the current message text.
    """
    def checkForMention(self, message):
        message = message.split(' ')
        return '<@'+ self.config['slack']['bot_id'] +'>' in message or self.config['slack']['bot_name'] in message

    """
        Checks message sender against authorized users
    """
    def checkAuthorization(self, user):
        authorized_users = self.config['slack']['authorized_user_ids']
        authorized_users.append(self.config['slack']['master_id'])
        return user in authorized_users

    """
        Removes any blacklisted characters from the message.
    """
    def stripCharacters(self, text):
        for char in self.config['character_blacklist']:
            text = text.replace(char, '')
        return text

    """
        Strips the command name from the message, which leaves us with the arguments to pass.
    """
    def stripCommand(self, command, text):
        text = text[text.find(command)+len(command)+1:] # Strip first occurrence of command name
        return text

    """
        The first string after our bot's nick in a message is the name of the command.
        So, we'll take that string and compare it against the configured list of valid
        commands.
    """
    def findCommand(self, text):
        text = text.split(' ')
        commands = list()
        for key in self.config['commands']:
            commands.append(key)
        for word in text:
            if word in commands:
                return word
        return None

    """
        If a command was found, then we'll need to know what method to call
        in the CommandMap class. Thankfully, this is defined in the config,
        so it's easy to look up.
    """
    def findMethod(self, text):
        text = text.split(' ')
        for word in text:
            if self.findCommand(word) is not None:
                return self.config['commands'][word]['method']
        return None

    def formatResponse(self, text, message):
        return {
           "channel": self.config['slack']['channel'],
           "text": text,
           "parent": message['thread_ts'] if 'thread_ts' in message else message['ts'],
           "reply_broadcast": None
        }
