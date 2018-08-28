import vlc, time

class Player:
  def __init__(self):
    self.instance = vlc.Instance()
    self.player = self.instance.media_player_new()
    self.toggled = False
    self.playlist = []
    self.current = 0
    self.volume = 100

  def update(self):
    if (not self.player.is_playing() and not self.toggled):
      if (len(self.playlist) > 0 and self.current < len(self.playlist) - 1):
        self.nextSong()
      else:
        self.player.stop()

  def play(self):
    self.player.play()
    self.toggled = False

  def pause(self):
    self.player.pause()
    self.toggled = True

  def stop(self):
    self.player.stop()
    self.toggled = True

  def nextSong(self):
    item = self.getNext()
    if (len(item) > 0):
      self.current += 1
      media = self.instance.media_new(item[1])
      self.player.set_media(media)
      self.play()
      vlc.libvlc_audio_set_volume(self.player, self.volume)
      time.sleep(5)

  def prevSong(self):
    item = self.getPrev()
    if (len(item) > 0):
      self.current -= 1
      media = self.instance.media_new(item[1])
      self.player.set_media(media)
      self.play()
      vlc.libvlc_audio_set_volume(self.player, self.volume)
      time.sleep(5)

  def add(self, item):
    if (len(self.playlist) == 0):
      self.playlist.append(item)
      media = self.instance.media_new(item[1])
      self.player.set_media(media)
      self.player.play()
      vlc.libvlc_audio_set_volume(self.player, self.volume)
      time.sleep(5)
    else:  
      self.playlist.append(item)

  def getNext(self):
    if ( (self.current + 1) < len(self.playlist) ):
      return self.playlist[self.current + 1]
    else:
      return ("", "")

  def getPrev(self):
    if ( (self.current - 1) >= 0 ):
      return self.playlist[self.current - 1]
    else:
      return ("", "")
  
  def getTitle(self):
    if(len(self.playlist) > 0):
      return self.playlist[self.current][0]
    else:
      return ""

  def playNow(self, item):
    self.playlist.append(item)
    self.current = len(self.playlist) - 2
    self.nextSong()

  def toggle(self):
    if (self.toggled):
      self.toggled = False
      self.player.play()
    else:
      self.toggled = True
      self.player.pause()

  def setVolume(self, volume):
    self.volume += int(volume)
    vlc.libvlc_audio_set_volume(self.player, self.volume)
      
  def fullscreen(self):
    self.player.toggle_fullscreen()