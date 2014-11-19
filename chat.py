from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        self.sendLine("What's your name?")

    def connectionLost(self, reason):
        if self.name in self.users:
            del self.users[self.name]

    def lineReceived(self, line):
        line = line.lstrip()
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if name in self.users:
            self.sendLine("Name taken, please choose another.")
            return
        self.sendLine("Welcome, %s!" % (name,))
        self.name = name
        for user, protocol in self.users.iteritems():
            protocol.transport.write("%s\r\n" % (name + " connected to chat."))
        self.users[name] = self
        self.state = "CHAT"

    def handle_CHAT(self, message):
        if message[0] == '-':
            self.handle_COMMAND(message)
        else:
            message = "<%s> %s" % (self.name, message)
            for name, protocol in self.users.iteritems():
                if protocol != self:
                    protocol.sendLine(message)

    def handle_COMMAND(self, line):
        if line == "-users":
            names = ""
            print self.users
            for name, protocol in self.users.iteritems():
                names += name + " " 
            self.sendLine(names)
        elif line.split(" ")[0] == "-kickuser":
            #del self.users[line.split(" ")[1]]
            for name, protocol in self.users.iteritems():
                if name == line.split(" ")[1]:
                    protocol.transport.loseConnection()
        else:
            self.sendLine("Unknown command!")


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)


reactor.listenTCP(8123, ChatFactory())
reactor.run()