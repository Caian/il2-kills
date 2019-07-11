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

import sys, requests, logging

def scan_server(server, user):
    """"""

    if not server.startswith('http://') and not server.startswith('https://'):
        logging.critical("server_url must start with http:// or https://!")
        exit(1)

    if server[-1] != '/':
        server = server + '/'

    url = '%ssorties/%s/' % (server, user)
    logging.info("User sorties URL is '%s'.", url)

    response = requests.get(url)
    html = response.text

    text_tour = '<a href="?tour='
    text_ctour = '">'
    text_sortie = 'href="/en/sortie/'
    text_cell = '<div class="cell">'
    text_ca = '</a>'
    text_cdiv = '</div>'

    last_tour = -1

    logging.info("Listing tours...")

    tours = []

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

    logging.info("Tours: %s.", ', '.join(tours))

    for tour in tours:

        page = 1

        while True:

            logging.info("Fetching tour %s, page %d...", tour, page)

            url = '%ssorties/%s/?tour=%s&page=%d' % (server, user, tour, page)
            logging.info("Tour URL is '%s'.", url)

            response = requests.get(url)
            html = response.text

            if response.status_code == 404:
                logging.info("URL not found, ending tour.")
                break

            elif response.status_code != 200:
                logging.critical("Server returned error %d!", response.status_code)
                exit(1)

            last_sortie = -1
            n_sortie = 1

            while True:

                sortie = html.find(text_sortie, last_sortie + 1)
                if sortie < 0:
                    break

                ca = html.find(text_ca, sortie + 1)
                if ca < 0:
                    logging.critical("Missing '%s' after '%s'!", text_sortie, text_ca)
                    exit(1)

                last_cell = sortie
                line = []

                while True:

                    cell = html.find(text_cell, last_cell + 1)
                    if cell < 0 or cell > ca:
                        break

                    cdiv = html.find(text_cdiv, cell + 1)
                    if cdiv < 0:
                        logging.critical("Missing '%s' after '%s'!", text_cell, text_cdiv)
                        exit(1)

                    line.append(html[cell+len(text_cell):cdiv])
                    last_cell = cell

                print(' '.join(line))
                n_sortie = n_sortie + 1
                last_sortie = ca

            page = page + 1


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('USAGE: ./il2-kills.py server_url usercode/username')
        exit(1)

    server = sys.argv[1]
    user = sys.argv[2]

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = []
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - '+ '%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    scan_server(server, user)
