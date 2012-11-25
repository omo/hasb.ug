

import hasbug.testing as testing
import hasbug.user as user

if not testing.enable_database:
    user.fake_urlopen()
    user.add_fake_mojombo_to_urlopen()
