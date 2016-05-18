(This repository is deprecated. I'm preparing new one which based AWS.)

# Radiople: server application based Flask-Framework


Homepage: [http://radiople.com](http://radiople.com)

I'm developing server, android application it's podcast platform service in Republic of Korea.

*Radiople is not published yet it's still in progress.*

# Getting started

This project is based Flask-Framework and many dependencies.

- Python3.x
- Postgresql9.4 or 9.5 maybe.
- [Conoha](http://conoha.jp) object-storage service (based openstack swift).

Please look up the path `/radiople-app/bin/*`

### Runnable web services
* api: api service with port: 5001
* console: broadcast, episode manage service with port: 5002
* image: image thumbnail service with port: 5003
* web: webpage service with port: 5005
* audio: not using.

### Runnable script
* script: wrapper for something scripts with podcast crawler

# Installation
```
$ git clone git@github.com:leejaycoke/radiople-app.git
$ cd radiople-app
$ virtualenv venv
(venv) $ pip install -r requirements.txt
```

# Configuration

This application need some configuration files for getting db, secret_key, ... information.

Make below files then paste this wiki [contents](https://github.com/leejaycoke/radiople-app/wiki/config).

```
$ touch radiople/config/common.conf, api.conf, web.conf, console.conf, image.conf
```

# Run server

Service are `api`, `console`, `image`, `web`, `script`

```
$./bin/(api|image|web|console) runserver
```
# Thanks
If you have any issue? please let me know [github issue tracker](https://github.com/leejaycoke/radiople-app/issues) or make a email for me leejaycoke@gmail.com.
