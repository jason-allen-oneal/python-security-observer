import requests
import time
from requests.exceptions import HTTPError
from urllib.parse import urlencode
from utils import Utils


class Scanner:
    def __init__(self, options):
        self.options = options
        self.base = 'https://observatory-api.mdn.mozilla.net/api/v2/'
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
            raise
        except Exception as err:
            self.utils.msg(f'Other error occurred: {err}', 'error')
            raise

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
            raise
        except Exception as err:
            self.utils.msg(f'Other error occurred: {err}', 'error')
            raise

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
                raise Exception(err)
        else:
            # Check if scan is already complete
            if 'scan' in result and result['scan'] and result['scan'].get('error') is None:
                # Scan is complete, extract results
                self.scan_id = result['scan']['id']
                self.scan_result = result['tests']
                self.running = False
                self.end = time.time()
            else:
                # Scan is in progress, extract state and scan_id
                self.state = result.get('state', 'UNKNOWN')
                self.scan_id = result.get('scan_id')

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
