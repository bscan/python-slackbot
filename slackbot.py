import time
import traceback
from collections import namedtuple
from slackclient import SlackClient

""" This code originally forked from https://github.com/slackhq/python-rtmbot
As of 2016-04-10, that repo hasn't been actively maintained in about a year.
Primary reasons for forking:
UTF-8 support!
Automatic reconnection
Simplified bot architecture: bots are functions instead of plugins
Move some message handling, such as "speaking to me" check into SlackBot
"""


Message = namedtuple('Message', ['channel', 'text'])


class SlackBot(object):
    def __init__(self, token, reply_func, only_speaking_to_me=True):
        self.last_ping = 0
        self.token = token
        self.reply_func = reply_func
        self.slack_client = None
        self.user_id = None
        self.only_speaking_to_me = only_speaking_to_me

    def _connect(self):
        self.slack_client = SlackClient(self.token)
        self.user_id = self.slack_client.api_call('auth.test')['user_id']
        self.slack_client.rtm_connect()
        time.sleep(1)
        self.slack_client.rtm_read()

    def start(self):
        while True:
            self._connect()
            try:
                while True:
                    outbox = []
                    for event in self.slack_client.rtm_read():
                        # print event
                        outbox += self._process_event(event)
                    self._send_messages(outbox)
                    self._autoping()
                    time.sleep(0.1)
            except Exception as e:
                traceback.print_exc()
            time.sleep(60)  # What happened?; try to reconnect
                
    def _autoping(self):
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def _process_event(self, event):
        channel = event.get('channel')
        mtext = None
        callout = "<@{}>".format(self.user_id)

        if event.get('type') == 'message' and \
                channel and event.get('text') and \
                event.get('user', self.user_id) != self.user_id:
            if channel.startswith("D") or callout in event['text']:
                event['speaking_to_me'] = True
            else:
                event['speaking_to_me'] = False
                
            event['username'] = self.slack_client.server.users.find(event.get('user')).name
            # Turn "@your_bot: a bunch of words" into "a bunch of words"
            event['text_query'] = event['text'].replace(callout + ':', ' ').replace(callout, ' ')
            
            if not self.only_speaking_to_me or event['speaking_to_me']:
                mtext = self.reply_func(self.slack_client, event)

        if mtext:
            return [Message(channel=channel, text=mtext)]
        else:
            return []

    def _send_messages(self, outbox):
        limiter = False
        for message in outbox:
            channel_obj = self.slack_client.server.channels.find(message.channel)
            if channel_obj is not None and message.text:
                if limiter:
                    time.sleep(1)
                limiter = True
                channel_obj.send_message(u"{}".format(message.text))
                print u"Sent: " + message.text + u"  To: " + channel_obj.name
