#!/usr/bin/env python

import requests, json, time
from requests.exceptions import HTTPError
from urllib.parse import urlencode
from utils import Utils

class Scanner:
	def __init__(self, options):
		self.options = options
		self.base = 'https://http-observatory.security.mozilla.org/api/v1/'
		self.start = time.time()
		self.end = None
		self.scanId = None
		self.state = None
		self.running = True
		
		self.utils = Utils()
		self.statusResult = None
		self.scanResult = None
	
	def makePost(self, action, params):
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
	
	def makeGet(self, action, params):
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
		result = self.makePost('analyze', {'hidden': 'true', 'rescan': 'true'})
		
		if "error" in result:
			err = result['text']
			if "cooldown" in err:
				if self.running != 'cooldown':
					self.utils.msg(f'{self.options.target} is in cooldown.  Waiting 3 minutes as required by the API.', 'warn')
				self.running = 'cooldown'
				self.utils.countdown(int(3*60), self.rescan)
			else:
				self.utils.msg(err, 'error')
				exit(1)
		else:
			self.state = result['state']
			self.scanId = result['scan_id']
	
	def checkResults(self):
		self.statusResult = self.makeGet('analyze', {'host': self.options.target})
		
		if 'error' in self.statusResult:
			self.utils.msg(self.statusResult['text'], 'error')
		else:
			self.state = self.statusResult['state']
		
		if self.state == 'FINISHED':
			self.checkTests()
	
	def checkTests(self):
		self.scanResult = self.makeGet('getScanResults', {'scan': self.scanId})
		self.running = False
		self.end =time.time()
	
	def rescan(self):
		self.running = True
		self.begin()