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
          episode = "%.2d" % float(item['episode'])
          season = "%.2d" % float(item['season'])
          episodeno = "s%se%s" % (season, episode)
          plot = item['plot']
          if "cast" in item:
            cast = self._get_cast(item['cast'])
          liz = xbmcgui.ListItem(item['title'])
          liz.setInfo(type="Video", infoLabels={"Title": item['title'],
                                                "Episode": item['episode'],
                                                "Season": item['season'],
                                                "Premiered": item['firstaired'],
                                                "Plot": plot,
                                                "TVshowTitle": item['showtitle'],
                                                "Rating": str(round(float(item['rating']))),
                                                "Playcount": item['playcount'], })
          if "director" in item:
            liz.setInfo(type="Video", infoLabels={"Director": " / ".join(item['director'])})
          if "writer" in item:
            liz.setInfo(type="Video", infoLabels={"Writer": " / ".join(item['writer'])})
          if "cast" in item:
            liz.setInfo(type="Video", infoLabels={"Cast": cast[0]})
            liz.setInfo(type="Video", infoLabels={"CastAndRole": cast[1]})
          liz.setProperty("episodeno", episodeno)
          liz.setProperty("resumetime", str(item['resume']['position']))
          liz.setProperty("totaltime", str(item['resume']['total']))
          liz.setArt(item['art'])
          liz.setThumbnailImage(item['art'].get('thumb', ''))
          liz.setIconImage('DefaultTVShows.png')
          liz.setProperty("dbid", str(item['episodeid']))
          liz.setProperty("fanart_image", item['art'].get('tvshow.fanart', ''))
          for key, value in item['streamdetails'].iteritems():
            for stream in value:
              liz.addStreamInfo(key, stream)
          full_liz.append((item['file'], liz, False))
      del json_query

  def _get_cast(self, castData):
    listCast = []
    listCastAndRole = []
    for castmember in castData:
      listCast.append(castmember["name"])
      listCastAndRole.append((castmember["name"], castmember["role"]))
    return [listCast, listCastAndRole]

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
