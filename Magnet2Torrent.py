import argparse
import json
import os
import sys
import time
import csv
import tempfile

import libtorrent as lt

import os.path as pt


def main(args):
    lt_session = lt.session()
    lt_session.listen_on(6881, 6891)

    magnet_list = get_magnet(args.csv_path)
    torrent_num = len(magnet_list)
    torrent_handles = list()
    timer = list()
    timer_g = 0

    torrent_count = 0
    torrent_finish = 0
    torrent_fail = 0

    for _ in range(0, min(torrent_num, args.max)+1):
        torrent_handles.append(add_torrent(args, lt_session, magnet_list[torrent_count]))
        timer.append(0)
        torrent_count += 1

    while torrent_finish < torrent_num:
        if not (timer_g % 10):
            print "Timer: " + str(timer_g) + "\t" + str(torrent_finish-torrent_fail) + " success" + " " + str(torrent_fail) + " failure."
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Aborting...")
            ses.pause()
            sys.exit(0)
        timer_g += 1
        for i in range(0, len(torrent_handles)):
            handle = torrent_handles[i]
            timer[i] += 1
            if handle.has_metadata():
                torinfo = handle.get_torrent_info()
                torfile = lt.create_torrent(torinfo)

                output = pt.abspath(torinfo.name() + ".torrent")

                if args.save_path:
                    if pt.isdir(args.save_path):
                        output = pt.abspath(pt.join(
                            args.save_path, torinfo.name() + ".torrent"))
                    elif pt.isdir(pt.dirname(pt.abspath(args.save_path))):
                        output = pt.abspath(args.save_path)

                print("Saving torrent file here : " + output + " ...")
                torcontent = lt.bencode(torfile.generate())
                f = open(output, "wb")
                f.write(lt.bencode(torfile.generate()))
                f.close()
                print("Saved! Cleaning up temp directory.")
                lt_session.remove_torrent(handle, True)
                torrent_finish += 1
                timer[i] = 0
                if torrent_count < torrent_num:
                    torrent_handles[i] = add_torrent(args, lt_session, magnet_list[torrent_count])
                    torrent_count += 1
                    print ("adding new torrent.")

            if timer[i] > 600:
                lt_session.remove_torrent(handle, True)
                torrent_finish += 1
                timer[i] = 0
                if torrent_count < torrent_num:
                    torrent_handles[i] = add_torrent(args, lt_session, magnet_list[torrent_count])
                    torrent_count += 1
                    torrent_fail += 1
                    print ("adding new torrent.")


def get_magnet(csv_file):
    magnet_list = []
    with open(csv_file) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for row in f_csv:
            magnet_list.append(row[1])
    return magnet_list


def add_torrent(args, ltsession, magnet):
    params = {
        'save_path': args.save_path+"/temp",
        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True
    }

    torrent_handle = lt.add_magnet_uri(ltsession, magnet, params)

    return torrent_handle

def stop_download(args, lt_session, torrent_handle):
    torrent_handle.pause()
    lt_session.remove_torrent(torrent_handle, args.delete_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch download torrents in a same directory.')
    parser.add_argument('--save_path', type=str, help='The directory for torrents.', default='./torrents')
    parser.add_argument('--csv_path', type=str, help='The path for csv file.', default="torrents.csv")
    parser.add_argument('--max', type=int, help='m', default=20)
    args = parser.parse_args()

    main(args)
