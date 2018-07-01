
-- --------------------------------------------------------

--
-- Table structure for table `fact_keyword_steps`
--

CREATE TABLE `fact_keyword_steps` (
  `unix_timestamp` int(11) NOT NULL DEFAULT '0',
  `keyword_tag_step_id` varchar(255) DEFAULT NULL,
  `sub_brand_id` varchar(255) DEFAULT NULL,
  `unique_count` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


