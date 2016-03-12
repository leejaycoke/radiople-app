# Radiople: server application based Flask-Framework


Homepage: [http://radiople.com](http://radiople.com)

I'm developing server, android application it's podcast platform service in R. Korea not published yet.

# Getting started

This project is based Flask-Framework and many dependencies.

- Python3.x
- Postgresql9.4 or 9.5 maybe.
- Audio storage use [Conoha](http://conoha.jp) object-storage service.
```

$ git clone git@github.com:leejaycoke/radiople-app.git
$ cd radiople-app
$ virtualenv venv
(venv) $ pip install -r requirements.txt
```

# Configuration

This application need some configuration items likes Database server, secret_key ...

Make below files then paste this wiki [contents](https://github.com/leejaycoke/radiople-app/wiki/config).

```
$ touch radiople/config/common.conf, api.conf, web.conf, console.conf, image.conf
```

# Run server

Service are `api`, `console`, `image`, `web`, `script`

```
$./bin/api runserver
```
