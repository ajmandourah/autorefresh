import requests
import json
import bottle
import yaml
import logging
import os , sys
import urllib3

def checkConfig():
    if os.path.isfile('autorefresh/config.yaml'):
        with open('autorefresh/config.yaml', 'r') as f:
            cfg = yaml.safe_load(f)

        PLEXADDR = cfg['PLEXADDR']
        TOKEN = cfg['TOKEN']
        PORT = cfg['PORT']
        logging.info('Config file detected!')
        return True
    else:
        with open('autorefresh/config.yaml', 'w') as f:
            f.write('PLEXADDR: http//:127.0.0.1:32400\n')
            f.write('TOKEN: 0000 #put your Token here\n')
            f.write('PORT: 6969')
        logging.warning('Config file is not detected, Creating one, please add your Plex token and edit it to your setting. ')
        return False



app = application = bottle.default_app()


#fetching all libraries IDs
def libraryID():
    session = requests.Session()
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    libraries = session.get(PLEXADDR + "/library/sections?X-Plex-Token=" + TOKEN, headers={"Accept":"application/json"})
    liblist = json.loads(libraries.content)["MediaContainer"]["Directory"]
    libcount = len(liblist)
    libidlist = []
    for i in liblist:
        libidlist.append(i["Location"][0]["id"])
    return libidlist


#fetching shows and metadata ids
def contentMetadataID():
    session = requests.Session()
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    shows = {}
    logging.info('going through your library\'s content. Scraping metadata IDs')
    for i in libraryID():
        x = session.get(PLEXADDR + "/library/sections/" + str(i) + "/all?X-Plex-Token=" + TOKEN, headers={"Accept":"application/json"})
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
    session = requests.Session()
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    checkConfig()
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
            r = session.put(PLEXADDR +"/library/metadata/" + str(metaid) + "/refresh?X-Plex-Token=" + TOKEN)
        except:
            logging.error('There was some problem sending the command to Plex!! Aborting!')
    except:
        logging.warning('Failed!!! either the content was not found or your plex token / plex address was not correct!')
        return "Could not find the dir, make sure its correct"
    logging.info('SUCCESS!! Refresh metadata request sent!')
    return "done"

if __name__ == '__main__':
    output_file_handler = logging.FileHandler("autorefresh/autorefresh.log")
    stdout_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level= logging.INFO,format= '[%(asctime)s] [%(process)d] [%(levelname)s]  %(message)s', handlers=[output_file_handler,stdout_handler])
    # checking ENV
    PLEXADDR = os.getenv('PLEXADDR')
    TOKEN = os.getenv('TOKEN')
    PORT = os.getenv('PORT')

    if not all([PLEXADDR,TOKEN,PORT]):
        logging.info('Not all env variable detected...checking for config file!!')
        status = checkConfig()
        if status == True:
            with open('autorefresh/config.yaml', 'r') as f:
                cfg = yaml.safe_load(f)

            PLEXADDR = cfg['PLEXADDR']
            TOKEN = cfg['TOKEN']
            PORT = cfg['PORT']
            bottle.run(server= 'gunicorn',host = '0.0.0.0', port = PORT)
        else:
            logging.debug('exiting!')
    else:
        bottle.run(server= 'gunicorn',host = '0.0.0.0', port = PORT)


        



