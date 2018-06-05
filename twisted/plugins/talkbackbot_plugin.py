from ConfigParser import ConfigParser
from twisted.application.service import IServiceMaker, Service
from twisted.internet.endpoints import clientFromString
from twisted.plugin import IPlugin
from twisted.python import usage, log
from zope.interface import implementer
from talkback.bot import TalkBackBotFactory
from talkback.excuse_picker import ExcusePicker

class Options(usage.Options):
    optParameters = [
        ['config', 'c', 'settings.ini', 'Configuration file.'],
    ]


class TalkBackBotService(Service):
    _bot = None

    def __init__(self, endpoint, channel, nickname, realname, excusesFilename, triggers):
        self._endpoint = endpoint
        self._channel = channel
        self._nickname = nickname
        self._realname = realname
        self._excusesFilename = excusesFilename
        self._triggers = triggers

    
    def startService(self):
        """
        Construct a client and connect to the server
        """
        from twisted.internet import reactor

        def connected(bot):
            self._bot = bot
        
        def failure(err):
            log.err(err, _why = "Could not connect to the server")
            reactor.stop()
        
        excuses = ExcusePicker(self._excusesFilename):
        client = clientFromString(reactor, self._endpoint)
        factory = TalkBackBotFactory(
            self._channel,
            self._nickname,
            self._realname,
            excuses,
            self._triggers,
            )

        return client.connect(factory).addCallbacks(connected, failure)


    def stopService(self):
        """
        Disconnect from the server
        """
        if self._bot and self._bot.transport.connected:
            self._bot.transport.loseConnection()

@implementer(IServiceMaker, IPlugin)
class BotServiceMaker(object):
    tapname = "twsrs"
    description = "IRC bot that provides excuses to get out of plans you dont want to attend"
    options = Options

    def makeService(self, options):
        """
        Construct the talk back service
        """
        config = ConfigParser()
        config.read([options['config']])
        triggers = [
            triggers.strip()
            for trigger
            in config.get('talkback', 'triggers',).split('\n')
            if trigger.strip()
        ]

        return TalkBackBotService(
        endpoint=config.get('irc', 'endpoint'),
        channel=config.get('irc', 'channel'),
        nickname=config.get('irc', 'nickname'),
        realname=config.get('irc', 'realname'),
        excusesFilename=config.get('talkback', 'excusesFilename'),
        triggers=triggers,
    )





serviceMaker = BotServiceMaker()