import requests
import json
import bottle
import yaml
import logging

logging.basicConfig(level= logging.INFO,format= '[%(asctime)s] [%(process)d] [%(levelname)s]  %(message)s', filename='autorefresh/autorefresh.log', filemode='a')


with open('autorefresh/config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)

PLEXADDR = cfg['PLEXADDR']
TOKEN = cfg['TOKEN']
PORT = cfg['PORT']

logging.info('Config file imported...Starting the service')

app = application = bottle.default_app()


#fetching all libraries IDs
def libraryID():
    libraries = requests.get(PLEXADDR + "/library/sections?X-Plex-Token=" + TOKEN, headers={"Accept":"application/json"})
    liblist = json.loads(libraries.content)["MediaContainer"]["Directory"]
    libcount = len(liblist)
    libidlist = []
    for i in liblist:
        libidlist.append(i["Location"][0]["id"])
    return libidlist


#fetching shows and metadata ids
def contentMetadataID():
    shows = {}
    logging.info('going through your library\'s content. Scraping metadata IDs')
    for i in libraryID():
        x = requests.get(PLEXADDR + "/library/sections/" + str(i) + "/all?X-Plex-Token=" + TOKEN, headers={"Accept":"application/json"})
        y = json.loads(x.content)["MediaContainer"]["Metadata"]
        for q in y:
            try:
                file_dir = q["Media"][0]["Part"][0]["file"]
                metaid = q["ratingKey"]
                shows[file_dir] = metaid
            except:
                file_dir = q["title"]
                metaid = q["ratingKey"]
                shows[file_dir] = metaid
    return shows


@bottle.post("/refresh")
def refresh():
    try:
    # parse input data
        try:
            logging.info('Checking your POST data...!')
            data = bottle.request.json
        except:
            logging.error('Could not process your POST data. check if the data is in JSON format and the header is correctly configured!')
            raise ValueError

        if data is None:
            logging.error('No data have been recived, did you include a JSON formated data?')
            raise ValueError

        if "dir" not in data:
            logging.error('There is no "dir" field in the sent JSON data. ')
            raise ValueError

    except ValueError:
        # if bad request data, return 400 Bad Request
        bottle.response.status = 400
        return
    
    except KeyError:
        # if name already exists, return 409 Conflict
        bottle.response.status = 409
        return
    logging.info('POST data in a correct format has been recieved!')

    try:
        for i in contentMetadataID().keys():
            if data["dir"] in i:
                metaid = contentMetadataID()[i]
                logging.info('Found a match in your library, metadata ID is ' + str(metaid))
            elif i in data["dir"]: # Basicly tv shows as they have one metadata
                logging.warn('Did not find a match in the library, seems like this is a TV series')
                metaid = contentMetadataID()[i]
                logging.info('Found a match for a TV series')
        # Send the request for the metadata refresh
        try:
            logging.info('Sending refresh command to Plex Media Server')
            r = requests.put(PLEXADDR +"/library/metadata/" + str(metaid) + "/refresh?X-Plex-Token=" + TOKEN)
        except:
            logging.error('There was some problem sending the command to Plex!! Aborting!')
    except:
        return "Could not find the dir, make sure its correct"
    logging.info('SUCCESS!!')
    return "done"

if __name__ == '__main__':
    bottle.run(server= 'gunicorn',host = '0.0.0.0', port = PORT)
