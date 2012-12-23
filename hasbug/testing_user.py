

import hasbug.testing as testing
import hasbug.net as net
import hasbug.user as user
import hasbug.conf as conf

if not testing.enable_database:
    net.fake_urlopen()
    user.add_fake_mojombo_to_urlopen()
    conf.fake_google_api_key()
