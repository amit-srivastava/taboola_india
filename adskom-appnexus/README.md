# Adskom DBM Sync API

Author: Amit Srivastava (s.amitsrivastava@gmail.com)

This program includes:
- Pulls raw data from AppNexus API
- Extracts the following resources:
  - Brands
  - Campaigns
  - Flights
  - Creatives
  - Campaign reports
- Outputs the schema for each resource
  - Check for update on already fetched data
  - Else insert new data
- Incrementally pulls data based on the input start_date & end_date
  - Default its pull for yesterday & today
  - Command line argument params start_date, end_date


## Quick start

1. Install of adskom-appnexus api
	
	- Clone application project
    ```bash
    > git clone git@github.com:adskom/taboola_india.git
    > cd taboola_india/adskom-appnexus

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

	- Install adskom-appnexus
    ```bash
    > pip install .
    ```
	

2. Get credentials from AppNexus India:

    You'll need:
	- A AppNexus username and password with access to the API
    - Report Time Zone


3. Create the config file.

    There is a template you can use at `config.json.example`, just copy it to `config.json`
    in the repo root and insert your credentials.
	
	- Configuration for AppNexus API's
		- `username`, your AppNexus username -- used to generate an API access key.
	    - `password`, the AppNexus password to go along with `username`.
	    - `timezone`, report timezone
	    - `download_folder`, temporary download folder which stores the downloaded attachments.
    - Configuration for Database connection
    	- `host`, you mysql hostname (looks like `localhost`)
    	- `user`, you mysql hostname 
    	- `password`, you mysql user password 
    	- `database`, you mysql database name (looks like `adskom`)
    

4. Create the database tables.

	There is a database.sql file which need to be import for creating database and tables.
	


5. Run the application.

   ```bash
   > adskom-appnexus --config config.json
   ```
   
   - Command line parameters are
   		--config, config file name which provides taboola api credentail and database access permission
   		--start_date, report syncing start from date with format YYYY-MM-DD (default is yesterday)
   		--end_date, report syncing end from date with format YYYY-MM-DD (default is today)

---

Copyright &copy; 2018 Actech Information Systems
