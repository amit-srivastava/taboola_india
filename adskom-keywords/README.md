# Adskom DBM Sync API

Author: Amit Srivastava (s.amitsrivastava@gmail.com)

This program includes:
- Scan *.csv log files in specific folder
- Insert data into database



## Quick start

1. Installation of adskom-keywords api
	
	- Clone application project
    ```bash
    > git clone git@github.com:adskom/taboola_india.git
    > cd taboola_india/adskom-keywords

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

	- Install adskom-keywords
    ```bash
    > pip install .
    ```
	

2. Create the config file.

    There is a template you can use at `config.json.example`, just copy it to `config.json`
    in the repo root and insert your credentials.
	
	- Configuration for Importing logs
		- `log_folder`, log file folder 
	    - `processing_limit`, concurrent processing for data insertion
    - Configuration for Database connection
    	- `host`, you mysql hostname (looks like `localhost`)
    	- `user`, you mysql hostname 
    	- `password`, you mysql user password 
    	- `database`, you mysql database name (looks like `adskom`)
    

3. Create the database tables.

	There is a database.sql file which need to be import for creating database and tables.
	


4. Run the application.

   ```bash
   > adskom-keywords --config config.json
   ```
   
   - Command line parameters are
   		--config, config file name which provides api credentail and database access permission


---

Copyright &copy; 2018 Actech Information Systems
