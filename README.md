# autorefresh 🎥
Plex autorefresh is python scripted solution to a problem that has been around for many years without any apparent solution.

Autorefresh issues a force metadata update of a specific Movie/show which force detecting any changes in subtitles, an issue which apparently happens with rclone mounted libraries and subtitle solutions like bazarr.

Autorefresh offer a webhook solution. Post calls to it with json information about the desired folder to refresh will send a refresh command to your plex server through plex api. You are going to need your plex token for this. 

## Installation
Python >= 3.7 is required. I recommend creating a virtual environment if you are going to install it directly on your machine. Created and tested on a linux based machine, should work fine in windows.

```
git clone https://github.com/ajmandourah/autorefresh.git
cd autorefresh
pip install -r requirements.txt
```
edit the config.yaml with any text editor. paste in your plex address and Plex token ( [Find your X-plex-token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) )

Create a systemctl entry in /etc/systemd/system lso the script can start on boot. you can use the following template.

```
#autorefresh.service
[Service]
ExecStart=Path/to/python /path/to/autorefresh/main.py
Restart=always
Type=simple
RestartSec=15s
WorkingDirectory=/path/to/autorefresh/dir/
User=YOUR USER

[Install]
WantedBy=multi-user.target

```

## How to use autorefresh
Autorefresh exposes a webhook point at `/refresh` on the port that you defined, default is port `6969`. Sending post requests with attached `Content-Type: application/json` header and JSON formated data with a `dir` key with the directory of the content you want will send a refresh metadata request to your plex server.

using curl the command will look like this
```
curl -X POST http://127.0.0.1:6969/refresh -d '{"dir":"/movies/Paul Blart Mall Cop (2009)"}' -H 'Content-Type: application/json'
```

The curl command can be used as post processing script in bazarr like this

```
curl -X POST http://127.0.0.1:6969/refresh -d '{"dir":"{{directory}}"}' -H 'Content-Type: application/json'
```

## How it works
Plex API allow you to issue a scan library command as per [Plex Media Server URL commands](https://support.plex.tv/articles/201638786-plex-media-server-url-commands/). This has been used in most of the autoscan script including plex_autoscan and autoscan. There is no mention of the ability to issue a directed metadata refresh of a specefic content here rather a full metadata refresh of the whole library.
While inspecting the api I discovered you can do a refresh command of a specefic content if the metadata id is known. the script will scrape your libraries for metadata ids and see if it match. it will then send a request for metadata refresh on that specefic metadata.

## Limitations
The biggest limitation is TV series. the metadata id is for the whole show. this will result in refreshing all this specefic show metadata.

## Todo
- do a more thourough API hunt to see if the TV show limitations can be fixed.
- Create a page for manual post requests.
- you tell me...
