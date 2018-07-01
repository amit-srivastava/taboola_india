-- Given the limitation on /login requests, the recommended way to manage tokens is to store an active token to be used in all requests, 
-- and periodically update it. Since each token is valid for 30 days, the update period should 30 days or less.


ALTER TABLE `dsp_demand_side_platforms` ADD `access_token` VARCHAR(1500) NULL, ADD `token_created_at` TIMESTAMP NULL;

