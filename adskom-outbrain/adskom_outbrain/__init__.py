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
import logging
import backoff
import base64
import requests
import singer
import dateutil.parser
import adskom_outbrain.database as database


import adskom_outbrain.schemas as schemas
import adskom_outbrain.configs as configs

LOGGER = singer.get_logger()

BASE_URL = 'https://api.outbrain.com/amplify/v0.1'
PLATFORM_NAME = 'Outbrain'

PLATFORM_NAME_TABOOLA = 'Taboola'

platform_id = None
access_token = None

configs = {}

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=lambda e: e.response is not None and 400 <= e.response.status_code < 500, # pylint: disable=line-too-long
                      factor=2)



def request(url, access_token, params={}):

    try:
        response = requests.get(
            url,
            headers={'OB-TOKEN-V1': '{}'.format(access_token),
                     'Accept': 'application/json'},
            params=params)
    except Exception as exception:
        LOGGER.exception(exception)

    response.raise_for_status()
    return response


# Function to generate access token for outbrain api
def generate_access_token(username, password):

    url = '{}/login'.format(BASE_URL)
   
    auth_string = "{}:{}".format(username, password)
#     print(auth_string)
    response = requests.get(
        url,
        headers={'Authorization': b'Basic ' + base64.b64encode(auth_string.encode(encoding='utf_8')),
                 'Accept': 'application/json'},
        )

    if response.status_code == 200:
        LOGGER.info("Got an access token.")
    elif response.status_code >= 400 and response.status_code < 500:
        LOGGER.error('{}: {}'.format(response.json().get('error'),
                                     response.json().get('error_description')))
        raise RuntimeError

    return response.json().get('OB-TOKEN-V1', None)


def get_access_token():
    global access_token
    token_days = None
    config_api = configs.get("api_credentials")
    access_token_day_limit = int(config_api.get('access_token_day_limit',"30"))
    
    if(access_token is None):
        LOGGER.info("Reading access_token from Database & if its generation date is < 30 days then generate new")
        config_db = configs.get("db_credentials")
        db = database.Connection(database=config_db.get('database'), user=config_db.get('user'),password=config_db.get('password'),host=config_db.get('host'))
        
        data = db.get("SELECT access_token, TIMESTAMPDIFF(DAY, token_created_at, CURDATE()) as token_days FROM dsp_demand_side_platforms WHERE name = '{}' " .format(PLATFORM_NAME))
    
        if (data):
            access_token = data.get('access_token')
            token_days = data.get('token_days')
            if(token_days is None):
                token_days = access_token_day_limit
            else :
                token_days = int(token_days)
                
            if(access_token is None):
                access_token = ""
            
            if(access_token == "" or  token_days >= access_token_day_limit):
                LOGGER.info("Generating new token since it get expired")
                access_token = generate_access_token(config_api.get('username'),config_api.get('password'))
                
                if(access_token is not None):
                    LOGGER.info("Save access token into database")
                    statement = "UPDATE dsp_demand_side_platforms set access_token = '{}', token_created_at=now()  WHERE name = '{}'".format(access_token, PLATFORM_NAME)
                    db.execute(statement)
        
    return access_token
        
            

# Function to get Outbrain DSP Platform Id

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

def getTaboolaPlatformId():
    
    
    LOGGER.info("Reading platform_id from Database")
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    data = db.get("SELECT hex(id) as platform_id FROM dsp_demand_side_platforms WHERE name = '{}' " .format(PLATFORM_NAME_TABOOLA))

    if (data):
        platform_id = data.get('platform_id')
        
        
    return platform_id


# Function to get DSP Partner Brand Id by code
def getDSPPartnerBrandId(code):
    
    brand_id = ''
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    data = db.get("SELECT hex(id) as brand_id FROM dsp_partner_brands WHERE code = '{}' " .format(code))

    if (data):
        brand_id = data.get('brand_id')
        
        
    return brand_id


# Function to get DSP Partner Campaign Id by code
def getDSPPartnerCampaignId(code):
    
    campaign_id = ''
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    data = db.get("SELECT hex(id) as campaign_id FROM dsp_partner_campaigns WHERE code = '{}' " .format(code))

    if (data):
        campaign_id = data.get('campaign_id')
        
        
    return campaign_id
        



# Function to fetch & parse campaigns

def parse_campaign(campaign, marketer_id):
    
    id = campaign.get('id')
    name = campaign.get('name', '')
#     marketer_id = campaign.get('marketerId')
        
    temp_campaign = {
            'id': str(id),
            'marketer_id': str(marketer_id),
            'name': str(name),
        }
    
    
    return temp_campaign


# Function to insert campaign in dsp_partner_campaigns & dsp_partner_campaign_demand_side_platforms

def insert_campaign(campaign):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
            
    api_id = campaign.get('id')
    name = campaign.get('name', '')
    marketer_id = campaign.get('marketer_id')
    
#     Get Partner Brand Id
    brand_id = getDSPPartnerBrandId(marketer_id)
    
#     Get Outbrain Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
    data = db.query("SELECT * FROM dsp_partner_campaigns WHERE code = '{}' " .format(api_id))

    if (data):
        LOGGER.info("Updating Campaign for api_id : {} ".format(api_id))

        statement = "UPDATE dsp_partner_campaigns set name = '{}', updated_at = now() WHERE code = '{}'".format(name, api_id)
        db.execute(statement)
        
    else:
        LOGGER.info("Inserting Campaign for api_id : {} ".format(api_id))
#         Insert campaign in dsp_partner_campaigns
        statement = "INSERT INTO dsp_partner_campaigns (name,code,dsp_partner_brand_id,id,created_at,updated_at) VALUES ('{}','{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format(name, api_id, brand_id)
        db.execute(statement)
        
        
        campaign_id = getDSPPartnerCampaignId(api_id)
#         Insert campaign in dsp_partner_campaign_demand_side_platforms
        statement = "INSERT INTO dsp_partner_campaign_demand_side_platforms (dsp_partner_campaign_id,dsp_demand_side_platform_id) VALUES (unhex('{}'),unhex('{}'))".format(campaign_id, platform_id)
        db.execute(statement)
    
    return True



def fetch_campaigns(marketer_id):
    access_token = get_access_token()

    params = {
        'includeArchived': 'true',
        'fetch': 'basic',
        'limit': '500'
    }
    url = '{}/marketers/{}/campaigns'.format(BASE_URL, marketer_id)
    response = request(url, access_token, params)

    
    return response.json().get('campaigns')


def sync_campaigns(marketer_id):
    campaigns = fetch_campaigns(marketer_id)
    LOGGER.info('Synced {} campaigns.'.format(len(campaigns)))
    parsed_campaigns = [parse_campaign(c, marketer_id) for c in campaigns]
    
    for parsed_campaign in parsed_campaigns:
#         Insert campaign
        status = insert_campaign(parsed_campaign) 
    
    LOGGER.info("Done syncing campaigns.")


def parse_campaign_performance(campaign_performance, campaign_id):
    

#     {
#         'metadata':{'id':'2018-02-17','toDate':'2018-02-17','fromDate':'2018-02-17'},
#         'metrics':{'ecpc':0,'clicks':0.0,'impressions':0.0,'cpa':0,'conversionRate':0,'ctr':0,'spend':0.0,'conversions':0.0}
#     }
#     Taboola cpa_actions_num -> Total number of actions (also referred as conversions), same value is in outbrain 'conversions'

    metrics = campaign_performance.get('metrics')
    metadata = campaign_performance.get('metadata')
    
    impressions = metrics.get('impressions', '')
    clicks = metrics.get('clicks', '')
    last_click = metrics.get('conversions','')
    spend = metrics.get('spend', '')
    campaign_date = metadata.get('id')
    
    temp_campaign_performance = {
            'campaign_id': str(campaign_id),
            'impressions': str(impressions),
            'last_click': str(last_click),
            'clicks': str(clicks),
            'spend': str(spend),
            'campaign_date': str(campaign_date),
        }
    
    
    return temp_campaign_performance


# Function to insert campaign performace into fact_platform_campaigns_taboola
def insert_campaign_performance(campaign_performance):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    campaign_id = str(campaign_performance.get('campaign_id'))
    campaign_date = str(datetime.strptime( campaign_performance.get('campaign_date'),'%Y-%m-%d').date())
    campaign_timestamp = str(datetime.strptime( campaign_performance.get('campaign_date'),'%Y-%m-%d').timestamp())
    campaign_action_hour = str(datetime.strptime( campaign_performance.get('campaign_date'),'%Y-%m-%d').time())

    
    impressions = campaign_performance.get('impressions', '')
    clicks = campaign_performance.get('clicks', '')
    last_click = campaign_performance.get('last_click','')
    spend = campaign_performance.get('spend', '')
    
    dsp_brand_id = ''
    dsp_campaign_id = ''
    
    dsp_campaign_data = db.get("SELECT hex(id) as campaign_id, hex(dsp_partner_brand_id) as brand_id FROM dsp_partner_campaigns WHERE code = '{}' " .format(campaign_id))
    if (dsp_campaign_data):
        dsp_campaign_id = dsp_campaign_data.get('campaign_id')
        dsp_brand_id = dsp_campaign_data.get('brand_id')
    
    
    platform_id = getPlatformId()
    
    #     check if already exist then update it else insert
    data = db.query("SELECT * FROM fact_platform_campaigns_taboola WHERE dsp_partner_campaign_id = unhex('{}') AND action_date = '{}'" .format(dsp_campaign_id, campaign_date))

    if (data):

        LOGGER.info("Updating Campaign Performace for campaign_id : {} and campaign_date = {}".format(campaign_id, campaign_date))
        statement = "UPDATE fact_platform_campaigns_taboola set impressions = '{}', clicks = '{}', last_click = '{}', spend = '{}'  WHERE dsp_partner_campaign_id = unhex('{}') AND action_date = '{}'".format(impressions, clicks, last_click, spend,dsp_campaign_id,campaign_date)
        db.execute(statement)
        
    else:
        
        LOGGER.info("Inserting Campaign Performace for campaign_id : {} and campaign_date = {}".format(campaign_id, campaign_date))
        statement = "INSERT INTO fact_platform_campaigns_taboola (unix_timestamp,action_date,action_hour,impressions,clicks,last_click,spend,dsp_partner_brand_id,dsp_partner_campaign_id,dsp_demand_side_platform_id) VALUES ('{}','{}','0', '{}','{}','{}','{}',unhex('{}'),unhex('{}'),unhex('{}'))".format(campaign_timestamp, campaign_date, impressions, clicks, last_click, spend, dsp_brand_id, dsp_campaign_id, platform_id)
#         LOGGER.info("Insert Statement : {}".format(statement))
        db.execute(statement)
        
    return True
    
    

def insert_partner_campaigns():
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    platform_id = getPlatformId()
    
    taboola_platform_id = getTaboolaPlatformId()
    
    LOGGER.info("Inserting Partner Campaigns")
    
    statement = "TRUNCATE table dim_partner_campaigns"
    db.execute(statement)
    
    statement = "INSERT INTO dim_partner_campaigns (dsp_partner_campaign_id, dsp_partner_campaign_name, dsp_partner_brand_id, dsp_partner_brand_name, dsp_demand_side_platform_id, dsp_demand_side_platform_name) (SELECT c.id, c.NAME, b.id, b.NAME, d.id, d.NAME FROM dsp_partner_campaigns c LEFT JOIN dsp_partner_brands b ON c.dsp_partner_brand_id = b.id LEFT JOIN dsp_partner_campaign_demand_side_platforms cd ON c.id = cd.dsp_partner_campaign_id LEFT JOIN dsp_demand_side_platforms d ON cd.dsp_demand_side_platform_id = d.id WHERE cd.dsp_demand_side_platform_id = unhex('{}'))".format(platform_id)
    db.execute(statement)
    
    statement = "INSERT INTO dim_partner_campaigns (dsp_partner_campaign_id, dsp_partner_campaign_name, dsp_partner_brand_id, dsp_partner_brand_name, dsp_demand_side_platform_id, dsp_demand_side_platform_name) (SELECT c.id, c.NAME, b.id, b.NAME, d.id, d.NAME FROM dsp_partner_campaigns c LEFT JOIN dsp_partner_brands b ON c.dsp_partner_brand_id = b.id LEFT JOIN dsp_partner_campaign_demand_side_platforms cd ON c.id = cd.dsp_partner_campaign_id LEFT JOIN dsp_demand_side_platforms d ON cd.dsp_demand_side_platform_id = d.id WHERE cd.dsp_demand_side_platform_id = unhex('{}'))".format(taboola_platform_id)
    db.execute(statement)
    
    
    return True
    
    
    

def fetch_campaign_performance(marketer_id, start_date  = None, end_date = None):
    access_token = get_access_token()

    url = ('{}/reports/marketers/{}/campaigns/periodic' #pylint: disable=line-too-long
           .format(BASE_URL, marketer_id))

    today = datetime.today()
    
    if(end_date is None):
        end_date = today.strftime('%Y-%m-%d')
    
    yesterday = today - timedelta(1)
    
    if(start_date  is None):
        start_date = yesterday.strftime('%Y-%m-%d')
    
    params = {
        'from': start_date,
        'to': end_date,
        'limit':'100',
        'offset':'0',
        'breakdown':'daily',
        'includeArchivedCampaigns':'true',
        'includeConversionDetails':'false',
        'format':'v2'
        
    }
    
    LOGGER.info("Campaign Performance Date Range :: {}".format(params))
    
    campaign_performance = request(url, access_token, params)
    
#     print("Reports :::: {}".format(campaign_performance.json()))
    
    if(campaign_performance.json().get('totalCampaigns') > 0):
        return campaign_performance.json().get('campaignResults')
    
    return False


def sync_campaign_performance(marketer_id, marketer, start_date  = None, end_date = None):
    performances = fetch_campaign_performance(marketer_id, start_date, end_date)

    parsed_performances = None
    
#     Loop each report and insert into database, and create allowed account if report found
    if(performances):
#         Insert marketer if report found
        insert_marketer(marketer)
#         Fetch campaigns for this account
        LOGGER.info("Fetching campaign for marketer_id : {}".format(marketer_id))
        campaigns = sync_campaigns(marketer_id)
        
        for performance in performances:
#             Insert reports
            campaign_id = performance.get("campaignId")
            results = performance.get("results")
            for result in results:
                parsed_performance = parse_campaign_performance(result, campaign_id)
                status = insert_campaign_performance(parsed_performance) 
            

    
    LOGGER.info("Done syncing campaign_performance.")





def parse_marketer(marketer):
    id = marketer.get('id')
    name = marketer.get('name', '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   
    account = {
            'name': str(name),
            'id': str(id),
        }
    return account


# Function to insert record in dsp_partner_brands
def insert_marketer(marketer):
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
        
    marketer_id = marketer.get('id')
    name = marketer.get('name', '')
        
#     Get Outbrain Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
    data = db.query("SELECT * FROM dsp_partner_brands WHERE code = '{}' " .format(marketer_id))
    
    if (data):
        LOGGER.info("Updating marketer_id : {} ".format(marketer_id))

        statement = "UPDATE dsp_partner_brands set name = '{}', updated_at = now() WHERE code = '{}'".format(name, marketer_id)
        db.execute(statement)
        
    else:
        LOGGER.info("Inserting marketer_id : {} ".format(marketer_id))
        statement = "INSERT INTO dsp_partner_brands (name,code,dsp_demand_side_platform_id,id,created_at,updated_at) VALUES ('{}','{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format(name, marketer_id, platform_id)
        db.execute(statement)
    
    return True


#Fetch marketer from api
def fetch_marketers():
    access_token = get_access_token()
    url = '{}/marketers'.format(BASE_URL)
    response = request(url, access_token)
#     print("{}".format(response.json()))
    return response.json().get('marketers')


#Function call for syncing marketers
def sync_marketers():
    marketers = fetch_marketers()
    LOGGER.info('Synced {} Marketers.'.format(len(marketers)))
    parsed_marketers = [parse_marketer(c) for c in marketers]
    LOGGER.info("Done syncing marketers.")
    return parsed_marketers



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



#Function to sync account, campaigns & reports from Outbrain API


def do_sync(args):
    LOGGER.info("Starting sync.")
    
    global configs
    
    configs = load_config(args.config)
    config = configs.get("api_credentials")
    
    campaign_sync_start_date = None if args.start_date is None else args.start_date
    campaign_sync_end_date = None if args.start_date is None else args.end_date

    access_token = get_access_token()

    marketers = sync_marketers()
    if(marketers):
        for marketer in marketers:

            merketer_id = marketer.get("id","")
            LOGGER.info("Fetching campaign reports for marketer : {}".format(merketer_id))
            reports = sync_campaign_performance(merketer_id, marketer, campaign_sync_start_date, campaign_sync_end_date)

#         Insert partner dim_partner_campaigns
        insert_partner_campaigns()
                
    


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
