# autorefresh 🎥
Plex autorefresh is python scripted solution to a problem that has been around for many years without any apparent solution.

Autorefresh issues a force metadata update of a specific Movie/show which force detecting any changes in subtitles, an issue which apparently happens with rclone mounted libraries and subtitle solutions like bazarr.

Autorefresh offer a webhook solution. Post calls to it with json information about the desired folder to refresh will send a refresh command to your plex server through plex api. You are going to need your plex token for this. 
