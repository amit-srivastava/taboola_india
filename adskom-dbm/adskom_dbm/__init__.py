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
import adskom_dbm.database as database
import adskom_dbm.email as email

import adskom_dbm.schemas as schemas
import adskom_dbm.configs as configs

LOGGER = singer.get_logger()

PLATFORM_NAME = 'DBM India'

platform_id = None

configs = {}

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=lambda e: e.response is not None and 400 <= e.response.status_code < 500, # pylint: disable=line-too-long
                      factor=2)



# Function to get Taboola DSP Platform Id
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

        statement = "UPDATE dsp_partner_brands set name = %s, updated_at = now() WHERE code = '{}'".format( code )
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
            
    code = data.get('code')
    name = data.get('name', '')
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
        statement = "INSERT INTO dsp_partner_campaigns (name,code,dsp_partner_brand_id,id,created_at,updated_at) VALUES (%s,'{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format( code, brand_id)
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

        statement = "UPDATE dsp_partner_flights set name = %s, updated_at = now() WHERE code = '{}'  AND dsp_partner_campaign_id = unhex('{}')".format(code, campaign_id)
        db.execute(statement, name)
        
    else:
        LOGGER.info("Inserting Flight for code : {} ".format(code))
#         Insert Flight in dsp_partner_flights
        statement = "INSERT INTO dsp_partner_flights (name,code,dsp_partner_campaign_id,id,created_at,updated_at) VALUES (%s,'{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format( code, campaign_id)
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
        statement = "INSERT INTO dsp_partner_creatives (name,size,code,id,created_at,updated_at) VALUES (%s,'{}','{}',unhex(replace(uuid(),'-','')),now(), now())".format(size, code)
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
    
    
    campaign_date = str(datetime.strptime( data.get('campaign_date'),'%Y/%m/%d %H:%M:%S').date())
    campaign_timestamp = str(datetime.strptime( data.get('campaign_date'),'%Y/%m/%d %H:%M:%S').timestamp())
#     campaign_action_hour = str(datetime.strptime( data.get('campaign_date'),'%Y/%m/%d %H:%M:%S').time())
    campaign_action_hour = str(data.get('action_hour'))

    
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
        statement = "INSERT INTO fact_platform_campaigns (unix_timestamp,action_date,action_hour,impressions,clicks,last_view,last_click,spend,currency,dsp_partner_brand_id,dsp_partner_campaign_id,dsp_partner_flight_id,dsp_partner_creative_id,dsp_demand_side_platform_id) VALUES ('{}','{}','{}','{}', '{}', '{}','{}','{}','{}',unhex('{}'),unhex('{}'),unhex('{}'),unhex('{}'),unhex('{}'))".format(campaign_timestamp, campaign_date, campaign_action_hour, impressions, clicks, last_view, last_click, spend, currency, brand_id, campaign_id, flight_id, creative_id, platform_id)
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


def parse_attachments():
#     Parse attachments downloaded from email
    config = configs.get("api_credentials")
    temp_folder = config.get('download_folder')
    attachment_folder = "{}/attachments".format(temp_folder)
    
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
            if len(row) < 28:
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
            campaign = row[5]
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
            
            campaign_code = data['code']
            insert_dsp_partner_campaigns(data)
            
            
#           3) Populate partner flights table (dsp_partner_flights)
            flight = row[9]
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
            creative = row[9]
            LOGGER.info("Creative : {}".format(creative))
            size = "{} x {}".format(row[21], row[22])
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
            campaign_date = "{} {}:00:00".format(row[0], row[23])
            data = {
                'campaign_date': str(campaign_date),
                'action_hour': str(row[23]),
                'advertiser_code': advertiser_code,
                'campaign_code': campaign_code,
                'flight_code': flight_code,
                'creative_code': creative_code,
                'impressions': str(row[24]),
                'clicks': str(row[25]),
                'last_view': str(row[27]),
                'last_click': str(row[26]),
                'spend': str(row[28]),
                'currency': str(row[20])
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
        
        


def get_email_attachments(start_date  = None, end_date = None):

    config = configs.get("api_credentials")
    today = datetime.today()
    temp_folder = config.get('download_folder')
    resume_file = "{}/resume.txt".format(temp_folder)
    attachment_folder = "{}/attachments".format(temp_folder)
    
    if(end_date is None):
        tomorrow = today + timedelta(1)
        end_date = tomorrow.strftime('%Y/%m/%d')
    
    yesterday = today - timedelta(1)
    
    if(start_date  is None):
        start_date = yesterday.strftime('%Y/%m/%d')
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
    }
    
    LOGGER.info("DBM India Email Date Range :: {}".format(params))
    
    #     Read emails IInd format
    connection = email.FetchEmail(mail_server=config.get('mail_server'), username=config.get('email_username'),password=config.get('email_password'))
#     resumeFile = file_path = os.path.join(resume_file)
    resumeFile = file_path = resume_file #os.path.join(resume_file)
#     LOGGER.info(resumeFile)

    connection.recover(resumeFile)
#     if 'attachments' not in os.listdir(os.getcwd()):
    if 'attachments' not in os.listdir(temp_folder):
        os.mkdir(attachment_folder)
    for msg in connection.GenerateMailMessages(resumeFile, config.get('email_subject'), start_date, end_date):
        connection.SaveAttachmentsFromMailMessage(msg, attachment_folder)
    os.remove(file_path)


# Function to verify config file
def validate_config(config):
    required_keys = ['mail_server', 'email_username', 'email_password', 'email_subject', "download_folder", "host", "user", "password", "database"]
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
    
    campaign_sync_start_date = None if args.start_date is None else args.start_date
    campaign_sync_end_date = None if args.start_date is None else args.end_date
    
#     Read emails
    get_email_attachments(campaign_sync_start_date, campaign_sync_end_date)
    
#     Parse attachments
    parse_attachments()
    
    


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
