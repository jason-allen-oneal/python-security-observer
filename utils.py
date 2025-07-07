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
        elif 'warn' in level:
            print(f'{Fore.YELLOW}[!]{Style.RESET_ALL} {text}')
        elif 'info' in level:
            print(f'{Fore.BLUE}[*]{Style.RESET_ALL} {text}')
        elif 'success' in level:
            print(f'{Fore.GREEN}[$]{Style.RESET_ALL} {text}')
        elif 'title' in level:
            print(f'{Fore.CYAN}{text}{Style.RESET_ALL}')
        else:
            print(f'{text}')

    def countdown(self, t, cb):
        for i in range(t, -1, -1):
            mins, secs = divmod(i, 60)
            timer = f'{mins:02d}:{secs:02d}'
            print(f'{Fore.BLUE}{timer}{Style.RESET_ALL}', end="\r")
            time.sleep(1)
        print(end='')
        cb()

    def display_elapsed(self, t):
        print(f"{Fore.BLUE}{int(t / 3600)}H {int((t / 60) % 60) if t / 3600 > 0 else int(t / 60)}M {int(t % 60)}S{Style.RESET_ALL}")

    def print_result(self, data, elapsed):
        print(f'{Fore.GREEN}Scan completed in: {Style.RESET_ALL}', end='')
        self.display_elapsed(elapsed)
        self.msg('Results', 'title')

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Score", style="yellow")
        table.add_column("Description", style="white")

        for key in data.keys():
            test_data = data[key]
            status = "✅ PASS" if test_data['pass'] else "❌ FAIL" if test_data['pass'] is False else "⚠️  INFO"
            score = f"{test_data['score_modifier']:+d}" if test_data['score_modifier'] != 0 else "0"
            
            # Clean up HTML tags from description
            description = test_data['score_description']
            if description:
                import re
                description = re.sub(r'<[^>]+>', '', description)  # Remove HTML tags
                description = description.replace('\n', ' ').strip()  # Clean up whitespace
                description = description[:80] + "..." if len(description) > 80 else description
            
            table.add_row(
                test_data['name'],
                status,
                score,
                description
            )

        self.console.print(table)
        
        # Print summary
        total_tests = len(data)
        passed_tests = sum(1 for test in data.values() if test['pass'] is True)
        failed_tests = sum(1 for test in data.values() if test['pass'] is False)
        info_tests = total_tests - passed_tests - failed_tests
        
        print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {Fore.GREEN}{passed_tests}{Style.RESET_ALL}")
        print(f"  Failed: {Fore.RED}{failed_tests}{Style.RESET_ALL}")
        print(f"  Info: {Fore.YELLOW}{info_tests}{Style.RESET_ALL}")
