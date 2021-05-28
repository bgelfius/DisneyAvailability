import sys
sys.path.insert(0, '/var/www/html/Disney')
sys.path.append('/var/www/html/Disney')
sys.path.append(' /usr/lib/python3/dist-packages')
sys.path.append('/home/ubuntu/.local/lib/python3.6/site-packages')

from DisneyEndpoints import app as application

