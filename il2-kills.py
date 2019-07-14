#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Caian Benedicto <caianbene@gmail.com>
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys, requests, logging, glob, os.path
from datetime import datetime, timedelta, timezone

class Sortie(object):
    """"""    

    def __init__(self, sortie):
        """"""
        # Do basic check on the sortie array
        if len(sortie) != 8:
            logging.critical('Unknown sortie format, found %d elements!', len(sortie))
            raise RuntimeError()
        # Parse the start date
        start_date = '%s-%s' % (sortie[0], sortie[1])
        start_date = datetime.strptime(start_date, '%d.%m.%Y-%H:%M')
        start_date = start_date.replace(tzinfo=timezone.utc)
        # Parse the duration time
        duration = None
        try:
            duration = [int(i) for i in sortie[4].split(':')]
        except:
            pass
        if duration is None or len(duration) != 2:
            logging.critical("Unknown sortie format, duration '%s' is invalid!", sortie[4])
            raise RuntimeError()
        duration = timedelta(hours=duration[0], minutes=duration[1])
        # Parse the number of air kills
        try:
            air_kills = int(sortie[5])
        except:
            logging.critical("Unknown sortie format, air kills '%s' are invalid!", sortie[5])
            raise RuntimeError()
        # Parse the number of ground kills
        try:
            ground_kills = int(sortie[6])
        except:
            logging.critical("Unknown sortie format, air kills '%s' are invalid!", sortie[6])
            raise RuntimeError()
        # Set the attributes of the class
        self._start_date = start_date
        self._duration = duration
        self._air_kills = air_kills
        self._ground_kills = ground_kills


    @property
    def start(self):
        """"""
        return self._start_date


    @property
    def duration(self):
        """"""
        return self._duration


    @property
    def end(self):
        """"""
        return self._start_date + self.duration


    @property
    def air_kills(self):
        """"""
        return self._air_kills


    @property
    def ground_kills(self):
        """"""
        return self._ground_kills


    @property
    def kills(self):
        """"""
        return self.air_kills + self.ground_kills


class TrackRecord(object):
    """"""

    @staticmethod
    def get_track_extension():
        """Get the track file extension."""
        return '.trk'


    def __init__(self, path : str):
        """Constructor."""
        # Get the track name from the full file path
        trkdir, trkname = os.path.split(path)
        trkname, ext = os.path.splitext(trkname)
        # Check if it is a valid track file
        if ext.lower() != TrackRecord.get_track_extension():
            logging.critical('Invalid track extension %s!', ext)
            raise RuntimeError()
        # Check for its matching track directory
        trkdir, _ = os.path.splitext(path)
        if not os.path.exists(trkdir):
            logging.critical('Track file %s missing its matching diretory!', trkname)
            raise RuntimeError()
        if not os.path.isdir(trkdir):
            logging.critical('Track file %s missing its matching diretory!', trkname)
            raise RuntimeError()
        # Get the birth and last modification dates of the track file
        ctime = datetime.fromtimestamp(os.path.getctime(path), timezone.utc)
        mtime = datetime.fromtimestamp(os.path.getmtime(path), timezone.utc)
        # Set the attributes of the class
        self._name = trkname
        self._dir = trkdir
        self._ctime = ctime
        self._mtime = mtime


    @property
    def name(self):
        """Get the name of the track."""
        return self._name


    @property
    def start(self):
        """Get the start (creation) date of the track."""
        return self._ctime


    @property
    def end(self):
        """Get the end (last modification) date of the track."""
        return self._mtime


    @property
    def was_renamed(self):
        """Get if the track was already renamed by some program."""
        # Check the start of the file
        if not self._name.startswith('dogfight.'):
            return True
        # And check for the trailing _00, _01, ...
        u = self._name.rfind('_')
        if u < 0:
            return True
        for c in self._name[u+1:]:
            if c < '0' or c > '9':
                return True
        return False


    def rename(self, air_kills : int, ground_kills : int):
        """Rename the track file and directory"""
        new_name = 'ilk_%da_%dg_%s' % (air_kills, ground_kills, self.name)
        # TODO rename
        self._name = new_name


def scan_dir(dir):
    """List all track files in a directory."""
    logging.info("Scanning directory '%s'...", dir)
    # Check if the directory exists
    if not os.path.exists(dir):
        logging.critical("Diretory '%s' does not exist!", dir)
        raise RuntimeError()
    if not os.path.isdir(dir):
        logging.critical("Path '%s' is not a directory!", dir)
        raise RuntimeError()
    # Filter all files with the il2 track extension
    wildcard = '*%s' % TrackRecord.get_track_extension()
    files = glob.glob(os.path.join(dir, wildcard))
    tracks = []
    for file in files:
        logging.info("Found file '%s'.", file)
        # Create a track record object from the file path
        track = TrackRecord(file)
        # Ignore recordings that were renamed
        if track.was_renamed:
            logging.info("Track %s was already renamed and will be ignored.", track.name)
            continue
        # Estimate the total time of the recording as the 
        # difference between its creation and last modification
        cstr = track.start.strftime('%Y/%m/%d %H:%M:%S')
        etime = int((track.end - track.start).total_seconds())
        if etime < 60:
            etime = '%d seconds' % etime
        else:
            etime = '%d minutes' % (etime // 60)
        logging.info("Track '%s' - %s, %s.", track.name, cstr, etime)
        # Add the track to the list of valid tracks to check
        tracks.append(track)
    logging.info("Found %d renamable tracks.", len(tracks))
    return tracks


def scan_server(server, user, sortie_callback):
    """"""
    # Get the main sorties page
    url = '%ssorties/%s/' % (server, user)
    logging.info("User sorties URL is '%s'.", url)
    response = requests.get(url)
    html = response.text
    # The HTML elements that will be used to find sorties data
    text_tour = '<a href="?tour='
    text_ctour = '">'
    text_sortie = 'href="/en/sortie/'
    text_cell = '<div class="cell">'
    text_ca = '</a>'
    text_cdiv = '</div>'
    # List available tours in the server
    logging.info("Listing tours...")
    tours = []
    last_tour = -1
    while True:
        tour = html.find(text_tour, last_tour + 1)
        if tour < 0:
            break
        ctour = html.find(text_ctour, tour + 1)
        if ctour < 0:
            logging.critical("Missing '%s' after '%s'!", text_tour, text_ctour)
            exit(1)
        tours.append(html[tour+len(text_tour):ctour])
        last_tour = tour
    # Print the tours found
    logging.info("Tours: %s.", ', '.join(tours))
    # Scan through all tours
    for tour in tours:
        # Scan multi page tours
        page = 1
        while True:
            # Get the current page of the current tour
            logging.info("Fetching tour %s, page %d...", tour, page)
            url = '%ssorties/%s/?tour=%s&page=%d' % (server, user, tour, page)
            logging.info("Tour URL is '%s'.", url)
            response = requests.get(url)
            html = response.text
            # There is no data in the HTML to tell the last page, 
            # so do trial an error
            if response.status_code == 404:
                logging.info("URL not found, ending tour.")
                break
            # Anything other than 'not found' is a real error
            elif response.status_code != 200:
                logging.critical("Server returned error %d!", response.status_code)
                exit(1)
            # Scan trough all sorties
            last_sortie = -1
            while True:
                sortie = html.find(text_sortie, last_sortie + 1)
                if sortie < 0:
                    break
                ca = html.find(text_ca, sortie + 1)
                if ca < 0:
                    logging.critical("Missing '%s' after '%s'!", text_sortie, text_ca)
                    exit(1)
                last_sortie = ca
                # Scan through all HTML table columns for the data
                last_cell = sortie
                line = []
                while True:
                    cell = html.find(text_cell, last_cell + 1)
                    if cell < 0 or cell > last_sortie:
                        break
                    cdiv = html.find(text_cdiv, cell + 1)
                    if cdiv < 0:
                        logging.critical("Missing '%s' after '%s'!", text_cell, text_cdiv)
                        exit(1)
                    col = html[cell+len(text_cell):cdiv]
                    line.append(col.strip())
                    last_cell = cell
                # Process the sortie using a callback and 
                # allow it to abort the scan
                if not sortie_callback(line):
                    return
            # Move to the next page
            page = page + 1


def print_sortie(sortie):
    """"""
    sortie = Sortie(sortie)
    sdate = sortie.start.strftime('%Y/%m/%d %H:%M:%S')
    etime = sortie.duration.total_seconds() // 60
    if etime < 60:
        etime = '%d minutes' % etime
    else:
        etime = '%d hours' % (etime // 60)
    logging.info("Sortie %s, %s - %d kills.", sdate, etime, sortie.kills)
    return True


if __name__ == '__main__':
    # Validate the input arguments
    if len(sys.argv) != 4:
        print('USAGE: ./il2-kills.py track_dir server_url usercode/username')
        exit(1)
    # Initialize the log
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = []
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - '+ '%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    # Set the track diretory, the server and the user name
    track_dir = sys.argv[1]
    server = sys.argv[2]
    user = sys.argv[3]
    # Validate the server URL
    if not server.startswith('http://') and not server.startswith('https://'):
        logging.critical("server_url must start with http:// or https://!")
        exit(1)
    # Standardize the ending of the server URL to contain /
    if server[-1] != '/':
        server = server + '/'
    # Get the list of renamable track recordings
    tracks = scan_dir(track_dir)
    scan_server(server, user, print_sortie)
