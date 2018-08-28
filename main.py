#!/usr/bin/env python3

import sys, os
pathname = os.path.dirname(sys.argv[0])
sys.path.append(pathname)

from MusicBot import MusicBot

bot = MusicBot()
bot.readConfig()
bot.connect()
while (bot.isRunning()):
  bot.update()
  