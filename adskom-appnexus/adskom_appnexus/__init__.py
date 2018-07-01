#!/usr/bin/env python3

from decimal import Decimal

import argparse
import copy
from datetime import datetime, timedelta
import time
import json
import os
import sys
import time
import glob
import csv
import logging
import backoff
import requests
import singer
import dateutil.parser
import adskom_appnexus.database as database
from contextlib import closing
from appnexus.client import client, services_list, AppNexusClient


import adskom_appnexus.schemas as schemas
import adskom_appnexus.configs as configs

LOGGER = singer.get_logger()

BASE_URL = 'https://api.appnexus.com'
PLATFORM_NAME = 'Appnexus India'

platform_id = None

configs = {}

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=lambda e: e.response is not None and 400 <= e.response.status_code < 500, # pylint: disable=line-too-long
                      factor=2)


# Function to get DSP Platform Id
def getPlatformId():
    
    global platform_id
    
    if (platform_id is None):
        LOGGER.info("Reading platform_id from Database")
        config = configs.get("db_credentials")
        db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
        
        data = db.get("SELECT hex(id) as platform_id FROM dsp_demand_side_platforms WHERE name = '{}' " .format(PLATFORM_NAME))
    
        if (data):
            platform_id = data.get('platform_id')
        
        
    return platform_id


# Function to get DSP Partner Brand Id by code
def getDSPPartnerBrandId(code):
    
    brand_id = ''
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
#     data = db.get("SELECT hex(id) as brand_id FROM dsp_partner_brands WHERE code = '{}' AND dsp_demand_side_platform_id = unhex('{}')" .format(code, platform_id))
    data = db.get("SELECT hex(id) as brand_id FROM dsp_partner_brands WHERE code = '{}' " .format(code))

    if (data):
        brand_id = data.get('brand_id')
        
        
    return brand_id


# Function to get DSP Partner Campaign Id by code
def getDSPPartnerCampaignId(code, brand_id):
    
    campaign_id = ''
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
    data = db.get("SELECT hex(id) as campaign_id FROM dsp_partner_campaigns WHERE code = '{}' AND dsp_partner_brand_id = unhex('{}')" .format(code, brand_id))

    if (data):
        campaign_id = data.get('campaign_id')
        
        
    return campaign_id


# Function to get DSP Partner Flight Id by code
def getDSPPartnerFlightId(code, campaign_id):
    
    flight_id = ''
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
    data = db.get("SELECT hex(id) as flight_id FROM dsp_partner_flights WHERE code = '{}' AND dsp_partner_campaign_id = unhex('{}')" .format(code, campaign_id))

    if (data):
        flight_id = data.get('flight_id')
        
    return flight_id

# Function to get DSP Partner Creative Id by code
def getDSPPartnerCreativeId(code):
    
    creative_id = ''
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
    data = db.get("SELECT hex(id) as creative_id FROM dsp_partner_creatives WHERE code = '{}'" .format(code))

    if (data):
        creative_id = data.get('creative_id')
        
    return creative_id


# Function to insert record in dsp_partner_brands
def insert_dsp_partner_brands(data):
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
        
    code = data.get('code')
    name = data.get('name', '')
        
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
#     data = db.query("SELECT * FROM dsp_partner_brands WHERE code = '{}' AND dsp_demand_side_platform_id = unhex('{}')" .format(code, platform_id))
    data = db.query("SELECT * FROM dsp_partner_brands WHERE code = '{}'" .format(code))
    
    if (data):
        LOGGER.info("Updating account_id : {} ".format(code))

        statement = "UPDATE dsp_partner_brands set name = %s, updated_at = now() WHERE code = '{}'".format(code)
        db.execute(statement, name)
        
    else:
        LOGGER.info("Inserting account_id : {} ".format(code))
        statement = "INSERT INTO dsp_partner_brands (name,code,dsp_demand_side_platform_id,id,created_at,updated_at) VALUES (%s,'{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format( code, platform_id)
        db.execute(statement, name)
    
    return True


# Function to insert campaign in dsp_partner_campaigns & dsp_partner_campaign_demand_side_platforms

def insert_dsp_partner_campaigns(data):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
            
    code = str(data.get('code'))
    name = str(data.get('name', ''))
    advertiser_code = data.get('advertiser_code')
    
#     Get Partner Brand Id
    brand_id = getDSPPartnerBrandId(advertiser_code)
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
    data = db.query("SELECT * FROM dsp_partner_campaigns WHERE code = '{}' AND dsp_partner_brand_id = unhex('{}')" .format(code, brand_id))

    if (data):
        LOGGER.info("Updating Campaign for code : {} ".format(code))

        statement = "UPDATE dsp_partner_campaigns set name = %s, updated_at = now() WHERE code = '{}'  AND dsp_partner_brand_id = unhex('{}')".format( code, brand_id)
        db.execute(statement, name)
        
    else:
        LOGGER.info("Inserting Campaign for code : {} ".format(code))
#         Insert campaign in dsp_partner_campaigns
        statement = "INSERT INTO dsp_partner_campaigns (name,code,dsp_partner_brand_id,id,created_at,updated_at) VALUES (%s,'{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format(code, brand_id)
        db.execute(statement, name)
        
        
        campaign_id = getDSPPartnerCampaignId(code, brand_id)
#         Insert campaign in dsp_partner_campaign_demand_side_platforms
        statement = "INSERT INTO dsp_partner_campaign_demand_side_platforms (dsp_partner_campaign_id,dsp_demand_side_platform_id) VALUES (unhex('{}'),unhex('{}'))".format(campaign_id, platform_id)
        db.execute(statement)
    
    return True



# Function to insert flight in dsp_partner_flights

def insert_dsp_partner_flights(data):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
            
    code = data.get('code')
    name = data.get('name', '')
    campaign_code = data.get('campaign_code')
    advertiser_code = data.get('advertiser_code')
    
#     Get Partner Brand Id
    brand_id = getDSPPartnerBrandId(advertiser_code)
#     Get Partner Campaign Id
    campaign_id = getDSPPartnerCampaignId(campaign_code, brand_id)
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
    data = db.query("SELECT * FROM dsp_partner_flights WHERE code = '{}' AND dsp_partner_campaign_id = unhex('{}')" .format(code, campaign_id))

    if (data):
        LOGGER.info("Updating Flight for code : {} ".format(code))

        statement = "UPDATE dsp_partner_flights set name = %s, updated_at = now() WHERE code = '{}'  AND dsp_partner_campaign_id = unhex('{}')".format( code, campaign_id)
        db.execute(statement, name)
        
    else:
        LOGGER.info("Inserting Flight for code : {} ".format(code))
#         Insert Flight in dsp_partner_flights
        statement = "INSERT INTO dsp_partner_flights (name,code,dsp_partner_campaign_id,id,created_at,updated_at) VALUES (%s,'{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format(code, campaign_id)
        db.execute(statement, name)
    
    return True



# Function to insert creatives in insert_dsp_partner_creatives

def insert_dsp_partner_creatives(data):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
            
    code = data.get('code')
    name = data.get('name', '')
    size = data.get('size', '')

    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
    data = db.query("SELECT * FROM dsp_partner_creatives WHERE code = '{}'" .format(code))

    if (data):
        LOGGER.info("Updating Creative for code : {} ".format(code))

        statement = "UPDATE dsp_partner_creatives set name = %s, size = '{}', updated_at = now() WHERE code = '{}'".format( size, code)
        db.execute(statement, name)
        
    else:
        LOGGER.info("Inserting Creative for code : {} ".format(code))
#         Insert Flight in dsp_partner_flights
        statement = "INSERT INTO dsp_partner_creatives (name,size,code,id,created_at,updated_at) VALUES (%s,'{}','{}',unhex(replace(uuid(),'-','')),now(), now())".format( size, code)
        db.execute(statement, name)
    
    return True


# Function to insert campaign performace into fact_platform_campaigns

def insert_fact_platform_campaigns(data):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    campaign_code = data.get('campaign_code')
    advertiser_code = data.get('advertiser_code')
    flight_code = data.get('flight_code')
    creative_code = data.get('creative_code')
    
#     Get Partner Brand Id
    brand_id = getDSPPartnerBrandId(advertiser_code)
#     Get Partner Campaign Id
    campaign_id = getDSPPartnerCampaignId(campaign_code, brand_id)
#     Get Partner Flight Id
    flight_id = getDSPPartnerFlightId(flight_code, campaign_id)
#     Get Partner Creative Id
    creative_id = getDSPPartnerCreativeId(creative_code)
    
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
    
    campaign_date = str(datetime.strptime( data.get('campaign_date'),'%Y-%m-%d %H:%M').date())
    campaign_timestamp = str(datetime.strptime( data.get('campaign_date'),'%Y-%m-%d %H:%M').timestamp())
    campaign_action_hour = str(datetime.strptime( data.get('campaign_date'),'%Y-%m-%d %H:%M').hour)
#     campaign_action_hour = str(data.get('action_hour'))
#     print("ACTION HOUR ::: {}".format(campaign_action_hour))
    
    impressions = data.get('impressions', '')
    clicks = data.get('clicks', '')
    last_view = data.get('last_view','')
    last_click = data.get('last_click','')
    spend = data.get('spend', '')
    currency = data.get('currency', '')
    
    
    #     check if already exist then update it else insert
    data = db.query("SELECT * FROM fact_platform_campaigns WHERE unix_timestamp = '{}' AND dsp_partner_flight_id = unhex('{}') AND dsp_partner_creative_id = unhex('{}') AND dsp_demand_side_platform_id = unhex('{}')" .format(campaign_timestamp, flight_id, creative_id, platform_id))

    if (data):

        LOGGER.info("Updating Campaign Performace for campaign_id : {} and campaign_date = {}".format(campaign_id, campaign_date))
        statement = "UPDATE fact_platform_campaigns set impressions = '{}', clicks = '{}', last_view = '{}' , last_click = '{}', spend = '{}', currency = '{}'  WHERE dsp_partner_brand_id = unhex('{}') AND dsp_partner_campaign_id = unhex('{}') AND dsp_partner_flight_id = unhex('{}') AND dsp_partner_creative_id = unhex('{}') AND dsp_demand_side_platform_id = unhex('{}') AND unix_timestamp = '{}'".format(impressions, clicks, last_view, last_click, spend, currency, brand_id, campaign_id, flight_id, creative_id, platform_id, campaign_timestamp)
        db.execute(statement)
        
    else:
        
        LOGGER.info("Inserting Campaign Performace for campaign_id : {} and campaign_date = {}".format(campaign_id, campaign_date))
        statement = "INSERT INTO fact_platform_campaigns (unix_timestamp,action_date,action_hour,impressions,clicks,last_view,last_click,spend,currency,dsp_partner_brand_id,dsp_partner_campaign_id,dsp_partner_flight_id,dsp_partner_creative_id,dsp_demand_side_platform_id) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}',unhex('{}'),unhex('{}'),unhex('{}'),unhex('{}'),unhex('{}'))".format(campaign_timestamp, campaign_date, campaign_action_hour, impressions, clicks, last_view, last_click, spend, currency, brand_id, campaign_id, flight_id, creative_id, platform_id)
#         LOGGER.info("Insert Statement : {}".format(statement))
        db.execute(statement)
        
    return True


def insert_partner_flights():
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    platform_id = getPlatformId()
    
    LOGGER.info("Inserting Partner Flights")
    
    statement = "TRUNCATE table dim_partner_flights"
    db.execute(statement)
    
    statement = "INSERT INTO dim_partner_flights (dsp_partner_flight_id, dsp_partner_flight_name, dsp_partner_campaign_id, dsp_partner_campaign_name, dsp_partner_brand_id, dsp_partner_brand_name, dsp_demand_side_platform_id, dsp_demand_side_platform_name) (SELECT f.id, f.NAME, c.id, c.NAME, b.id, b.NAME, d.id, d.NAME FROM dsp_partner_flights f LEFT JOIN dsp_partner_campaigns c ON f.dsp_partner_campaign_id = c.id LEFT JOIN dsp_partner_brands b ON c.dsp_partner_brand_id = b.id LEFT JOIN dsp_partner_campaign_demand_side_platforms cd ON c.id = cd.dsp_partner_campaign_id LEFT JOIN dsp_demand_side_platforms d ON cd.dsp_demand_side_platform_id = d.id) "
    db.execute(statement)
    
    return True


def insert_partner_creatives():
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    platform_id = getPlatformId()
    
    LOGGER.info("Inserting Partner Creative")
    
    statement = "TRUNCATE table dim_partner_creatives"
    db.execute(statement)
    
    statement = "INSERT into dim_partner_creatives (id, code, name, size) (SELECT c.id, c.code, c.name, c.size FROM dsp_partner_creatives c)"
    db.execute(statement)
    
    return True


def parse_reports():
#     print("INSERTING DATA")
#     Parse attachments downloaded from email
    config = configs.get("api_credentials")
    temp_folder = config.get('download_folder')
    attachment_folder = "{}/reports".format(temp_folder)
    
    attachments = glob.glob("{}/*.csv".format(attachment_folder))
    report_inserted = False
    
    for attachment in attachments:
        
        LOGGER.info("Parsing attachment : {}".format(attachment))
        
        with open(attachment, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
#         LOGGER.info(rows)
#         Parse each rows
            count = 0
            for row in rows:
                count += 1
                if(count == 1):
                    continue  # First row is header
                
        #           If row length is greater than 1
                if len(row) < 11:
                    LOGGER.info("Rows column size is not correct. Total Rows : {}".format(len(row)))
                    continue
                
                LOGGER.info("Row :{} Data : {}".format(count,row))
                
        #           1) Populate partner brands table (dsp_partner_brands) 
                advertiser = row[1]
                LOGGER.info("Advertiser : {}".format(advertiser))
                temp = advertiser.split("__")
                if len(temp) == 2:
                    data = {
                        'name': str(temp[1]),
                        'code': str(temp[0])
                    }
                else :
                    LOGGER.info("Advertiser is not in correct format : {}".format(advertiser))
                    continue
                advertiser_code = data['code']
                insert_dsp_partner_brands(data)
              
        #           2) Populate partner campaigns table (dsp_partner_campaigns)
        #           5) Populate partner campaign demand side platform (dsp_partner_campaign_demand_side_platforms)
                campaign = row[2]
                LOGGER.info("Campaign : {}".format(campaign))
                temp = campaign.split("_")
                
                if len(temp) == 3:
                    temp = campaign.split("__")
#                     print("CAMPAIGN :::: CODE >> {} NAME >> {}".format(temp[0],temp[1]))
                    data = {
                        'name': str(temp[1]),
                        'code': str(temp[0]),
                        'advertiser_code': advertiser_code
                    }      
                elif len(temp) == 2:
                    data = {
                        'name': str(temp[1]),
                        'code': str(temp[0]),
                        'advertiser_code': advertiser_code
                    }
                else :
                    LOGGER.info("Campaign is not in correct format : {}".format(campaign))
                    continue
#                 print("CAMPAIGN DATA:::: {}".format(data))
                campaign_code = data['code']
                insert_dsp_partner_campaigns(data)
                
                
        #           3) Populate partner flights table (dsp_partner_flights)
                flight = row[3]
                LOGGER.info("Flight : {}".format(flight))
                temp = flight.split("__")
                if len(temp) == 2:
                    data = {
                        'name': str(temp[1]),
                        'code': str(temp[0]),
                        'campaign_code': campaign_code,
                        'advertiser_code': advertiser_code
                    }
                else :
                    LOGGER.info("Flight is not in correct format : {}".format(flight))
                    continue
                
                flight_code = data['code']
                insert_dsp_partner_flights(data)
        
        #           4) Populate partner creatives table (dsp_partner_creatives)
                creative = row[4]
                LOGGER.info("Creative : {}".format(creative))
                size = "{}".format(row[5])
                temp = creative.split("__")
                if len(temp) == 2:
                    data = {
                        'code': str(temp[0]),
                        'name': str(temp[1]),
                        'size': size
                    }
                else :
                    LOGGER.info("Creative is not in correct format : {}".format(creative))
                    continue
                
                creative_code = data['code']
                insert_dsp_partner_creatives(data)
                
        #           6) Save campaign report to database (fact_platform_campaigns)
                campaign_date = "{}".format(row[0])
                data = {
                    'campaign_date': str(campaign_date),
        #             'action_hour': str(row[23]),
                    'advertiser_code': advertiser_code,
                    'campaign_code': campaign_code,
                    'flight_code': flight_code,
                    'creative_code': creative_code,
                    'impressions': str(row[6]),
                    'clicks': str(row[7]),
                    'last_view': str(row[8]),
                    'last_click': str(row[9]),
                    'spend': str(row[10]),
                    'currency': str(row[11])
                }
                LOGGER.info("Fact Platform Campaign : {}".format(data))
                insert_fact_platform_campaigns(data)
                
                report_inserted = True
                    
    #         Remove attachment
            os.remove(attachment)
            
            
#   7) Populate our Dim tables (dim_partner_flights) & Dim Partner Creatives (dim_partner_creatives)
    if(report_inserted):
#         Regenerate dim flight table
        insert_partner_flights() #error in query 
        insert_partner_creatives()
        
        


def get_report(start_date  = None, end_date = None):

    config = configs.get("api_credentials")
    today = datetime.today()
    temp_folder = config.get('download_folder')
    resume_file = "{}/resume.txt".format(temp_folder)
    report_folder = "{}/reports".format(temp_folder)
    timezone = config.get('timezone')
    
        
    report_id = None
    
    if(end_date is None):
        tomorrow = today + timedelta(1)
        end_date = tomorrow.strftime('%Y-%m-%d')
    
    yesterday = today - timedelta(1)
    
    if(start_date  is None):
        start_date = yesterday.strftime('%Y-%m-%d')
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
    }
    
    LOGGER.info("Appnexus India API Date Range :: {}".format(params))
    
    
#     Connect to the API    
    client = AppNexusClient()
    client.connect(config.get('username'), config.get('password'))
    
    #Request to generate report
    params = {
        "report":
        {
            "report_type":"network_analytics",
            "columns":[
                "hour",
                "advertiser_name",
                "line_item_name",
                "campaign_name",
                "creative_name",
                "size",
                "imps",
                "clicks",
                "post_view_convs",
                "post_click_convs",
                "cost",
                "advertiser_currency"
            ],
            "timezone":timezone,
#             "report_interval":"last_48_hours",
            "start_date" : start_date,
            "end_date" : end_date,
            "format":"csv"
        }
    }
    response = client.create('report', params)    
#     print("REPORT REQUEST RETURN ::: {}".format(response));
    
    if response.get('status') == 'OK':
        report_id = response.get('report_id', None)
    else:
        LOGGER.error('RESPONSE ERROR :: {}'.format(response))
        raise RuntimeError
    
    print("REPORT ID ::: {}".format(report_id));

#     Get report status, retry for 5 times if execution_status is not getting ready 
#     if "execution_status": "ready" then get url for download report in  "url": "report-download?id=3876d8ed34a14921f95793a1d618d3a9" 
    valid_response = False
    limit = 5
    count = 0
    download_url = None
    report_object = None
    while not valid_response:
        response = client.get('report', id=report_id)  
#         print("REPORT REQUEST RETURN ::: {}".format(response));
        count += 1
        if (response.get('status') == 'OK' and response.get('execution_status') == 'ready'):
#             report_object = response.get('report')
            download_url = response.get('report').get('url')
            valid_response = True
        elif count == limit:
            valid_response = True
        else:
            time.sleep(4)
        
      
#     print("REPORT REQUEST RETURN ::: {}".format(report_object));
    print("REPORT DOWNLOAD URL ::: {}".format(download_url))

#     Download Report url = report-download?id=07bd4e5ae85ac2200955d4bfad6a4acc
#     response = client.get('report-download', id=report_id, raw=True)
#     print("RESPONSE ::: {}".format(response))
    data=None
    headers = dict(Authorization=client.token)
    url = client._prepare_uri('report-download', id=report_id)
    print('\n URI ::: {}'.format(url))
    
    if 'reports' not in os.listdir(temp_folder):
        os.mkdir(report_folder)
        
    file_path = "{}/report_{}.csv".format(report_folder,tomorrow.strftime('%Y-%m-%d %H:%M:%S'))
    with closing(requests.get(url, stream=True, headers=headers)) as r:
        with open(file_path, 'wb') as fp:
            fp.write(r.content)
        

# Function to verify config file


def validate_config(config):
    required_keys = ['username', 'password', 'download_folder', 'timezone', "host", "user", "password", "database"]
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



#Function to sync account, campaigns & reports from Appnexus API

def do_sync(args):
    LOGGER.info("Starting sync.")
    
    global configs
    
    configs = load_config(args.config)
    config = configs.get("api_credentials")
    
    campaign_sync_start_date = None if args.start_date is None else args.start_date
    campaign_sync_end_date = None if args.start_date is None else args.end_date
    
#     Generate Reports
    get_report(campaign_sync_start_date, campaign_sync_end_date)
    
#     Parse attachments
    parse_reports()
    
    


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
