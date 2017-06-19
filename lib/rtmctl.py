from slackclient import SlackClient
import time, json

class SlackBotController(object):
    def __init__(self, **kwargs):

        if 'config' in kwargs:
            if isinstance(kwargs['config'], dict):
                self.config = kwargs['config']
            else:
                with open(kwargs['config'], 'r') as cfg:
                    self.config = json.load(cfg)

        if 'parser' in kwargs and kwargs['parser'] is not None:
            self.messageParser = kwargs['parser']
        else:
            self.messageParser = self

        self.slackAPI = SlackClient(self.config['slack']['token'])

        self.connected = False
        self.loop = False
        self.most_recent_ping = int(time.time())
        self.sentGreeting = False
        self.sendReady = False

    """
        Call this method to connect, authenticate, and start the read/eval loop
        As the name implies, this runs the bot.
    """
    def run(self):
        self.loop = self.connect()
        self.message_loop()

    """
        This will stop the loop from running.
    """
    def stop():
        self.loop = False

    def connect(self):
        while self.connected is False:
            self.connected = self.slackAPI.rtm_connect()
            time.sleep(1)
        return self.connected

    """
        Sends the given message text to the current channel.
    """
    def reply(self, msg):
        if self.sendReady:
            self.slackAPI.rtm_send_message(msg['channel'], msg['text'], msg['parent'], msg['reply_broadcast'])

    def notifyConnected(self):
        connect_msg = {
            "channel": self.config['slack']['channel'],
            "text": 'Connected.',
            "parent": None,
            "reply_broadcast": None
        }
        self.reply(connect_msg)

    def notifyError(self, message, e):
        error_msg = {
            "channel": self.config['slack']['channel'],
            "text": 'Something isn\'t right: `'+ message['text'] +'` _(got `'+ repr(e) +'`)_.',
            "parent": message['ts'],
            "reply_broadcast": None
        }
        self.reply(error_msg)

    def manageStreamHealth(self, message):
        # Sends a ping to the server every 5 seconds, to prevent
        # accidentally being marked as idle.
        curtime = int(time.time())
        if curtime > self.most_recent_ping + 5:
            self.slackAPI.server.ping()
            self.most_recent_ping = curtime

        if 'type' in message and message['type'] == 'hello':
         self.sendReady = True

    def is_message(self, message):
        return 'event_ts' not in message and 'type' in message and message['type'] == 'message'

    def message_loop(self):
        while self.loop is True:
          message = self.slackAPI.rtm_read()
          message = message[0] if len(message) > 0 else {'type': '__EMPTY__'}

          self.manageStreamHealth(message)

          if self.sentGreeting is False and self.sendReady is True:
            self.notifyConnected()
            self.sentGreeting = True

          if self.is_message(message):
              try:
                  output = self.messageParser.parse(message) if self.sendReady is True and message['type'] is not '__EMPTY__' else None
                  if output is not None:
                      self.reply(output)
              except Exception,e:
                  self.notifyError(message, e)

    """
        If no parser is supplied, the controller will simply print every message it recieves.
    """
    def parse(self, message):
	print message['text'] if 'text' in message else None
