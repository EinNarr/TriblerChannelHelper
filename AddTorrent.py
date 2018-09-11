import argparse
import requests
import os
import urllib
import base64

def main(args):
    my_cid = requests.get("http://localhost:8085/mychannel").json()["mychannel"]["identifier"]

    torrent_list = list()
    for root, dirs, files in os.walk(args.torrent_path):
        for file in files:
            if file.endswith(".torrent"):
                torrent_list.append(os.path.join(root, file))

    for torrent in torrent_list:
        with open(torrent, "rb") as torrent_file:
            torrent_content = urllib.quote_plus(base64.b64encode(torrent_file.read()))
            print requests.put('http://localhost:8085/channels/discovered/%s/torrents'%my_cid, 'torrent=%s'%torrent_content).json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch download torrents in a same directory.')
    parser.add_argument('--torrent_path', type=str, help='The directory for torrents.', default='./torrents')
    args = parser.parse_args()

    main(args)