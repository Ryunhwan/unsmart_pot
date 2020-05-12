import urllib.request
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        print('true')
        return True
    except:
        return False

connect()
