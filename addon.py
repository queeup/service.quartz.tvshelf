#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    This script is based on service.library.data.provider
#    Thanks to the original authors

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

if sys.version_info < (2, 7):
  import simplejson
else:
  import json as simplejson

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
    self._parse_argv()

    full_liz = list()
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    self.parse_tvshows('recentepisodes', full_liz)
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), full_liz)
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

  def parse_tvshows(self, request, full_liz):
    json_query = self._get_data(request)
    while json_query == "LOADING":
      xbmc.sleep(100)
      json_query = self._get_data(request)
    if json_query:
      json_query = simplejson.loads(json_query)
      if 'result'in json_query and 'episodes' in json_query['result']:
        for item in json_query['result']['episodes']:
          liz = xbmcgui.ListItem(item['title'])
          liz.setInfo(type="Video", infoLabels={"Title": item['title'],
                                                "Episode": item['episode'],
                                                "Season": item['season'],
                                                })
          liz.setProperty("resumetime", str(item['resume']['position']))
          liz.setArt(item['art'])
          liz.setProperty("fanart_image", item['art'].get('tvshow.fanart', ''))
          full_liz.append((item['file'], liz, False))
      del json_query

  def _get_data(self, request):
    if request == "recentepisodes":
      return LIBRARY._fetch_recent_episodes(self.USECACHE)

  def _parse_argv(self):
    try:
      params = dict(arg.split("=") for arg in sys.argv[2].split("&"))
    except:
      params = {}
    self.USECACHE = params.get("reload", False)
    if self.USECACHE is not False:
      self.USECACHE = True

log('script version %s started' % addon_version)
Main()
log('script version %s stopped' % addon_version)
