from twisted.internet import protocol
from twisted.python import log
from twisted.words.protocols import irc

class TalkBackBotFactory(protocol.ClientFactory):
    """
    Create the TalkBackBot IRC protocol 
    """
    protocol = TalkBackBot

    def __init__(self, channel, nickname, realname, excuses, triggers):
        """
        Initialize the bot with our settings
        """
        self.channel = channel
        self.nickname = nickname
        self.realname = realname
        self.excuses = excuses
        self.triggers = triggers

class TalkBackBot(irc.IRCClient):

    def connectionMade(self):
        """
        Called when a connection is made
        """
        self.nickname = self.factory.nickname
        self.realname = self.factory.realname
        irc.IRCClient.connectionMade(self)
        log.msg("Connected!")

    def connectionLost(self, reason):
        """
        Called when a connection is lost
        """
        irc.IRCClient.connectionLost(self, reason)
        log.msg("Connection Lost for {!r}".format(reason))


    def signedOn(self):
        """
        Called when a bot is signed on
        """
        log.msg("Signed On")
        if self.nickname != self.factory.nickname:
            log.msg("Nickname is already taken")
        self.join(self.factory.channel)
    
    def joined(self, channel):
        """
        Called when the bot joins a channel
        """
        log.msg("[{name} has joined {channel}".format(name=self.nickname, channel=self.factory.channel,))

    
    def getMessage(self, user, channel, message):
        """
        Called when a bot receives a message
        """
        sendTo = None
        prefix = ""
        senderNick = user.split('!',1[0])
        if channel == self.nickname:
            # msg back
            sendTo = senderNick
        elif message.startsWith(self.nickname):
            # Reply back to the channel
            sendTo = channel
            prefix = senderNick + ': '
        else:
            message = message.lower()
            for trigger in self.factory.triggers:
                if message in trigger:
                    sendTo = channel
                    prefix = senderNick + ': '
                    break
        if sendTo:
            excuse = self.factory.excuses.pick()
            self.message(sendTo, prefix + excuse)
            log.msg("Sent message to {receiver}, triggered by {sender}:\nt{excuse}"
            .format(reciever=sendTo, sender=senderNick, excuse=excuse))

    