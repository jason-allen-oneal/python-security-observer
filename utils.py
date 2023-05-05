#!/usr/bin/env python

import re
import time
from sys import platform
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table


class Utils:
    def __init__(self):
        self.console = Console()

    def msg(self, text, level):
        if 'error' in level:
            print(f'{Fore.RED}[!]{Style.RESET_ALL} {text}')
        if 'warn' in level:
            print(f'{Fore.YELLOW}[!]{Style.RESET_ALL} {text}')
        if 'info' in level:
            print(f'{Fore.BLUE}[*]{Style.RESET_ALL} {text}')
        if 'success' in level:
            print(f'{Fore.GREEN}[$]{Style.RESET_ALL} {text}')
        if 'title' in level:
            print(f'{Fore.CYAN}{text}{Style.RESET_ALL}')

    def countdown(self, t, cb):
        for i in range(t, -1, -1):
            mins, secs = divmod(i, 60)
            timer = f'{mins:02d}:{secs:02d}'
            print(f'{Fore.BLUE}{timer}{Style.RESET_ALL}', end="\r")
            time.sleep(1)
        print(end='')
        cb()

    def displayElapsed(self, t):
        print(f"{Fore.BLUE}{int(t / 3600)}H {int((t / 60) % 60) if t / 3600 > 0 else int(t / 60)}M {int(t % 60)}S{Style.RESET_ALL}")

    def printResult(self, data, elapsed):
        print(f'{Fore.GREEN}Scan completed in: {Style.RESET_ALL}', end='')
        self.displayElapsed(elapsed)
        self.msg('Results', 'title')

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Test")
        table.add_column("Pass")
        table.add_column("Explanation")

        for key in data.keys():
            table.add_row(data[key]['name'], f"{data[key]['pass']}", data[key]['score_description'], end_section=True)

        self.console.print(table)
