#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
utils.py

Helper methods.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import requests
import urlparse
import datetime
import pandas as pd
import os


def download_file(download_link, filename, directory):
    """Download a file to a directory.

    Args:
        download_link (str): Link of the file to download.
        filename (str): Name of the file to be downloaded.
        directory (str): Directory where the filename will be downloaded.
    """
    # create the directory if is not there
    if not os.path.isdir(directory):
        os.mkdir(directory)

    path = os.path.join(directory, filename)

    with open(path, 'wb') as handle:
        response = requests.get(download_link, stream=True)

        if not response.ok:
            # something is wrong
            print(response, "link:", download_link, "filename:", filename)

        else:
            for block in response.iter_content(1024):
                handle.write(block)

            print(filename, "was downloaded in", directory)


def not_file_link(link):
    """Check that a link is not a file.

    Args:
        link (str): Link that could be a file or not.

    Returns:
        bool: True if a link is not file.
    """
    possible_file_format = link.split(".")[-1]
    return (possible_file_format != "xls" and
            possible_file_format != "xlsx" and
            possible_file_format != "zip" and
            possible_file_format != "pps" and
            possible_file_format != "ppsx" and
            possible_file_format != "rar" and
            possible_file_format != "pdf")


def get_base_url(url):
    """Return the base url of an absolute url (the host)."""
    parsed_url = urlparse.urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.hostname


def parse_pandas_date(date):
    """Convert a pandas date object in a datetime.datetime one.

    Frequencies above the day, will use 1 when the date field doesn't apply.

    Args:
        date (pandas date obj): A date to be parsed into datetime.datetime.

    Returns:
        datetime.datetime: Parsed date.
    """

    if date.freq == "Y":
        return datetime.datetime(date.year, 1, 1)
    elif date.freq == "Q" or date.freq == "M":
        return datetime.datetime(date.year, date.month, 1)
    else:
        return datetime.datetime(date.year, date.month, date.day)


def parse_context(context):
    """Parse a string context into a dictionary.

    Args:
        context (str): A context string to be parsed like
            "Total 1:C4-F4;Total 2:D5-F5,H5-J5"

    Returns:
        dict: A dict with parsed context like
            {"Total 1": ["C4-F4],
             "Total 2": ["D5-F5", "H5-J5"]}
    """
    if not context or pd.isnull(context):
        return None

    items = [(item.split(":")[0], item.split(":")[1])
             for item in context.split(";")]

    return {item[0].encode("utf-8"): item[1].split(",") for item in items}
