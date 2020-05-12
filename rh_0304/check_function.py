
import urllib.request


def check_internet_on():
    host = 'http://google.com'
    try:
        urllib.request.urlopen(host) #Python 3.x
        print('internet connect')
        return True
    except:
        print('internet disconnect')
        return False