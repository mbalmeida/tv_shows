#!/usr/bin/python -tt

"""
"""

import sys
import urllib, urllib2
import re
import string

class Episode:
  name        = ''
  number      = -1
  season      = -1
  rating      = -1
  description = ''
  aired       = ''

  def __init__ (object):
    pass

  def dump_0(self):
    """
    """
    print "S%dE%d.%s. %s %s" % (self.season, 
                                self.number, 
                                self.name, 
                                self.aired, 
                                self.rating)
    print "%s" % (self.description)


class ParseHttp:
  """
  Retrives URLs from 'www.tv.com/shows/NAME/episodes/?printable=1'
  """
  
  baseURL     = 'http://www.tv.com/shows/'
  suffix      = '/episodes/?printable=1'
  tvshow_name = ''
  page        = ''
  episodes     = []

  def __init__ (self, name):
    self.tvshow_name = name
    self.loadURL()

  def loadURL(self):
    """
    """
    print self.baseURL + self.tvshow_name + self.suffix

    self.page = urllib2.urlopen(self.baseURL + 
                                self.tvshow_name + 
                                self.suffix).read()

  def __get_episode_name__(self, match):
    """
    Example:
    <li class="episode">
      <a class="title" href="...">EPISODE NAME</a>
    """
    name = re.search(r"<li class=\"episode\">\s*"
                     "<a class=\"title\" href=\"[a-zA-Z0-9-/\s\"]*>"
                     "([a-zA-Z0-9-\.'\s]*)</a>",
                     match)
    if not name:
      print "Warning : Couldn't find name\n"
      return "Undefined"

    return  name.group(1)

  def __get_episode_description__(self, match):
    """
    [<p>]Description[<p>]</div>
    """
    match = re.search(">\s*([a-zA-Z0-9\s,.\'-<>/]*)\s*</div>",
                      match)
    
    if not match:
      print "No description"
      return ''

    return match.group(1).strip()

  def __get_episode_number__(self, match):
    """
    Example:
    <dt>Episode</dt>
    <dd>5</dd>   
    """
    match = re.search("<dt>Episode</dt>\s*<dd>([0-9]*)</dd>", 
                      match)
    
    if not match:
      print "No episode number"
      return -1

    return int(match.group(1))

  def __get_episode_rating__(self, match):
    """
    <dt>Rating</dt>
    <dd>
    8.6
    "Great"
    </dd>
    """
    match = re.search("<dt>Rating</dt>\s*<dd>\s*([0-9\.]*)", 
                      match)
    
    if not match:
      print "No rating info"
      return ''

    return match.group(1)

  def __get_episode_season__(self, match):
    """
    Example:
    <dt>Season</dt>
    <dd>5</dd>   
    """
    match = re.search("<dt>Season</dt>\s*<dd>([0-9]*)</dd>", 
                      match)
    
    if not match:
      print "No season info"
      return -1

    return int(match.group(1))

  def __get_episode_aired__(self, match):
    """
    <dt>Episode</dt>
    <dd>23</dd>
    """
    match = re.search("<dt>First Aired</dt>\s*<dd>([0-9/]*)</dd>",
                      match)
    
    if not match:
      print "No aired info"
      return ''

    return match.group(1)

  def emit_list_episodes_orgmode(self, filename):
    """
    This function emits a list of episodes using org-mode's syntax
    * tv-show Name
    ** Episodes
    *** Season X Episode Y Aired : ZZ Rating : WW
        Description....
    *** Season X Episode Y Aired : ZZ Rating : WW
        Description....
    """

    fileObj = open(filename, 'w')
    
    for ep in self.episodes:
      fileObj.write('***' + 
                    ' Season:'  + str(ep.season))
      fileObj.write(' Episode:' + str(ep.number))
      fileObj.write('\tAired:'   +     ep.aired)      
      fileObj.write('\tRating:'  + str(ep.rating))
      fileObj.write('\n')
      fileObj.write(ep.description)
      fileObj.write('\n')

    fileObj.close()


  def parsePage(self):
    """
    """

    self.page = string.replace(self.page, "</li>","<~~~~~>")
    
    matches = re.findall(r"<li class=\"episode\">\s*[a-zA-Z0-9.<>\s=/\"-_\'\.,]*"
                         "<~~~~~>",
                         self.page)
    
    if not matches:
      print "Problem parsing page"
      return

    for match in matches:
      ep = Episode()
      ep.name        = self.__get_episode_name__(match)
      ep.season      = self.__get_episode_season__(match)
      ep.number      = self.__get_episode_number__(match)
      ep.aired       = self.__get_episode_aired__(match)
      ep.rating      = self.__get_episode_rating__(match)
      ep.description = self.__get_episode_description__(match)
      ep.description = string.replace(ep.description,"<p>","")
      ep.description = string.replace(ep.description,"</p>","")

#      ep.dump_0()
      self.episodes.append(ep)

if __name__ == '__main__':
  args = sys.argv[1:]
#  teste = ParseHttp('the-big-bang-theory')
#  teste = ParseHttp('fringe')
  teste = ParseHttp('game-of-thrones')
  teste.parsePage()
  teste.emit_list_episodes_orgmode("gameofthrones.org")
