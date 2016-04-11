python-slackbot
=============
A Slack bot written in python that allows for two way communication.

Originally forked from https://github.com/slackhq/python-rtmbot, python-slackbot is the simplest way to build a Bot user for Slack. Unlike python-rtmbot, this repo also has full support for UTF-8 encoding.



Example Arnold Bot
-------
from slackbot import SlackBot
import random

def arnold(event):
    # Ignore what the user said, simply generate random arnold quote
    quotes = [u"Milk is for babies. When you grow up you have to drink beer.",
              u"Start wide, expand further, and never look back.",
              u"If it bleeds, we can kill it."]
    return random.choice(quotes)


token = 'SLACK TOKEN HERE'
my_bot = SlackBot(token, arnold)
my_bot.start()



Dependencies
----------
* websocket-client https://pypi.python.org/pypi/websocket-client/
* python-slackclient https://github.com/slackhq/python-slackclient