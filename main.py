#!/usr/bin/env python

import sys, requests, time
from optparse import OptionParser
from utils import Utils
from scanner import Scanner

def optionControl():
	parser = OptionParser(usage='%prog [options]\r\nexample: python3 %prog -u www.example.com', version="%prog 0.1")
	
	parser.add_option("-v", "--verbose", action="store_true", dest="verbosity", default=False, help="Show all output")
	
	parser.add_option("-u", "--url", default=None, dest="target", help="Domain on which to perform tests. (REQUIRED)")
	parser.add_option('-o', '--out', default=None, dest='write', help="File to which to write the program's output")
	
	options, args = parser.parse_args()
	
	if options.target is None:
		parser.print_help()
		exit(1)
	
	return (options, args)

def main():
	utils = Utils()
	utils.msg('HTTP Security Observer by Wr37ch3dZ3r0', 'title')
	(options, args) = optionControl()
	try:
		if options.write is not None:
			sys.stdout = open(options.write, "a")
		
		utils.msg(f'Checking {options.target}', 'info')
		scan = Scanner(options)
		scan.begin()
		
		with utils.console.status("[bold green]Awaiting results...") as status: 
			while scan.running:
				scan.checkResults()
				time.sleep(5)
		
		if options.write is not None:
			sys.stdout.close()
		
		utils.printResult(scan.scanResult, scan.end-scan.start)
	except KeyboardInterrupt:
		utils.msg('Caught Ctrl+c. Exiting!', 'info')
	except Exception as err:
		utils.msg(err, 'error')

if __name__ == '__main__':
	main()