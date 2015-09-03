#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xl_links_scraper.py

Base class for scraping excel file links (or any other kinds of links).
"""

from __future__ import unicode_literals
from __future__ import print_function
import os
import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup
import urlparse
import time
import json

import utils


class WebLinksScraper():

    def __init__(self, links_to_visit=None, visited_links=None,
                 target_links=None):
        """Load previous state into the scraper.

        Args:
            links_to_visit (str): Path to a json file with links to visit.
            visited_links (str): Path to a json file with visited links.
            target_links (str): Path to a json file with scraped links.
        """
        self.links_to_visit = None
        self.visited_links = None
        self.target_links = None

        if links_to_visit:
            with open(links_to_visit, "wb") as f:
                self.links_to_visit = json.load(links_to_visit, f)

        if visited_links:
            with open(visited_links, "wb") as f:
                self.visited_links = json.load(visited_links, f)

        if target_links:
            with open(target_links, "wb") as f:
                self.target_links = json.load(target_links, f)

    # PUBLIC
    def scrape(self, base_url, targets, to_visit_targets=None):
        """Look recursively for all the links in a webiste including substring.

        Go through all the links in the base_url storing the ones that have a
        substring from targets and recursively go through all the links that
        have a substring from to_visit_targets doing the same search.

        Args:
            base_url (str): URL where the search starts.
            targets (list): Strings we are looking in a link to store it.
            to_visit_targets (list): Strings we are looking in a link to visit.

        Side effects:
            Add and remove links to self.links_to_visit
            Add links to self.target_links
        """
        # start timer
        start = time.time()

        # scrape target_links and links_to_visit from the base_url
        self._scrape_links(base_url, targets, to_visit_targets)

        # take a link_to_visit and repeat the operation, until they're all done
        visited = 1
        while len(self.links_to_visit) > 0:
            link = self.links_to_visit.pop()

            # a link is stored as a tuple: (description, link)
            self._scrape_links(link, targets, to_visit_targets)
            self.visited_links.append(link)
            visited += 1

            # print a statement keeping track of the progress
            status = " ".join(["Scraped:", str(len(self.target_links)),
                               "To visit:", str(len(self.links_to_visit)),
                               "Visited:", str(visited)])
            print(status, end="\r" * len(status))

        # calculate how many minutes took
        elasped = time.time() - start
        print("Finished in", elasped / 60.0, "minutes")

    def download_all(self, directory):
        """Download all the target_links into a directory.

        Args:
            directory (str): Path to a directory to download files.
        """
        # start timer
        start = time.time()

        for index, link in enumerate(self.target_links):
            download_link = link[1]
            filename = download_link.split("/")[-1]
            path = os.path.join(directory, filename)

            # don't download the same file twice
            if not os.path.isfile(path):
                utils.download_file(download_link, filename, directory)

            # print a statement with the progress of the download
            status = " ".join(["Downloaded", str(index + 1), "of",
                               str(len(self.target_links)), "files."])
            print(status, end="\r" * len(status))

        # calculate how many minutes took
        elasped = time.time() - start
        print("Finished in", elasped / 60.0, "minutes")

    def save_to_excel(self, output_name="output.xlsx"):
        """Save the scraped links in an excel file.

        Args:
            output_name (str): Filename for the excel file.
        """

        wb = Workbook()
        ws = wb.active
        ws.title = "download_links"

        # write field names in the spreadsheet
        ws.append(("description", "download_link", "filename"))

        # add all the links to the spreadsheet
        for link in self.target_links:
            description = link[0].strip()
            download_link = link[1]
            filename = download_link.split("/")[-1].strip()

            ws.append((description, download_link, filename))

        wb.save(output_name)

    def save_state(self, name="source_x", directory="2-base_de_datos"):
        """Save current visited, scraped and to_visit links.

        Args:
            name (str): Name of the source being scraped
            directory (str): Directory where json files will be saved.

        Side effect:
            Creates 3 json files with current scraped, visited and yet to_visit
                links.
        """

        filename = "target_links_" + name + ".json"
        file_path = os.path.join(directory, filename)
        with open(file_path, "wb") as f:
            json.dump(self.target_links, f)

        filename = "visited_links_" + name + ".json"
        file_path = os.path.join(directory, filename)
        with open(file_path, "wb") as f:
            json.dump(self.visited_links, f)

        filename = "links_to_visit_" + name + ".json"
        file_path = os.path.join(directory, filename)
        with open(file_path, "wb") as f:
            json.dump(self.links_to_visit, f)

    # PRIVATE
    def _scrape_links(self, url, targets, to_visit_targets):
        """Look for all the links in a page that includes a substring.

        Go through all the links in the page storing the ones that have a
        substring from targets and storing the ones that have a substring from
        to_visit_targets doing the same search.

        Args:
            url (str): URL of the page to scrape.
            targets (list): Strings we are looking in a link to store it.
            to_visit_targets (list): Strings we are looking in a link to visit.

        Side effects:
            Add and remove links to self.links_to_visit
            Add links to self.target_links
        """

        # we'll need the host url of the site to build absolute links
        base_url = utils.get_base_url(url)

        resp = requests.get(url)
        bs = BeautifulSoup(resp.text)

        all_links = [(a.get_text(),
                      urlparse.urljoin(base_url, a.attrs.get('href')))
                     for a in bs.find_all("a") if a.attrs.get('href')]

        for tuple_link in all_links:
            link = tuple_link[1]

            if self._is_a_target_link(link, targets):
                self.target_links.append(tuple_link)

            elif self._is_a_link_to_visit(link, to_visit_targets):
                self.links_to_visit.append(link)

    def _is_a_target_link(self, link, targets):
        """Return True if the link is one of the scraping targets."""
        for target in targets:
            if target in link:
                return True
        return False

    def _is_a_link_to_visit(self, link, to_visit_targets):
        """Return True if the link has to be visited."""

        not_visited = link not in self.visited_links
        not_already_queued = link not in self.links_to_visit
        not_a_file = utils.not_file_link(link)

        if not_visited and not_a_file and not_already_queued:
            for to_visit_target in to_visit_targets:
                if to_visit_target in link:
                    return True

        return False
