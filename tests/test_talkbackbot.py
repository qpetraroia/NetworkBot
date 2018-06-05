from twisted.test import proto_helpers
from twisted.trial import unittest
from talkback.bot import TalkBackBotFactory

EXCUSE = "Nah I wanna sleep"

class FakePicker(object):
    """
    Always return the same excuse
    """
    def __init__(self, excuse):
        self.excuse = excuse 
    
    def pick(self):
        return self._excuse


class TestTalkBackBot(unittest.SynchronousTestCase):
    _channel = "#testchannel"
    _username = "tester"
    _us = 'tbb'

    def setUp(self):
        factory = TalkBackBotFactory(
            self._channel,
            self._us,
            "Bob Jones",
            FakePicker(EXCUSE),
            ['twss'],
        )
        self.bot = factory.buildProtocol(('127.0.0.1', 0))
        self.fake_transport = proto_helpers.StringTransport()
        self.bot.signedOn()
        self.bot.makeConnection(self.fake_transport)
        self.bot.joined(self._channel)
        self.fake_transport.clear()

    def test_getmsgNoTrigger(self):
        """
        Make sure an excuse isnt sent if the users text does not match the trigger
        """
        self.bot.getMessage(self._username, self._channel, "hi")
        self.assertEqual('', self.fake_transport.value())
    
    def test_getmsgWithTrigger(self):
        """
        Make sure an excuse is sent if the users text matches the trigger
        """
        self.bot.getMessage(self._username, self._channel, "twss")
        self.assertEqual(
        'GetMessage {channel} :{username}: {excuse}\r\n'.format(
            channel=self._channel, username=self._username, excuse=EXCUSE
        ),
        self.fake_transport.value())

    
    def test_getmsgAttribution(self):
        """
        If someone attributes the bot in public, they get a public response
        """
        self.bot.getMessage(self._username, self._channel, self._us + ': foo')
        self.assertEqual(
        'GetMessage {channel} :{username}: {excuse}\r\n'.format(
            channel=self._channel, username=self._username, excuse=EXCUSE
        ),
        self.fake_transport.value())

    
    def test_getmsgPrivateMessage(self):
        """
        Make sure to send the excuse to the user in a private message
        """
        self.bot.getMessage(self._username, self._us, "hi")
        self.assertEqual(
        'GetMessage {username} :{excuse}\r\n'.format(
            username=self._username, excuse=EXCUSE
        ),
        self.fake_transport.value()
    )
