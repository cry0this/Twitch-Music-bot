import socket, ssl, time

class IRCClient:
  tcp_sock = 0
  ssl_sock = 0
  
  config = {
    "host" : "",
    "port" : "",
    "server" : "tmi.twitch.tv",
    "nick" : "",
    "password" : "",
    "channel" : ""
  }

  def __init__(self):
    pass
  
  def ssl_send(self, message):
    self.ssl_sock.write(message.encode() + b'\r\n')
    print(message)

  def connect(self, host, port):
    self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.ssl_sock = ssl.wrap_socket(self.tcp_sock)
    self.ssl_sock.settimeout(3)
    self.ssl_sock.connect((host, port))
    self.config["host"] = host
    self.config["port"] = port

  def disconnect(self):
    self.ssl_send('QUIT')
    self.ssl_sock.close()

  def login(self, nick, password):
    self.ssl_send('PASS {}'.format(password))
    self.ssl_send('NICK {}'.format(nick))
    self.config["nick"] = nick
    self.config["password"] = password

  def joinChannel(self, channel):
    self.ssl_send('JOIN #{}'.format(channel))
    self.config["channel"] = channel

  def sendMessage(self, message):
    self.ssl_send('PRIVMSG #{} :{}'.format(self.config["channel"], message))

  def recieveData(self):
    try:
      data = self.ssl_sock.read().decode('utf-8')
    except:
      data = ""
    if (data.find('PING :' + self.config["server"]) != -1):
      self.ssl_send('PONG :' + self.config["server"])
      print(data)
      return ""
    else:
      if (data != ""):
        print(data)
      return data

  def parseData(self, data):
    data = data.split(' ')
    if (data[1] == 'PRIVMSG' and data[2] == '#' + self.config["channel"]):
      nick = data[0].split('!')
      nick = nick[0][1:]
      message = ""
      for i in range(3, len(data)):
        message += data[i]
        message += ' '
      return ((nick, message[1:].rstrip()))
    return (("", ""))