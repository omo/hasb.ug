# -*- coding: utf-8 -*-
import re
import zlib
import flask as f

class BackgroundImage(object):
    def __init__(self, url, credit):
        self.url = url
        self.credit = credit

    @property
    def credit_url(self):
        return self.creadit

    @property
    def credit_name(self):
        return re.match("http://www.flickr.com/photos/([^/]+)", self.credit).group(1)

index_background = BackgroundImage('http://farm4.staticflickr.com/3127/3308532489_6a1bbf61fa_b.jpg', "http://www.flickr.com/photos/rnw/3308532489/")
host_backgrounds = [
    BackgroundImage('http://farm6.staticflickr.com/5230/5660512933_19572efc37_b.jpg', 'http://www.flickr.com/photos/powi/5660512933/'),
    BackgroundImage('http://farm3.staticflickr.com/2522/4148872265_9ea723d1f4_b.jpg', 'http://www.flickr.com/photos/stuckincustoms/'),
    BackgroundImage('http://farm1.staticflickr.com/30/48858315_4448d1286b_b.jpg', 'http://www.flickr.com/photos/syldavia/48858315/'),
    BackgroundImage('http://farm4.staticflickr.com/3434/3366906291_c489ff17b2_o.jpg', 'http://www.flickr.com/photos/mugley/3366906291/'),
    BackgroundImage('http://farm6.staticflickr.com/5286/5323110200_4b8e353a9e_b.jpg', 'http://www.flickr.com/photos/49980618@N08/5323110200/'),
    BackgroundImage('http://farm1.staticflickr.com/41/87689672_4f7b6e4cd2_b.jpg', 'http://www.flickr.com/photos/jeffd/87689672/'),
    BackgroundImage('http://farm2.staticflickr.com/1155/1314862556_bc54f9d59b_b.jpg', 'http://www.flickr.com/photos/leff/1314862556/'),
    BackgroundImage('http://farm1.staticflickr.com/110/275699409_fbcdbf42e5_b.jpg', 'http://www.flickr.com/photos/roboppy/275699409/'),
    BackgroundImage('http://farm1.staticflickr.com/86/275048852_77aa1a7392_b.jpg', 'http://www.flickr.com/photos/moirabot/275048852/'),
    BackgroundImage('http://farm2.staticflickr.com/1353/1316145314_6e050ef82b_b.jpg', 'http://www.flickr.com/photos/eole/1316145314/'),
    BackgroundImage('http://farm5.staticflickr.com/4009/4438209398_d1c8a6bc74_b.jpg', 'http://www.flickr.com/photos/gaensler/4438209398/'),
    BackgroundImage('http://farm4.staticflickr.com/3160/2316473778_fe71869119_b.jpg', 'http://www.flickr.com/photos/tonivc/2316473778/')
]

def choose_backgrond(host):
    return host_backgrounds[abs(zlib.adler32(host))%len(host_backgrounds)]


#
# Filters
#
def register_helpers(app):
    @app.template_filter('link_to_profile')
    def link_to_profile(s):
        return "http://github.com/{0}".format(s)
    
    @app.template_filter('link_to_host')
    def link_to_host(s):
        return "http://{0}/".format(s)
    
    @app.template_filter('pattern_to_ellipsis')
    def pattern_to_ellipsis(p):
        return p.format(id="...")
    
    @app.template_filter('urlencode')
    def urlencode_filter(s):
        return urllib.quote_plus(s)

