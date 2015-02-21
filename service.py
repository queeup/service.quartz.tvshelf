#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    This script is based on service.library.data.provider
#    Thanks to the original authors

import xbmc
import xbmcgui
import xbmcaddon
import datetime

addon = xbmcaddon.Addon()
addon_version = addon.getAddonInfo('version')
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')

import library
LIBRARY = library.LibraryFunctions()


def log(txt):
  message = '%s: %s' % (addon_name, txt.encode('ascii', 'ignore'))
  xbmc.log(msg=message, level=xbmc.LOGDEBUG)


class Main:
  def __init__(self):
    self._init_vars()
    a_total = datetime.datetime.now()
    self._fetch_recent()
    b_total = datetime.datetime.now()
    c_total = b_total - a_total
    log('Total time needed for all queries: %s' % c_total)
    # give a possible other instance some time to notice the empty property
    self.WINDOW.setProperty('QuartzTVShelf_Running', 'true')
    self._daemon()

  def _init_vars(self):
    self.WINDOW = xbmcgui.Window(10000)
    self.Player = Widgets_Player(action=self._update)
    self.Monitor = Widgets_Monitor(update_listitems=self._update)

  def _fetch_recent(self):
    LIBRARY._fetch_recent_episodes()

  def _daemon(self):
    # deamon is meant to keep script running at all time
    home_update = False
    while self.WINDOW.getProperty('QuartzTVShelf_Running') == 'true':
      if self.Monitor.waitForAbort():
        log('Abort requested.')
        break
      xbmc.sleep(500)
      if not xbmc.Player().isPlayingVideo():
        if home_update and xbmcgui.getCurrentWindowId() == 10000:
          self._fetch_recent()
          home_update = False
        elif not home_update and xbmcgui.getCurrentWindowId() != 10000:
          home_update = True
    # clear our window property on exit
    self.WINDOW.clearProperty('QuartzTVShelf_Running')
    # clear our monitor classes before exit to avoid left in memory.
    del self.Player
    del self.Monitor

  def _update(self, _type):
    xbmc.sleep(1000)
    if _type == 'episode':
      self._fetch_recent()
    elif _type == 'video':
      # only on db update
      self._fetch_recent()


class Widgets_Monitor(xbmc.Monitor):
  def __init__(self, *args, **kwargs):
    xbmc.Monitor.__init__(self)
    self.update_listitems = kwargs['update_listitems']

  def onScanFinished(self, library):
    self.update_listitems(library)


class Widgets_Player(xbmc.Player):
  def __init__(self, *args, **kwargs):
    xbmc.Player.__init__(self)
    self.type = ""
    self.action = kwargs["action"]

  def onPlayBackStarted(self):
    xbmc.sleep(1000)
    if xbmc.getCondVisibility('VideoPlayer.Content(episodes)'):
      # Check for tv show title and season to make sure it's really an episode
      if xbmc.getInfoLabel('VideoPlayer.Season') != "" and xbmc.getInfoLabel('VideoPlayer.TVShowTitle') != "":
        self.type = "episode"

  def onPlayBackEnded(self):
    self.onPlayBackStopped()

  def onPlayBackStopped(self):
    if self.type == 'episode':
      self.action('episode')

log('service version %s started' % addon_version)
Main()
log('service version %s stopped' % addon_version)
