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
import requests
import singer
import dateutil.parser
import adskom_taboola.database as database


import adskom_taboola.schemas as schemas
import adskom_taboola.configs as configs

LOGGER = singer.get_logger()

BASE_URL = 'https://backstage.taboola.com'
PLATFORM_NAME = 'Taboola'

PLATFORM_NAME_OUTBRAIN = 'Outbrain'

platform_id = None

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
            headers={'Authorization': 'Bearer {}'.format(access_token),
                     'Accept': 'application/json'},
            params=params)
    except Exception as exception:
        LOGGER.exception(exception)

    response.raise_for_status()
    return response


# Function to generate access token for taboola api
def generate_token(client_id, client_secret, username, password):

    url = '{}/backstage/oauth/token'.format(BASE_URL)
   
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(
        url,
        headers={'Content-Type': 'application/x-www-form-urlencoded',
                 'Accept': 'application/json'},
        params=params)

    if response.status_code == 200:
        LOGGER.info("Got an access token.")
    elif response.status_code >= 400 and response.status_code < 500:
        LOGGER.error('{}: {}'.format(response.json().get('error'),
                                     response.json().get('error_description')))
        raise RuntimeError

    return response.json().get('access_token', None)


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

def getOutbrainPlatformId():
    
    
    LOGGER.info("Reading platform_id from Database")
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    data = db.get("SELECT hex(id) as platform_id FROM dsp_demand_side_platforms WHERE name = '{}' " .format(PLATFORM_NAME_OUTBRAIN))

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
        

# Function to fetch & parse campaign performace report 
def parse_campaign_performance(campaign_performance):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    campaign_id = str(campaign_performance.get('campaign'))
    
    impressions = campaign_performance.get('impressions', '')
    clicks = campaign_performance.get('clicks', '')
    last_click = campaign_performance.get('cpa_actions_num','')
    spend = campaign_performance.get('spent', '')
    
    temp_campaign_performance = {
            'campaign_id': str(campaign_id),
            'impressions': str(impressions),
            'ctr': str(campaign_performance.get('ctr', '')),
            'cpc': str(campaign_performance.get('cpc', '')),
            'cpa_actions_num': str(last_click),
            'cpa': str(campaign_performance.get('cpa', '')),
            'cpm': str(campaign_performance.get('cpm', '')),
            'clicks': str(clicks),
            'currency': str(campaign_performance.get('currency', '')),
            'cpa_conversion_rate': str(campaign_performance.get('cpa_conversion_rate', '')),
            'spent': str(spend),
            'campaign_date': str(campaign_performance.get('date')),
        }
    
    
    return temp_campaign_performance


# Function to insert campaign performace into fact_platform_campaigns_taboola
def insert_campaign_performance(campaign_performance):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    campaign_id = str(campaign_performance.get('campaign_id'))
    campaign_date = str(datetime.strptime( campaign_performance.get('campaign_date'),'%Y-%m-%d %H:%M:%S.%f').date())
    campaign_timestamp = str(datetime.strptime( campaign_performance.get('campaign_date'),'%Y-%m-%d %H:%M:%S.%f').timestamp())
    campaign_action_hour = str(datetime.strptime( campaign_performance.get('campaign_date'),'%Y-%m-%d %H:%M:%S.%f').time())

    
    impressions = campaign_performance.get('impressions', '')
    clicks = campaign_performance.get('clicks', '')
    last_click = campaign_performance.get('cpa_actions_num','')
    spend = campaign_performance.get('spent', '')
    
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
    
    outbrain_platform_id = getOutbrainPlatformId()
    
    LOGGER.info("Inserting Partner Campaigns")
    
    statement = "TRUNCATE table dim_partner_campaigns"
    db.execute(statement)
    
    statement = "INSERT INTO dim_partner_campaigns (dsp_partner_campaign_id, dsp_partner_campaign_name, dsp_partner_brand_id, dsp_partner_brand_name, dsp_demand_side_platform_id, dsp_demand_side_platform_name) (SELECT c.id, c.NAME, b.id, b.NAME, d.id, d.NAME FROM dsp_partner_campaigns c LEFT JOIN dsp_partner_brands b ON c.dsp_partner_brand_id = b.id LEFT JOIN dsp_partner_campaign_demand_side_platforms cd ON c.id = cd.dsp_partner_campaign_id LEFT JOIN dsp_demand_side_platforms d ON cd.dsp_demand_side_platform_id = d.id WHERE cd.dsp_demand_side_platform_id = unhex('{}'))".format(platform_id)
    db.execute(statement)
    
    statement = "INSERT INTO dim_partner_campaigns (dsp_partner_campaign_id, dsp_partner_campaign_name, dsp_partner_brand_id, dsp_partner_brand_name, dsp_demand_side_platform_id, dsp_demand_side_platform_name) (SELECT c.id, c.NAME, b.id, b.NAME, d.id, d.NAME FROM dsp_partner_campaigns c LEFT JOIN dsp_partner_brands b ON c.dsp_partner_brand_id = b.id LEFT JOIN dsp_partner_campaign_demand_side_platforms cd ON c.id = cd.dsp_partner_campaign_id LEFT JOIN dsp_demand_side_platforms d ON cd.dsp_demand_side_platform_id = d.id WHERE cd.dsp_demand_side_platform_id = unhex('{}'))".format(outbrain_platform_id)
    db.execute(statement)
    
    return True
    
    
    

def fetch_campaign_performance(access_token, account_id, start_date  = None, end_date = None):
    url = ('{}/backstage/api/1.0/{}/reports/campaign-summary/dimensions/campaign_day_breakdown' #pylint: disable=line-too-long
           .format(BASE_URL, account_id))

    today = datetime.today()
    
    if(end_date is None):
        end_date = today.strftime('%Y-%m-%d')
    
    yesterday = today - timedelta(1)
    
    if(start_date  is None):
        start_date = yesterday.strftime('%Y-%m-%d')
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
    }
    
    LOGGER.info("Campaign Performance Date Range :: {}".format(params))
    
    campaign_performance = request(url, access_token, params)
    
    return campaign_performance.json().get('results')


def sync_campaign_performance(access_token, account_id, allowed_account, start_date  = None, end_date = None):
    performance = fetch_campaign_performance(access_token, account_id, start_date , end_date)

    LOGGER.info("Got {} campaign performance records.".format(len(performance)))

    parsed_performances = [parse_campaign_performance(p) for p in performance]
    
#     Loop each report and insert into database, and create allowed account if report found
    if(parsed_performances):
#         Insert allowed account if report found
        insert_allowed_account(allowed_account)
#         Fetch campaigns for this account
        LOGGER.info("Fetching campaign for account : {}".format(account_id))
        campaigns = sync_campaigns(access_token, account_id)
        
        for parsed_performance in parsed_performances:
#             Insert reports
            status = insert_campaign_performance(parsed_performance) 
            

    
    LOGGER.info("Done syncing campaign_performance.")


# Function to fetch & parse campaigns
def parse_campaign(campaign):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    api_id = campaign.get('id')
    
    start_date = campaign.get('start_date')
    end_date = campaign.get('end_date')
    
    country_targeting = campaign.get('country_targeting')
    if country_targeting:
        country_targeting = ",".join(country_targeting)
        
    platform_targeting = campaign.get('platform_targeting')
    if platform_targeting:
        platform_targeting = ",".join(platform_targeting)
        
    publisher_targeting = campaign.get('publisher_targeting')
    if publisher_targeting:
        publisher_targeting = ",".join(publisher_targeting)
        
    api_id = campaign.get('id')
    name = campaign.get('name', '')
    advertiser_id = campaign.get('advertiser_id')
        
    temp_campaign = {
            'api_id': str(api_id),
            'advertiser_id': str(advertiser_id),
            'name': str(name),
            'tracking_code': str(campaign.get('tracking_code', '')),
            'cpc': str(campaign.get('cpc', '')),
            'daily_cap': str(campaign.get('daily_cap', '')),
            'spending_limit': str(campaign.get('spending_limit', '')),
            'spending_limit_model': str(campaign.get('spending_limit_model', '')),
            'country_targeting': str(country_targeting),
            'platform_targeting': str(platform_targeting),
            'publisher_targeting': str(publisher_targeting),
            'start_date': str('9999-12-31' if start_date is None else start_date),
            'end_date': str('9999-12-31' if end_date is None else end_date),
            'approval_state': str(campaign.get('approval_state', '')),
            'is_active': str(campaign.get('is_active',False)),
            'spent': str(campaign.get('spent', '')),
            'status': str(campaign.get('status', '')),
        }
    
    
    return temp_campaign


# Function to insert campaign in dsp_partner_campaigns & dsp_partner_campaign_demand_side_platforms

def insert_campaign(campaign):
    
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
            
    api_id = campaign.get('api_id')
    name = campaign.get('name', '')
    advertiser_id = campaign.get('advertiser_id')
    
#     Get Partner Brand Id
    brand_id = getDSPPartnerBrandId(advertiser_id)
    
#     Get Taboola Platform ID
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



def fetch_campaigns(access_token, account_id):
    url = '{}/backstage/api/1.0/{}/campaigns/'.format(BASE_URL, account_id)
    response = request(url, access_token)
    return response.json().get('results')


def sync_campaigns(access_token, account_id):
    campaigns = fetch_campaigns(access_token, account_id)
    LOGGER.info('Synced {} campaigns.'.format(len(campaigns)))
    parsed_campaigns = [parse_campaign(c) for c in campaigns]
    
    for parsed_campaign in parsed_campaigns:
#         Insert campaign
        status = insert_campaign(parsed_campaign) 
    
    LOGGER.info("Done syncing campaigns.")


# Function to fetch & parse allowed accounts
def parse_allowed_account(allowed_account):
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
    
    partner_types = allowed_account.get('partner_types')
    if partner_types:
        partner_types = ",".join(partner_types)
        
    campaign_types = allowed_account.get('campaign_types')
    if campaign_types:
        campaign_types = ",".join(campaign_types)
    
    account_id = allowed_account.get('account_id')
    name = allowed_account.get('name', '')
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   
    account = {
            'api_id': str(allowed_account.get('api_id')),
            'name': str(name),
            'account_id': str(account_id),
            'partner_types':  str(partner_types),
            'type': str(allowed_account.get('type', '')),
            'campaign_types': str(campaign_types),
        }
    
    
    return account



# Function to insert record in dsp_partner_brands
def insert_allowed_account(allowed_account):
    config = configs.get("db_credentials")
    db = database.Connection(database=config.get('database'), user=config.get('user'),password=config.get('password'),host=config.get('host'))
        
    account_id = allowed_account.get('account_id')
    name = allowed_account.get('name', '')
        
#     Get Taboola Platform ID
    platform_id = getPlatformId() 
    
#     check if already exist then update it else insert
    data = db.query("SELECT * FROM dsp_partner_brands WHERE code = '{}' " .format(account_id))
    
    if (data):
        LOGGER.info("Updating account_id : {} ".format(account_id))

        statement = "UPDATE dsp_partner_brands set name = '{}', updated_at = now() WHERE code = '{}'".format(name, account_id)
        db.execute(statement)
        
    else:
        LOGGER.info("Inserting account_id : {} ".format(account_id))
        statement = "INSERT INTO dsp_partner_brands (name,code,dsp_demand_side_platform_id,id,created_at,updated_at) VALUES ('{}','{}',unhex('{}'),unhex(replace(uuid(),'-','')),now(), now())".format(name, account_id, platform_id)
        db.execute(statement)
    
    return True



def fetch_allowed_accounts(access_token):
    url = '{}/backstage/api/1.0/users/current/allowed-accounts/'.format(BASE_URL)
    response = request(url, access_token)
    return response.json().get('results')


def sync_allowed_accounts(access_token):
    allowed_accounts = fetch_allowed_accounts(access_token)
    LOGGER.info('Synced {} allowed accounts.'.format(len(allowed_accounts)))
    parsed_allowed_accounts = [parse_allowed_account(c) for c in allowed_accounts]
    LOGGER.info("Done syncing allowed accounts.")
    return parsed_allowed_accounts


# Function to verify api access for account_id
def verify_account_access(access_token, account_id):
    url = '{}/backstage/api/1.0/token-details/'.format(BASE_URL)

    result = request(url, access_token)
    
    if result.json().get('account_id') != account_id:
        LOGGER.error("The provided credentials don't have access to `account_id` from the config file.")
        raise RuntimeError
    else:
        LOGGER.info("Verified account access via token details endpoint.")


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
    
    campaign_sync_start_date = None if args.start_date is None else args.start_date
    campaign_sync_end_date = None if args.start_date is None else args.end_date
    
    access_token = generate_token(
        client_id=config.get('client_id'),
        client_secret=config.get('client_secret'),
        username=config.get('username'),
        password=config.get('password'))
       
  
    allowed_accounts = sync_allowed_accounts(access_token)

    if(allowed_accounts):
        for allowed_account in allowed_accounts:

            partner_types = allowed_account.get("partner_types").split(",")
            account_id = allowed_account.get("account_id","")
#             Check if partner types have values ADVERTISER
            if('ADVERTISER' in partner_types):
                LOGGER.info("Fetching campaign reports for account : {}".format(account_id))
                reports = sync_campaign_performance(access_token, account_id, allowed_account, campaign_sync_start_date, campaign_sync_end_date)
            else:
                LOGGER.info("Not fetching campaign for account : {}".format(account_id))
                
        
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
