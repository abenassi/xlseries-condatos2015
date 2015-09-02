#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
build_database.py

Build a time series database.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import dataset
import pandas as pd
import os
import requests
import datetime

from xlseries import XlSeries


def parse_pandas_date(date):

    if date.freq == "Y":
        return datetime.datetime(date.year, 1, 1)
    elif date.freq == "Q" or date.freq == "M":
        return datetime.datetime(date.year, date.month, 1)
    else:
        return datetime.datetime(date.year, date.month, date.day)


def parse_context(context):

    if not context or pd.isnull(context):
        return None

    items = [(item.split(":")[0], item.split(":")[1])
             for item in context.split(";")]

    return {item[0].encode("utf-8"): item[1].split(",") for item in items}


def download_file(download_link, filename, directory):
    """Download a file to a directory."""

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


def scrape_series(path_excel, headers_coord, data_starts, frequency,
                  time_header_coord, context=None, ws_name=None):

    if not ws_name or pd.isnull(ws_name):
        ws_name = None
    else:
        ws_name = ws_name.encode("utf-8")

    xl = XlSeries(path_excel)
    params = {
        "headers_coord": headers_coord.split(","),
        "frequency": frequency.split(","),
        "time_header_coord": time_header_coord.split(","),
        "data_starts": data_starts,
        "context": parse_context(context)
    }

    # print(ws_name)

    return xl.get_data_frames(params, ws_name)


def add_series_to_db(table, source_name, categories, description, df_series):

    fields = df_series.columns

    for row in df_series.iterrows():
        date = parse_pandas_date(row[0])

        for field in fields:
            value = row[1][field]

            new_entry = {
                "source": source_name,
                "categories": categories,
                "description": description,
                "name": field,
                "date": date,
                "value": value,
                "frequency": df_series.index.freq
            }

            table.upsert(new_entry, ["name", "date", "frequency"])


def update_database(table, source_file, source_dir, use_cache=False):
    """Update a time series database downloading and scraping excel files.

    Args:
        table (dataset.Database table): A table in the database used.
        source_file (str): Path to an xlsx file with the list of excel files to
            download and their parameters to extract data with xlseries.
        source_dir (str): Path to a cache directory where excel files will be
            downloaded.
        use_cache (bool): When True will use the files already downloaded, when
            False will re-download the files.
    """

    # use pandas to read the excel where we store the metadata of the files
    df_source = pd.read_excel(source_file)

    # scrape every excel and add its time series to the database
    for row in df_source.iterrows():
        if not use_cache:
            download_file(row[1]["download_link"], row[1]["filename"],
                          source_dir)

        path_excel = os.path.join(source_dir, row[1]["filename"])

        # here is where the magic really happens!
        df_series = scrape_series(path_excel,
                                  row[1]["headers_coord"],
                                  row[1]["data_starts"],
                                  row[1]["frequency"],
                                  row[1]["time_header_coord"],
                                  row[1]["context"],
                                  row[1]["ws_name"])

        source_name = source_file.replace(".xlsx", "")

        if not type(df_series) == list:
            df_series = [df_series]

        print(sum(map(len, df_series)), "series were scraped from",
              row[1]["filename"])

        for df in df_series:
            add_series_to_db(table, source_name,
                             row[1]["categories"], row[1]["description"], df)


def main():
    SOURCES = ["ejemplos"]
    DATABASE_URL = 'sqlite:///latam_series.db'

    # make a connection with the database
    db = dataset.connect(DATABASE_URL)
    # db.begin()

    for source in SOURCES:
        table = db[source]
        update_database(table, source + ".xlsx", source, True)

    # db.commit()


if __name__ == '__main__':
    main()
