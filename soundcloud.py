from bs4 import BeautifulSoup
import urllib2
import re

''' soundcloud:

Basic SoundCloud page-scraping interface, allows listing a user's sets, tracks
and the tracks in a set, as well as getting the streaming audio url for a 
track.
'''

# get main-content-inner divs from multiple index pages
def scpages(url):
    results = []
    nexturl = url
    while nexturl:
        maincontent = BeautifulSoup(urllib2.urlopen(nexturl).read()).find("div",attrs={'id':'main-content-inner'})
        pagination = maincontent.find("div",attrs={'class':'pagination'})
        if pagination:
            nextpagelink = pagination.find('a',attrs={'class':'next_page'})
            if nextpagelink:
                nexturl = urllib2.urlparse.urljoin(nexturl, nextpagelink.attrs['href'])
            else:
                nexturl = None
        else:
            nexturl = None
        results = results + [maincontent]
    return results

# get a list of ("seturl", "Set Name") of the specified user's sets
def scusersets(user):
	return [(link.get('href'), link.text) for link in reduce(lambda x, y: x+y, [[li.find('h3').find('a') for li in page.findAll("li", "set")] for page in scpages("http://www.soundcloud.com/%s/sets" % (user,))], [])]

# get a list of ("trackurl", "Track Name") of the specified set's tracks
def scsettracks(seturl):
	return [(a.get('href'), a.text) for a in [li.find("a", "set-track-title") for li in BeautifulSoup(urllib2.urlopen(urllib2.urlparse.urljoin("http://www.soundcloud.com/", seturl)).read()).findAll("li", attrs={"data-sc-list-position":re.compile("[0-9]+")})]]

# get a list of ("trackurl", "Track Name") of the specified user's tracks
def scusertracks(user):
	return [(link.attrs['href'], link.text) for link in reduce(lambda x, y: x + y, [[li.find('h3').find('a') for li in page.find_all('li', attrs={'class':'player'})] for page in scpages("http://www.soundcloud.com/%s/tracks" % (user,))], [])]

# get a url for streaming audio playback of the specified track
def scstreamurl(trackurl):
	return re.search('"streamUrl":"([^"]*)"', BeautifulSoup(urllib2.urlopen(urllib2.urlparse.urljoin("http://www.soundcloud.com/", trackurl)).read()).find("div", id="main-content-inner").find("script", text=re.compile('"streamUrl":')).text).group(1)

