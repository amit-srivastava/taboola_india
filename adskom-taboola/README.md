# Adskom Taboola Sync API

Author: Amit Srivastava (s.amitsrivastava@gmail.com)

This program includes:
- Pulls raw data from Taboola's Backstage API
- Extracts the following resources:
  - allowed accounts
  - Campaigns
  - Campaign Reports, specifically the `campaign_day_breakdown` report
- Outputs the schema for each resource
  - Check for update on already fetched data
  - Else insert new data
- Incrementally pulls data based on the input start_date & end_date
  - Default its pull for yesterday & today
  - Command line argument params start_date, end_date


## Quick start

1. Install of adskom-taboola api
	
	- Clone application project
    ```bash
    > git clone git@github.com:adskom/taboola_india.git
    > cd taboola_india/adskom-taboola

    ```
	
	- Prepare environment for Python 3
	```bash
	> pyvenv p3_env
	> source p3_env/bin/activate
	```
	
	- To deactivate from environment
	```bash
	> deactivate
	```
	
	- If pip upgrade required
	```bash
	> pip install --upgrade pip
	```

	- Install adskom-taboola
    ```bash
    > pip install .
    ```
	

2. Get credentials from Taboola:

    You'll need:

    - Your account id (if you aren't sure, contact your account manager)
    - A Taboola username and password with access to the API
    - A client ID and secret for the API (your account manager can give you these)

3. Create the config file.

    There is a template you can use at `config.json.example`, just copy it to `config.json`
    in the repo root and insert your credentials.
	
	- Configuration for Taboola API's
	    - `username`, your Taboola username -- used to generate an API access key.
	    - `password`, the Taboola password to go along with `username`.
	    - `client_id`, your Taboola client ID. You should reach out to your account manager to get this.
	    - `client_secret`, your Taboola client secret. You should reach out to your account manager to get this.
    - Configuration for Database connection
    	- `host`, you mysql hostname (looks like `localhost`)
    	- `user`, you mysql hostname 
    	- `password`, you mysql user password 
    	- `database`, you mysql database name (looks like `adskom`)
    

4. Create the database tables.

	There is a database.sql file which need to be import for creating database and tables.
	


5. Run the application.

   ```bash
   > adskom-taboola --config config.json
   ```
   
   - Command line parameters are
   		--config, config file name which provides taboola api credentail and database access permission
   		--start_date, report syncing start from date with format YYYY-MM-DD (default is yesterday)
   		--end_date, report syncing end from date with format YYYY-MM-DD (default is today)

## Gotchas

- `campaigns`: Taboola pushes `null` for `start_date` and `9999-12-31` for `end_date` sometimes. This tap converts `null` dates to `9999-12-31` for consistency. I don't know what that signifies at present.

---

Copyright &copy; 2017 Actech Information Systems
