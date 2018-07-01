
--
-- Database: `adskom`
--
CREATE DATABASE IF NOT EXISTS `adskom` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `adskom`;

-- --------------------------------------------------------

--
-- Table structure for table `taboola_accounts`
--

DROP TABLE IF EXISTS `taboola_accounts`;
CREATE TABLE `taboola_accounts` (
  `id` int(11) NOT NULL,
  `api_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `account_id` varchar(255) DEFAULT NULL,
  `partner_types` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `campaign_types` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `taboola_campaigns`
--

DROP TABLE IF EXISTS `taboola_campaigns`;
CREATE TABLE `taboola_campaigns` (
  `id` int(11) NOT NULL,
  `api_id` int(11) DEFAULT NULL,
  `advertiser_id` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `tracking_code` varchar(255) DEFAULT NULL,
  `cpc` varchar(255) DEFAULT NULL,
  `daily_cap` varchar(255) DEFAULT NULL,
  `spending_limit` varchar(255) DEFAULT NULL,
  `spending_limit_model` varchar(255) DEFAULT NULL,
  `country_targeting` varchar(255) DEFAULT NULL,
  `platform_targeting` varchar(255) DEFAULT NULL,
  `publisher_targeting` varchar(255) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `approval_state` varchar(255) DEFAULT NULL,
  `is_active` varchar(255) DEFAULT NULL,
  `spent` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `taboola_campaign_performances`
--

DROP TABLE IF EXISTS `taboola_campaign_performances`;
CREATE TABLE `taboola_campaign_performances` (
  `id` int(11) NOT NULL,
  `campaign_id` int(11) DEFAULT NULL,
  `campaign_date` date DEFAULT NULL,
  `impressions` varchar(255) DEFAULT NULL,
  `ctr` varchar(255) DEFAULT NULL,
  `clicks` varchar(255) DEFAULT NULL,
  `cpc` varchar(255) DEFAULT NULL,
  `cpm` varchar(255) DEFAULT NULL,
  `cpa_conversion_rate` varchar(255) DEFAULT NULL,
  `cpa_actions_num` varchar(255) DEFAULT NULL,
  `cpa` varchar(255) DEFAULT NULL,
  `spent` varchar(255) DEFAULT NULL,
  `currency` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `taboola_accounts`
--
ALTER TABLE `taboola_accounts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `taboola_campaigns`
--
ALTER TABLE `taboola_campaigns`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `taboola_campaign_performances`
--
ALTER TABLE `taboola_campaign_performances`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `taboola_accounts`
--
ALTER TABLE `taboola_accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT for table `taboola_campaigns`
--
ALTER TABLE `taboola_campaigns`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT for table `taboola_campaign_performances`
--
ALTER TABLE `taboola_campaign_performances`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

