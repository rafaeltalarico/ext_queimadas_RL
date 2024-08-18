import urllib
import urllib.request
import urllib.parse


class Requester:

    def __init__(self):
        self.__responseCode = 0
        self.__timeout = 60
        self.__headers = {}

    def getResponseCode(self):
        return self.__responseCode

    def getHeaders(self):
        return self.__headers

    def setTimeout(self, timeout):
        self.__timeout = timeout

    def requestGet(self, url, headers=None):
        self.__responseCode = 0
        requisition = urllib.request.Request(url, method='GET')
        requisition.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        if headers is not None:
            for header in headers.items():
                requisition.add_header(header[0], header[1])

        try:
            response = urllib.request.urlopen(requisition, timeout=self.__timeout)
        except urllib.error.HTTPError as e:
            print(f'HTTPError: {e.code}', end=' ')
        except urllib.error.URLError as e:
            print(f'URLError: {e.reason}', end=' ')
        else:
            self.__headers = response.info()
            self.__responseCode = response.getcode()
            return response.read().decode('utf-8')

    def requestPost(self, url, headers=None, data=None):
        self.__responseCode = 0
        if data == None:
            raise Exception('Post data parameter cant be None.')

        requisition = urllib.request.Request(url, method='POST', data=data.encode('utf-8'))
        requisition.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        if headers is not None:
            for header in headers.items():
                requisition.add_header(header[0], header[1])

        try:
            response = urllib.request.urlopen(requisition, timeout=self.__timeout)
        except urllib.error.HTTPError as e:
            print(f'HTTPError: {e.code}', end=' ')
        except urllib.error.URLError as e:
            print(f'URLError: {e.reason}', end=' ')
        else:
            self.__headers = response.info()
            self.__responseCode = response.getcode()
            return response.read().decode('utf-8')

    def urlEncode(self, text):
        return urllib.parse.quote_plus(text)
