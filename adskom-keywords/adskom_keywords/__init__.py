#!/usr/bin/env python3

from decimal import Decimal

import argparse
import copy
from datetime import datetime, timedelta
import time
import json
import os
import sys
# import string
# from threading import Thread
import threading
import time
import glob
import csv
import codecs
import logging
import backoff
import requests
import singer
import dateutil.parser
import adskom_keywords.database as database

LOGGER = singer.get_logger()

#create as many threads as you want
thread_count = 5

configs = {}

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=lambda e: e.response is not None and 400 <= e.response.status_code < 500, # pylint: disable=line-too-long
                      factor=2)

def insert_kt_dim_sub_brands():
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    statement = "TRUNCATE table kt_dim_sub_brands"
    db.execute(statement)
    
    statement = "INSERT INTO kt_dim_sub_brands (sub_brand_id, brand_id, advertiser_id, sub_brand_name, brand_name, advertiser_name) (SELECT s.id, b.id, a.id, s.name, b.name, a.name, FROM dsp_sub_brands s INNER JOIN dsp_brands b ON s.brand_id = b.id INNER JOIN dsp_advertisers a ON b.advertiser_id = a.id ); "
    db.execute(statement)
    
    return True 

def insert_kt_dim_dpp_keyword_tags():
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    statement = "TRUNCATE table kt_dim_dpp_keyword_tags"
    db.execute(statement)
    
    statement = "INSERT INTO kt_dim_dpp_keyword_tags (keyword, keyword_type, sub_brand_id, keyword_tag_step_id, media_placement) (SELECT kt_s.keyword, kt.keyword_type, kt.sub_brand_id, kt_s.id, kt.media_placement FROM dsp_keyword_tag_steps kt_s INNER JOIN dsp_keyword_tags kt ON kt.id = kt_s.keyword_tag_id); "
    db.execute(statement)
    
    return True 

# Function to insert record in fact_keyword_steps
def insert_fact_keyword_steps(record):
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))

    unix_timestamp = int(record.get('unix_timestamp'))
    keyword_tag_step_id = str(record.get('keyword_tag_step_id'))
    sub_brand_id = str(record.get('sub_brand_id'))
    unique_count = int(record.get('unique_count'))

    data = db.query("SELECT * FROM fact_keyword_steps WHERE unix_timestamp = {} AND keyword_tag_step_id = unhex('{}') AND sub_brand_id = unhex('{}')" .format(unix_timestamp, keyword_tag_step_id, sub_brand_id))

    if (data):

#         LOGGER.info("Updating fact_keyword_steps : {} ".format(record))
        statement = "UPDATE fact_keyword_steps set unique_count = {} WHERE unix_timestamp = {} AND keyword_tag_step_id = unhex('{}') AND sub_brand_id = unhex('{}')".format(unique_count, unix_timestamp, keyword_tag_step_id, sub_brand_id)
        db.execute(statement)
        
    else:
#         LOGGER.info("Inserting fact_keyword_steps : {} ".format(record))
        statement = "INSERT INTO fact_keyword_steps (unix_timestamp,keyword_tag_step_id,sub_brand_id,unique_count) VALUES ({},unhex('{}'),unhex('{}'),{})".format( unix_timestamp,keyword_tag_step_id,sub_brand_id,unique_count)
        db.execute(statement)
    
    return True


# Function to insert record in fact_keyword_step_uniques
def insert_fact_keyword_step_uniques(record):
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))

    unix_timestamp = int(record.get('unix_timestamp'))
    keyword_tag_step_id = str(record.get('keyword_tag_step_id'))
    sub_brand_id = str(record.get('sub_brand_id'))
    unique_count = int(record.get('unique_count'))

    data = db.query("SELECT * FROM fact_keyword_step_uniques WHERE unix_timestamp = {} AND keyword_tag_step_id = unhex('{}') AND sub_brand_id = unhex('{}')" .format(unix_timestamp, keyword_tag_step_id, sub_brand_id))

    if (data):

#         LOGGER.info("Updating fact_keyword_steps : {} ".format(record))
        statement = "UPDATE fact_keyword_step_uniques set unique_count = {} WHERE unix_timestamp = {} AND keyword_tag_step_id = unhex('{}') AND sub_brand_id = unhex('{}')".format(unique_count, unix_timestamp, keyword_tag_step_id, sub_brand_id)
        db.execute(statement)
        
    else:
#         LOGGER.info("Inserting fact_keyword_steps : {} ".format(record))
        statement = "INSERT INTO fact_keyword_step_uniques (unix_timestamp,keyword_tag_step_id,sub_brand_id,unique_count) VALUES ({},unhex('{}'),unhex('{}'),{})".format( unix_timestamp,keyword_tag_step_id,sub_brand_id,unique_count)
        db.execute(statement)
    
    return True


def read_logs():
    config = configs.get("api_credentials")
    log_folder = config.get('log_folder')
    processing_limit = int(config.get('processing_limit'))
    processing_status = {}
#     report_inserted = 
    try:
    
        attachments = glob.glob("{}/*.csv".format(log_folder))
        report_inserted = False
        file_count = 0
        
        for attachment in attachments:
            
            LOGGER.info("Parsing attachment : {}".format(attachment))
            file_count += 1
            
            with open(attachment, 'r') as f:
#             with codecs.open(attachment,"rb","utf-16") as f:
#                 reader = csv.reader(f, delimiter='\t')
                reader = csv.reader((line.replace('\0','') for line in f), delimiter='\t')
                rows = list(reader)
    #         LOGGER.info(rows)
    #         Parse each rows
                count = 0
                for row in rows:
                    count += 1
                    LOGGER.info("Row :{} Data : {}".format(count,row))
                    #           If row length is greater than 1
                    if len(row) < 4:
                        LOGGER.info("Rows column size is not correct. Total Rows : {}".format(len(row)))
                        continue
                    
                    data = {}
#                     | row[0] == "NULL" | row[1] == "" | row[2] == ""| row[3] == ""
                    if(str(row[0]).isdigit() == False ):
                        continue
                    
                    
                    data['unix_timestamp'] = int(row[0])
                    data['keyword_tag_step_id'] = str(row[1])
                    data['sub_brand_id'] = str(row[2])
                    data['unique_count'] = int(row[3])
                    
                    data['keyword_tag_step_id'] = str.replace(data['keyword_tag_step_id'], '-', '')
                    data['sub_brand_id'] = str.replace(data['sub_brand_id'], '-', '')
                    
                    
    #                 status = insert_fact_keyword_steps(data);
                    
                    thread = threading.Thread(target=insert_fact_keyword_steps, args=(data,))
                    thread.start()
                    
                    if threading.active_count() == processing_limit:  # set maximum threads.
                        thread.join()
                    
                    tc = threading.active_count()
#                     LOGGER.info("Active Thread ::: {}".format(tc)) 
                           # number of alive threads.
                    
                    report_inserted = True
                temp = {}
                temp['fileName'] = attachment
                temp['total_rows'] = count
                processing_status[file_count] = temp
                        
#           Remove attachment
#           os.remove(attachment)

#            Rename file
            new_filename = "{}.uploaded".format(attachment)
            os.rename(attachment, new_filename)
    
        if(report_inserted):
#         Regenerate tag tables
            insert_kt_dim_dpp_keyword_tags() #error in query 
            insert_fact_keyword_steps()
            
    except Exception as e:
        LOGGER.info("Error: unable to start thread {}".format(e))

        
    return processing_status


def read_unique_logs():
    config = configs.get("api_credentials")
    log_folder = config.get('unique_log_folder')
    processing_limit = int(config.get('processing_limit'))
    processing_status = {}
#     report_inserted = 
    try:
    
        attachments = glob.glob("{}/*.csv".format(log_folder))
        report_inserted = False
        file_count = 0
        
        for attachment in attachments:
            
            LOGGER.info("Parsing attachment : {}".format(attachment))
            file_count += 1
            
            with open(attachment, 'r') as f:
                reader = csv.reader((line.replace('\0','') for line in f), delimiter='\t')
                rows = list(reader)
    #         LOGGER.info(rows)
    #         Parse each rows
                count = 0
                for row in rows:
                    count += 1
                    LOGGER.info("Row :{} Data : {}".format(count,row))
                    #           If row length is greater than 1
                    if len(row) < 4:
                        LOGGER.info("Rows column size is not correct. Total Rows : {}".format(len(row)))
                        continue
                    
                    data = {}
                    if(str(row[0]).isdigit() == False ):
                        continue
                    
                    data['unix_timestamp'] = int(row[0])
                    data['keyword_tag_step_id'] = str(row[1])
                    data['sub_brand_id'] = str(row[2])
                    data['unique_count'] = int(row[3])
                    
                    data['keyword_tag_step_id'] = str.replace(data['keyword_tag_step_id'], '-', '')
                    data['sub_brand_id'] = str.replace(data['sub_brand_id'], '-', '')
                    
    #                 status = insert_fact_keyword_steps(data);
                    
                    thread = threading.Thread(target=insert_fact_keyword_step_uniques, args=(data,))
                    thread.start()
                    
                    if threading.active_count() == processing_limit:  # set maximum threads.
                        thread.join()
                    
                    tc = threading.active_count()
#                     LOGGER.info("Active Thread ::: {}".format(tc)) 
                           # number of alive threads.
                    
                    report_inserted = True
                temp = {}
                temp['fileName'] = attachment
                temp['total_rows'] = count
                processing_status[file_count] = temp
                        
#           Remove attachment
#           os.remove(attachment)

#            Rename file
            new_filename = "{}.uploaded".format(attachment)
            os.rename(attachment, new_filename)
    
        if(report_inserted):
#         Regenerate tag tables
            insert_kt_dim_dpp_keyword_tags() #error in query 
            insert_fact_keyword_steps()
            
    except Exception as e:
        LOGGER.info("Error: unable to start thread {}".format(e))

        
    return processing_status
        



# Function to verify config file
def validate_config(config):
    required_keys = ['username', 'password', 'client_id', 'client_secret', "host", "user", "database"]
    missing_keys = []
    null_keys = []
    has_errors = False
 
    for required_key in required_keys:
        if required_key not in config:
            missing_keys.append(required_key)
 
        elif config.get(required_key) is None:
            null_keys.append(required_key)
 
    if missing_keys:
        LOGGER.fatal("Config is missing keys: {}"
                     .format(", ".join(missing_keys)))
        has_errors = True
 
    if null_keys:
        LOGGER.fatal("Config has null keys: {}"
                     .format(", ".join(null_keys)))
        has_errors = True
 
    if has_errors:
        raise RuntimeError


#Function to load external config file
def load_config(filename):
    config = {}

    try:
        with open(filename, 'r') as config_file:
            file_content = config_file.read()
            config = json.loads(file_content)
    except:
        LOGGER.fatal("Failed to decode config file. Is it valid json?")
        raise RuntimeError

#     validate_config(config)

    return config



#Function to sync account, campaigns & reports from Taboola API


def do_sync(args):
    LOGGER.info("Starting sync.")
    
    global configs
    
    configs = load_config(args.config)
    config = configs.get("api_credentials")
    
#     Read log files
    status = read_logs()
    LOGGER.info("Status ::: {}".format(status))
    
#     Read log files
    status = read_unique_logs()
    LOGGER.info("Status ::: {}".format(status))
     


def main_impl():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', help='Config file', required=True)
    parser.add_argument('-s', '--start_date', help='Sync start date : format YYYY-MM-DD')
    parser.add_argument('-e', '--end_date', help='Sync end date  : format YYYY-MM-DD')

    args = parser.parse_args()

    try:
        do_sync(args)
    except RuntimeError:
        LOGGER.fatal("Run failed.")
        exit(1)

def main():
    try:
        main_impl()
    except Exception as exc:
        LOGGER.critical(exc)
        raise exc


if __name__ == '__main__':
    main()
