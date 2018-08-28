import json, urllib.request, urllib.parse, os, time, pafy
from IrcClient import IRCClient
from Player import Player

class MusicBot:
  def __init__(self):
    self.config = {}
    self.running = True
    self.ircClient = IRCClient()
    self.player = Player()
    self.currentTitle = ""
  
  def readConfig(self):
    file = open("auth.json", 'r')
    self.config = json.load(file)
    file.close()

  def connect(self):
    self.ircClient.connect('irc.chat.twitch.tv', 6697)
    self.ircClient.login(self.config["login"], self.config["token"])
    self.ircClient.joinChannel(self.config["channel"])
    self.ircClient.sendMessage('Python bot is connected. Use !help for help')

  def isRunning(self):
    return self.running

  def update(self):
    data = self.ircClient.recieveData()
    if (data != ""):
      data = self.ircClient.parseData(data)
      if (data != ("","")):
        if (data[1][0] == '!' and data[0] != self.config["login"]):
          self.executeCmd(data[1])
    self.player.update()
    if (self.currentTitle != self.player.getTitle()):
      self.currentTitle = self.player.getTitle()
      self.ircClient.sendMessage("Playing: " + self.currentTitle)

  def executeCmd(self, cmd):
    cmd = cmd.split(' ')
    command = cmd[0]
    message = ""
    for i in range(1, len(cmd)):
      message += cmd[i]
      message += ' '

    if (command == '!print'):
      self.ircClient.sendMessage(message)

    elif (command == '!exit'):
      self.exit()

    elif (command == '!add'):
      answer = self.getURL(message)
      try:
        if (answer[0] == "youtube#video"):
          video = pafy.new(answer[1])
          self.ircClient.sendMessage("Added: " + video.title)
          self.player.add((video.title, video.getbest().url))
        elif (answer[0] == "youtube#playlist"):
          try:
            playlist = pafy.get_playlist(answer[1])
            self.ircClient.sendMessage("Added playlist: " + playlist['title'])
            for i in range(0, len(playlist['items'])):
              buf = playlist['items'][i]['pafy']
              self.player.add((buf.title, buf.getbest().url))
          except:
            self.ircClient.sendMessage("Ooops, some songs in playlist are blocked. Sorry.")
      except:
        self.ircClient.sendMessage("Video not found :(")

    elif (command == '!addurl'):
      if (message.find('list=') != -1):
        message = message[:len(message)-1]
        try:
          playlist = pafy.get_playlist(message)
          self.ircClient.sendMessage("Added playlist: " + playlist['title'])
          for i in range(0, len(playlist['items'])):
            buf = playlist['items'][i]['pafy']
            self.player.add((buf.title, buf.getbest().url))
        except:
          self.ircClient.sendMessage("Ooops, some songs in playlist are blocked. Sorry.")
      elif (message.find('watch?v=') != -1):
        message = message[:len(message)-1]
        video = pafy.new(message)
        self.ircClient.sendMessage("Added: " + video.title)
        self.player.add((video.title, video.getbest().url))
      else:
        self.ircClient.sendMessage("Invalid url!")

    elif (command == '!playnow'):
      answer = self.getURL(message)
      try:
        if (answer[0] == "youtube#video"):
          video = pafy.new(answer[1])
          self.player.playNow((video.title, video.getbest().url))
        elif (answer[0] == "youtube#playlist"):
          self.ircClient.sendMessage("Playlist is detected. Please, put single video")
      except:
        self.ircClient.sendMessage("Video not found :(")

    elif (command == '!playurlnow'):
      if (message.find('list=') != -1):
        self.ircClient.sendMessage("Playlist is detected. Please, put single video")
      elif (message.find('watch?v=') != -1):
        message = message[:len(message)-1]
        video = pafy.new(message)
        self.player.playNow((video.title, video.getbest().url))
      
      else:
        self.ircClient.sendMessage("Invalid url!")

    elif (command == '!pause'):
      self.ircClient.sendMessage('Paused.')
      self.player.pause()

    elif (command == '!play'):
      self.ircClient.sendMessage('Playing.')
      self.player.play()

    elif (command == '!p'):
      self.ircClient.sendMessage('Play/Pause toggled.')
      self.player.toggle()

    elif (command == '!stop'):
      self.ircClient.sendMessage('Stopped.')
      self.player.stop()

    elif (command == '!next'):
      self.player.nextSong()

    elif (command == '!prev'):
      self.player.prevSong()

    elif (command == '!get'):
      self.ircClient.sendMessage("Current track: " + self.player.getTitle())

    elif (command == '!whatnext'):
      self.ircClient.sendMessage("Next track: " + self.player.getNext()[0])

    elif (command == '!vol'):
      self.player.setVolume(message)

    elif (command == '!fullscr'):
      self.player.fullscreen()

    elif (command == '!help'):
      helpmsg = []
      helpmsg.append("MusicBot usage: ")
      helpmsg[0] += "!add [phrase] -- search song by [phrase] and add to playlist; " 
      helpmsg[0] += "!addurl [url] -- add [url] to playlist; " 
      helpmsg[0] += "!playnow [phrase] -- search song by [phrase] and play it now; " 
      helpmsg[0] += "!playurlnow [url] -- play [url] now; " 
      
      helpmsg.append("!pause -- pause music; ")
      helpmsg[1] += "!play -- continue music; " 
      helpmsg[1] += "!p -- toggle play/pause; "
      helpmsg[1] += "!next -- next track; "
      helpmsg[1] += "!prev -- previous track; "
      
      helpmsg.append("!get -- get title of current track; ")
      helpmsg[2] += "!whatnext -- get title of next track; "
      helpmsg[2] += "!vol [value] -- add or subtract [value] of volume; "
      helpmsg[2] += "!fullscr -- toggle fullscreen; "
      helpmsg[2] += "!print [message] -- print the [message]; " 
      
      helpmsg.append("!exit -- close bot; ")
      helpmsg[3] += "!help -- print this help"

      for i in range(0, len(helpmsg)):
        self.ircClient.sendMessage(helpmsg[i])
        time.sleep(3)
  
  def getURL(self, searchWord):
    url = 'https://www.googleapis.com/youtube/v3/search?'
    query = {
      'maxResults' : '1',
      'part' : 'snippet',
      'key' : self.config['apiKey'],
      'q' : searchWord
    }
    request = url + urllib.parse.urlencode(query)
    print(request)
    response = urllib.request.urlopen(request)
    json_encoded = json.loads(response.read())
    if (json_encoded["pageInfo"]["totalResults"] > 0):
      if (json_encoded["items"][0]["id"]["kind"] == "youtube#video"):
        videoId = json_encoded["items"][0]["id"]["videoId"]
        url = "https://www.youtube.com/watch?v=" + videoId
        return ( ("youtube#video", url) )
      if (json_encoded["items"][0]["id"]["kind"] == "youtube#playlist"):
        playlistId = json_encoded["items"][0]["id"]["playlistId"]
        url = "https://www.youtube.com/playlist?list=" + playlistId
        return ( ("youtube#playlist", url) )
    else:
      return -1

  def getTitle(self, videoUrl):
    video = pafy.new(videoUrl)
    return video.title

  def exit(self):
    self.ircClient.sendMessage('PyBot is disconnected.')
    self.ircClient.disconnect()
    self.running = False
