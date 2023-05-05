import requests
import time
from requests.exceptions import HTTPError
from urllib.parse import urlencode
from utils import Utils


class Scanner:
    def __init__(self, options):
        self.options = options
        self.base = 'https://http-observatory.security.mozilla.org/api/v1/'
        self.start = time.time()
        self.end = None
        self.scan_id = None
        self.state = None
        self.running = True

        self.utils = Utils()
        self.status_result = None
        self.scan_result = None

    def make_post(self, action, params):
        try:
            response = requests.post(f'{self.base}{action}?host={self.options.target}', params)
            response.raise_for_status()
            if self.options.verbosity:
                print('Scan initiation response: ', end='')
                print(response.json())
            return response.json()
        except HTTPError as http_err:
            self.utils.msg(f'HTTP error occurred: {http_err}', 'error')
            exit(1)
        except Exception as err:
            self.utils.msg(f'Other error occurred: {err}', 'error')
            exit(1)

    def make_get(self, action, params):
        try:
            p = urlencode(params)
            response = requests.get(f'{self.base}{action}?{p}')
            if self.options.verbosity:
                print(f'{action} response: ', end='')
                print(response.json())
            return response.json()
        except HTTPError as http_err:
            self.utils.msg(f'HTTP error occurred: {http_err}', 'error')
            exit(1)
        except Exception as err:
            self.utils.msg(f'Other error occurred: {err}', 'error')
            exit(1)

    def begin(self):
        result = self.make_post('analyze', {'hidden': 'true', 'rescan': 'true'})

        if "error" in result:
            err = result['text']
            if "cooldown" in err:
                if self.running != 'cooldown':
                    self.utils.msg(f'{self.options.target} is in cooldown. Waiting 3 minutes as required by the API.', 'warn')
                self.running = 'cooldown'
                self.utils.countdown(int(3*60), self.rescan)
            else:
                self.utils.msg(err, 'error')
                exit(1)
        else:
            self.state = result['state']
            self.scan_id = result['scan_id']

    def check_results(self):
        self.status_result = self.make_get('analyze', {'host': self.options.target})

        if 'error' in self.status_result:
            self.utils.msg(self.status_result['text'], 'error')
        else:
            self.state = self.status_result['state']

        if self.state == 'FINISHED':
            self.check_tests()

    def check_tests(self):
        self.scan_result = self.make_get('getScanResults', {'scan': self.scan_id})
        self.running = False
        self.end = time.time()

    def rescan(self):
        self.running = True
        self.begin()
