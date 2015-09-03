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

import utils
from xlseries import XlSeries


def scrape_series(path_excel, headers_coord, data_starts, frequency,
                  time_header_coord, context=None, ws_name=None):
    """Scrape time series from excel file into a DataFrame object."""

    # xlseries decode ws_name, and this come already decoded from openpyxl
    # so it has to be encoded to pass it to xlseries
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
        "context": utils.parse_context(context)
    }

    return xl.get_data_frames(params, ws_name)


def add_series_to_tbl(table, source_name, categories, description, df_series):
    """Iterate a dataframe adding each row of date to a database table."""

    fields = df_series.columns

    for row in df_series.iterrows():
        date = utils.parse_pandas_date(row[0])

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


def update_table(table, source_file, source_dir, use_cache=False):
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
            utils.download_file(row[1]["download_link"], row[1]["filename"],
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
            add_series_to_tbl(table, source_name,
                              row[1]["categories"], row[1]["description"], df)


def main(sources=None,
         database_url='sqlite:///2-base_de_datos/latam_series.db',
         use_cache=True):
    sources = sources or ["1-ejemplos"]

    # make a connection with the database
    db = dataset.connect(database_url)

    # each source (INDEC, INE..) would be a separate table in the db
    for source in sources:
        table = db[source]
        update_table(table, source + ".xlsx", source, use_cache)


if __name__ == '__main__':
    main()
