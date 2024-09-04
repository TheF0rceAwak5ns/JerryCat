import sys

from rich.console import Console
from rich.text import Text
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

console = Console()


class Output:
    def __init__(self, args):
        self.description = ""
        self.base_url = ""
        self.args = args

    @staticmethod
    def header():
        timestamp_width = 35
        url_width = 40
        state_width = 15

        header = Text()
        header.append(f"{'Timestamp':<{timestamp_width}}")
        header.append(f"{'Target':<{url_width}}")
        header.append(f"{'Result':<{state_width}}")
        header.append(f"\n\r{'----------':<{timestamp_width}}")
        header.append(f"{'-------':<{url_width}}")
        header.append(f"{'-------':<{state_width}}")

        console.print(header, style="bold")

    def message(self, state: str, description: str, url: str, **kwargs) -> None:

        if 'verbose' in kwargs and not self.args.verbose:
            return

        self.description = description

        if 'clear_before' in kwargs:
            sys.stdout.write("\033[F")  # back to previous line
            sys.stdout.write("\033[K")  # clear line

        text = Text()

        current_time = datetime.now()
        formatted_time = current_time.strftime("%d-%m-%Y %H:%M:%S")

        timestamp_width = 35
        url_width = 40
        state_width = 0

        text.append(f"{formatted_time:<{timestamp_width}}", style='bold')

        base_endpoint = urlparse(self.base_url).path
        full_endpoint = base_endpoint + url

        text.append(f"{full_endpoint:<{url_width}}", style=f'link {full_endpoint}')

        # Format the state text with a fixed width based on the state value
        match state:
            case "credit":
                state_text = "[+] "
                state_style = 'bold pale_turquoise1'
            case "settings":
                state_text = "[#] "
                state_style = 'bold turquoise2'
            case "command":
                state_text = "[+] COMMAND OUTPUT "
                state_style = 'bold yellow'
            case "success":
                state_text = "[+] "
                state_style = 'bold spring_green2'
            case "failed":
                state_text = "[-] "
                state_style = 'bold red1'
            case "error":
                state_text = "[!] "
                state_style = 'bold orange_red1'
            case "ongoing":
                state_text = "[*] "
                state_style = 'bold turquoise2'
            case "exit":
                state_text = "[EXITING] "
                state_style = 'bold red1'
            case _:
                state_text = ""
                state_style = "bold yellow"

        text.append(f"{state_text:<{state_width}}", style=state_style)
        text.append(self.description)

        if state == "success" and "admin" in kwargs:
            text.append(" (Admin account!)", style="bold yellow")

        console.print(text, style='')

    def webshell_response(self, response: str, url: str):

        lines = response.splitlines()

        self.message(state="command", description="", url=url)

        for line in lines:
            self.message(state="", description=line, url=url)