#!/usr/bin/env python

import sys
import argparse
from utils import Utils
from scanner import Scanner

def validate_domain(domain):
    """Validate domain format"""
    import re
    # Basic domain validation
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if not re.match(pattern, domain):
        raise argparse.ArgumentTypeError(f"Invalid domain format: {domain}")
    return domain

def main_cli(cli_args=None):
    import time
    parser = argparse.ArgumentParser(
        description="HTTP Security Observer - CLI Mode",
        epilog="Example: python3 main.py --cli -u www.example.com"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbosity",
        default=False,
        help="Show all output",
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        dest="target",
        help="Domain on which to perform tests. (REQUIRED)",
    )
    parser.add_argument(
        "-o",
        "--out",
        default=None,
        dest="write",
        help="File to which to write the program's output",
    )
    if cli_args is not None:
        options = parser.parse_args(cli_args)
    else:
        options = parser.parse_args()

    utils = Utils()
    utils.msg("HTTP Security Observer by z3r0POINTz3r0", "title")
    try:
        if options.write is not None:
            try:
                sys.stdout = open(options.write, "a")
            except IOError as e:
                utils.msg(f"Error opening output file: {e}", "error")
                exit(1)

        utils.msg(f"Checking {options.target}", "info")
        scan = Scanner(options)
        scan.begin()

        with utils.console.status("[bold green]Awaiting results...") as status:
            while scan.running:
                scan.check_results()
                time.sleep(5)

        if options.write is not None:
            try:
                sys.stdout.close()
            except IOError as e:
                utils.msg(f"Error closing output file: {e}", "error")

        utils.print_result(scan.scan_result, scan.end - scan.start)
    except KeyboardInterrupt:
        utils.msg("Caught Ctrl+c. Exiting!", "info")
    except Exception as err:
        utils.msg(err, "error")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--cli', action='store_true', help='Run in command-line mode')
    args, remaining = parser.parse_known_args()

    if args.cli:
        main_cli(remaining)
    else:
        from gui import main as gui_main
        gui_main()
