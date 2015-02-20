#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    This script is based on service.library.data.provider
#    Thanks to the original authors

import sys
import xbmc
import xbmcgui
from time import gmtime, strftime

if sys.version_info < (2, 7):
  import simplejson
else:
  import json as simplejson


class LibraryFunctions():
  def __init__(self):
    self.WINDOW = xbmcgui.Window(10000)

  def _get_data(self, _type, useCache):
    # Check if data is being refreshed elsewhere
    if self.WINDOW.getProperty(_type + "-data") == "LOADING":
      count = 0
      while count < 30:
        xbmc.sleep(100)
        count += 1
        if not self.WINDOW.getProperty(_type + "-data") == "LOADING":
          # Data has just been refreshed, return it
          return self.WINDOW.getProperty(_type + "-data")
    if useCache:
      # Check whether there is saved data
      if self.WINDOW.getProperty(_type + "-data") is not "":
        return self.WINDOW.getProperty(_type + "-data")
    # We haven't got any data, so don't send back anything
    return None

  def _fetch_recent_episodes(self, useCache=False):
    data = self._get_data("quartz_tvshelf", useCache)
    if data is not None:
      return data

    # Set that we're getting updated data
    self.WINDOW.setProperty("quartz_tvshelf-data", "LOADING")

    # TODO: Give priority last added episode more then last watched tvshow.
    json_string_tvshows = '{"jsonrpc": "2.0", "id": "service.quartz.tvshelf_gettvshowids", "method": "VideoLibrary.GetTVShows", "params": {"properties": [],'
    json_query_tvshows = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "lastplayed"}}}' % json_string_tvshows)
    json_query_tvshows = unicode(json_query_tvshows, 'utf-8', errors='ignore')
    json_query_tvshows = simplejson.loads(json_query_tvshows)
    if 'result' in json_query_tvshows and 'tvshows' in json_query_tvshows['result']:
      all_tvshow_ids = [tvshow['tvshowid'] for tvshow in json_query_tvshows['result']['tvshows']]
      all_episodes = []
      for show_id in all_tvshow_ids:
        EPISODE_PER_SHOW_LIMIT = 1
        json_string_episodes = '{"jsonrpc": "2.0", "id": "service.quartz.tvshelf_getepisodes", "method": "VideoLibrary.GetEpisodes", "params": {"tvshowid": %d, "properties": ["title", "season", "episode", "file", "resume", "art"], "limits": {"end": %d},' % (show_id, EPISODE_PER_SHOW_LIMIT)
        json_query_episodes = xbmc.executeJSONRPC('%s "sort": {"order": "ascending", "method": "episode"}, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' % json_string_episodes)
        json_query_episodes = unicode(json_query_episodes, 'utf-8', errors='ignore')
        json_query_episodes = simplejson.loads(json_query_episodes)
        if 'result' in json_query_episodes and 'episodes' in json_query_episodes['result']:
          for item in json_query_episodes['result']['episodes']:
            all_episodes.append(item)
    json_query = simplejson.dumps({"result": {"episodes": all_episodes}})
    json_query = unicode(json_query, 'utf-8', errors='ignore')

    self.WINDOW.setProperty("quartz_tvshelf-data", json_query)
    self.WINDOW.setProperty("quartz_tvshelf", strftime("%Y%m%d%H%M%S", gmtime()))

    return json_query
