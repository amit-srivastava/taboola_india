-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 23, 2017 at 03:01 PM
-- Server version: 5.7.20-0ubuntu0.16.04.1
-- PHP Version: 7.0.22-0ubuntu0.16.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `adskom`
--

--
-- Dumping data for table `taboola_accounts`
--

INSERT INTO `taboola_accounts` (`id`, `api_id`, `name`, `account_id`, `partner_types`, `type`, `campaign_types`, `created_at`, `updated_at`) VALUES
(1, 1113456, 'ADSKOM - Amuratech Parkwest - SC', 'adskom-amuratechparkwest', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:35', '2017-11-23 14:40:35'),
(2, 1117232, 'ADSKOM - Amuratech- Ten BKC - SC', 'adskom-amuratech-tenbkc-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:35', '2017-11-23 14:40:35'),
(3, 1105228, 'ADSKOM - Droom Credit - SC', 'adskom-droomcredit-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:35', '2017-11-23 14:40:35'),
(4, 1115682, 'ADSKOM - Droom Discovery - SC', 'adskom-droomdiscovery-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(5, 1116429, 'ADSKOM - Droom.in - SC', 'adskom-droomin-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(6, 1095492, 'ADSKOM - Network', 'adskom-network', 'None', 'NETWORK', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(7, 1065545, 'ADSKOM India - Droom - SC', 'adskomindia-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(8, 1107927, 'ADSKOM India - Droom Eco - SC', 'adskomindia-droomeco-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(9, 1105482, 'ADSKOM India - Droom History - SC', 'adskomindia-droomhistory-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(10, 1103342, 'ADSKOM India - Patanjali - SC', 'adskomindia-patanjali-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(11, 1107926, 'ADSKOM India - SaiPushp - Puranik Builders - SC', 'adskomindia-saipushp-puranikbuilders-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36'),
(12, 1095494, 'ADSKOM India - Shapoorji Pallonji - SC', 'adskomindia-shapoorjipallonji-sc', 'ADVERTISER', 'PARTNER', 'PAID', '2017-11-23 14:40:36', '2017-11-23 14:40:36');

--
-- Dumping data for table `taboola_campaigns`
--

INSERT INTO `taboola_campaigns` (`id`, `api_id`, `advertiser_id`, `name`, `tracking_code`, `cpc`, `daily_cap`, `spending_limit`, `spending_limit_model`, `country_targeting`, `platform_targeting`, `publisher_targeting`, `start_date`, `end_date`, `approval_state`, `is_active`, `spent`, `status`, `created_at`, `updated_at`) VALUES
(1, 774314, 'adskom-amuratechparkwest', 'Parkwest - Desktop', 'utm_source=taboola&amp;utm_medium=referral', '0.12', '0.0', '2767.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '9999-12-31', '2017-11-30', 'PENDING', 'False', '0.0', 'PENDING_APPROVAL', '2017-11-23 14:40:38', '2017-11-23 14:40:38'),
(2, 774315, 'adskom-amuratechparkwest', 'Parkwest - Mobile', 'utm_source=taboola&amp;utm_medium=referral', '0.08', '0.0', '1844.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-10-26', '2017-11-30', 'APPROVED', 'False', '0.0', 'PAUSED', '2017-11-23 14:40:38', '2017-11-23 14:40:38'),
(3, 820267, 'adskom-amuratech-tenbkc-sc', 'Ten BKC - Desktop', 'utm_source=taboola&amp;utm_medium=referral', '0.11', '0.0', '800.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-23', '2017-12-10', 'APPROVED', 'True', '0.0', 'RUNNING', '2017-11-23 14:41:15', '2017-11-23 14:41:15'),
(4, 820282, 'adskom-amuratech-tenbkc-sc', 'Ten BKC - Mobile', 'utm_source=taboola&amp;utm_medium=referral', '0.03', '0.0', '500.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-23', '2017-12-10', 'APPROVED', 'True', '0.0', 'RUNNING', '2017-11-23 14:41:15', '2017-11-23 14:41:15'),
(5, 700340, 'adskom-droomcredit-sc', 'Droom Credit - Desktop', 'None', '0.01', '0.0', '100.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-23', '2017-08-31', 'APPROVED', 'False', '86.26', 'EXPIRED', '2017-11-23 14:41:25', '2017-11-23 14:41:25'),
(6, 700344, 'adskom-droomcredit-sc', 'Droom Credit - Mob/Tab', 'None', '0.01', '0.0', '320.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-23', '2017-08-31', 'APPROVED', 'False', '319.77', 'EXPIRED', '2017-11-23 14:41:25', '2017-11-23 14:41:25'),
(7, 805317, 'adskom-droomdiscovery-sc', 'Droom Discovery - Desktop', 'utm_source=taboola&amp;utm_medium=referral', '0.01', '0.0', '200.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-15', '2017-11-29', 'APPROVED', 'True', '23.45', 'RUNNING', '2017-11-23 14:41:33', '2017-11-23 14:41:33'),
(8, 805324, 'adskom-droomdiscovery-sc', 'Droom Discovery - Mobile', 'utm_source=taboola&amp;utm_medium=referral', '0.01', '0.0', '500.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-15', '2017-11-29', 'APPROVED', 'True', '116.43', 'RUNNING', '2017-11-23 14:41:33', '2017-11-23 14:41:33'),
(9, 805302, 'adskom-droomin-sc', 'DroomIn- Desktop', 'utm_source=taboola&amp;utm_medium=referral', '0.01', '0.0', '500.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-16', '2017-11-29', 'APPROVED', 'True', '19.14', 'RUNNING', '2017-11-23 14:41:58', '2017-11-23 14:41:58'),
(10, 805308, 'adskom-droomin-sc', 'DroomIn- Mobile', 'utm_source=taboola&amp;utm_medium=referral', '0.01', '0.0', '1200.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-16', '2017-11-29', 'APPROVED', 'True', '245.95', 'RUNNING', '2017-11-23 14:41:58', '2017-11-23 14:41:58'),
(11, 395518, 'adskomindia-sc', '203__Droom.in - Desktop/Tablet', 'None', '0.12', '0.0', '44957.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2016-10-19', '2017-11-29', 'APPROVED', 'True', '44383.74', 'RUNNING', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(12, 396211, 'adskomindia-sc', '203__Droom.in - Mobile', 'None', '0.03', '0.0', '4347.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2016-10-19', '2017-03-30', 'APPROVED', 'True', '4140.89', 'EXPIRED', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(13, 459827, 'adskomindia-sc', '203__Droom.in - Tablet', 'None', '0.06', '0.0', '500.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-01-13', '2017-01-23', 'APPROVED', 'False', '134.34', 'EXPIRED', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(14, 622264, 'adskomindia-sc', 'Test__Droom.in - Mob/Tab', 'None', '0.02', '0.0', '5700.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-06-15', '2017-11-29', 'APPROVED', 'True', '5156.46', 'RUNNING', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(15, 638088, 'adskomindia-sc', '203__Droom.in - Desktop/Tablet - Copy/Auto Contextual', 'None', '0.12', '0.0', '300.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-06-28', '2017-06-30', 'APPROVED', 'False', '1.92', 'EXPIRED', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(16, 666964, 'adskomindia-sc', 'Droom History - Desktop', 'utm_source=taboola&amp;utm_medium={site}', '0.01', '0.0', '762.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-07-25', '2017-09-08', 'APPROVED', 'False', '736.63', 'EXPIRED', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(17, 666967, 'adskomindia-sc', 'Droom History - Mob/Tab', 'utm_source=taboola&amp;utm_medium={site}', '0.01', '0.0', '784.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-07-25', '2017-09-08', 'APPROVED', 'False', '767.84', 'EXPIRED', '2017-11-23 14:42:02', '2017-11-23 14:42:02'),
(18, 724532, 'adskomindia-droomeco-sc', 'Droom Eco - Desktop', 'None', '0.02', '0.0', '100.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-09-14', '2017-09-30', 'APPROVED', 'False', '84.36', 'EXPIRED', '2017-11-23 14:42:06', '2017-11-23 14:42:06'),
(19, 726147, 'adskomindia-droomeco-sc', 'Droom Eco - Mobile', 'None', '0.01', '0.0', '350.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-09-14', '2017-09-30', 'APPROVED', 'False', '285.48', 'EXPIRED', '2017-11-23 14:42:06', '2017-11-23 14:42:06'),
(20, 718747, 'adskomindia-droomhistory-sc', 'Droom History - Mob/Tab', 'None', '0.01', '0.0', '1950.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-09-08', '2017-11-29', 'APPROVED', 'True', '1661.88', 'RUNNING', '2017-11-23 14:42:17', '2017-11-23 14:42:17'),
(21, 718749, 'adskomindia-droomhistory-sc', 'Droom History - Desktop', 'None', '0.01', '0.0', '862.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-09-08', '2017-11-29', 'APPROVED', 'True', '824.29', 'RUNNING', '2017-11-23 14:42:17', '2017-11-23 14:42:17'),
(22, 684834, 'adskomindia-patanjali-sc', '#iSupportSwadeshi - Hindi Desktop', 'None', '0.015', '0.0', '1140.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-09', '2017-08-15', 'APPROVED', 'False', '5.96', 'EXPIRED', '2017-11-23 14:42:20', '2017-11-23 14:42:20'),
(23, 684847, 'adskomindia-patanjali-sc', '#iSupportSwadeshi - Hindi - Mob/Tab', 'None', '0.016', '0.0', '1140.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-09', '2017-08-15', 'APPROVED', 'False', '84.79', 'EXPIRED', '2017-11-23 14:42:20', '2017-11-23 14:42:20'),
(24, 684850, 'adskomindia-patanjali-sc', '#iSupportSwadeshi - EN -  Desktop', 'None', '0.01', '0.0', '1200.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-10', '2017-08-15', 'APPROVED', 'False', '0.78', 'EXPIRED', '2017-11-23 14:42:21', '2017-11-23 14:42:21'),
(25, 684858, 'adskomindia-patanjali-sc', '#iSupportSwadeshi - EN -  Mob/Tab', 'None', '0.01', '0.0', '1200.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-10', '2017-08-15', 'APPROVED', 'False', '115.8', 'EXPIRED', '2017-11-23 14:42:21', '2017-11-23 14:42:21'),
(26, 731183, 'adskomindia-saipushp-puranikbuilders-sc', 'Puranik- Desktop', 'utm_source=taboola&amp;utm_medium={site}', '0.08', '0.0', '1550.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-09-22', '2017-12-15', 'APPROVED', 'False', '1066.95', 'PAUSED', '2017-11-23 14:42:30', '2017-11-23 14:42:30'),
(27, 731218, 'adskomindia-saipushp-puranikbuilders-sc', 'Puranik- Mobile', 'utm_source=taboola&amp;utm_medium={site}', '0.05', '0.0', '500.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-09-22', '2017-12-15', 'APPROVED', 'False', '384.09', 'PAUSED', '2017-11-23 14:42:30', '2017-11-23 14:42:30'),
(28, 802483, 'adskomindia-saipushp-puranikbuilders-sc', 'GC Puranik- Desktop', 'utm_source=taboola&amp;utm_medium={site}', '0.1', '0.0', '1950.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-14', '2017-12-31', 'APPROVED', 'True', '366.88', 'RUNNING', '2017-11-23 14:42:30', '2017-11-23 14:42:30'),
(29, 802499, 'adskomindia-saipushp-puranikbuilders-sc', 'GC Puranik- Mobile', 'utm_source=taboola&amp;utm_medium={site}', '0.02', '0.0', '500.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-11-14', '2017-12-15', 'APPROVED', 'True', '115.31', 'RUNNING', '2017-11-23 14:42:30', '2017-11-23 14:42:30'),
(30, 678080, 'adskomindia-shapoorjipallonji-sc', 'Virar - Desktop', 'utm_source=taboola&amp;utm_medium={site}', '0.13', '0.0', '5300.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-04', '2017-11-21', 'APPROVED', 'False', '5110.08', 'EXPIRED', '2017-11-23 14:42:41', '2017-11-23 14:42:41'),
(31, 678095, 'adskomindia-shapoorjipallonji-sc', 'Virar - Mobile', 'utm_source=taboola&amp;utm_medium={site}', '0.05', '0.0', '358.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-08-04', '2017-11-21', 'APPROVED', 'False', '346.37', 'EXPIRED', '2017-11-23 14:42:41', '2017-11-23 14:42:41'),
(32, 755004, 'adskomindia-shapoorjipallonji-sc', 'JoyAssurance Howrah - Desktop', 'None', '0.11', '0.0', '3209.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-10-09', '2017-12-14', 'APPROVED', 'True', '2614.2', 'RUNNING', '2017-11-23 14:42:41', '2017-11-23 14:42:41'),
(33, 757069, 'adskomindia-shapoorjipallonji-sc', 'JoyAssurance Howrah - Mobile', 'None', '0.06', '0.0', '1306.0', 'ENTIRE', 'href,type,value', 'href,type,value', 'href,type,value', '2017-10-12', '2017-12-14', 'APPROVED', 'True', '381.77', 'RUNNING', '2017-11-23 14:42:41', '2017-11-23 14:42:41');

--
-- Dumping data for table `taboola_campaign_performances`
--

INSERT INTO `taboola_campaign_performances` (`id`, `campaign_id`, `campaign_date`, `impressions`, `ctr`, `clicks`, `cpc`, `cpm`, `cpa_conversion_rate`, `cpa_actions_num`, `cpa`, `spent`, `currency`, `created_at`, `updated_at`) VALUES
(1, 805324, '2017-11-23', '896490', '0.1839395866100012', '1649', '0.01', '0.02', '0.0', '0', '0.0', '16.49', 'USD', '2017-11-23 14:41:44', '2017-11-23 14:41:44'),
(2, 805324, '2017-11-22', '550974', '0.2526435004192575', '1392', '0.01', '0.03', '0.0', '0', '0.0', '13.92', 'USD', '2017-11-23 14:41:44', '2017-11-23 14:41:44'),
(3, 805317, '2017-11-22', '1102465', '0.0377336241966865', '416', '0.01', '0.0', '0.0', '0', '0.0', '4.16', 'USD', '2017-11-23 14:41:44', '2017-11-23 14:41:44'),
(4, 805317, '2017-11-23', '268298', '0.0376447084957771', '101', '0.01', '0.0', '0.0', '0', '0.0', '1.01', 'USD', '2017-11-23 14:41:44', '2017-11-23 14:41:44'),
(5, 805308, '2017-11-23', '2899549', '0.1400562639224238', '4061', '0.01', '0.01', '0.0', '0', '0.0', '40.61', 'USD', '2017-11-23 14:42:00', '2017-11-23 14:42:00'),
(6, 805308, '2017-11-22', '1353062', '0.2094508603449066', '2834', '0.01', '0.02', '0.0', '0', '0.0', '28.34', 'USD', '2017-11-23 14:42:00', '2017-11-23 14:42:00'),
(7, 805302, '2017-11-22', '945823', '0.0253747265608893', '240', '0.01', '0.0', '0.0', '0', '0.0', '2.4', 'USD', '2017-11-23 14:42:00', '2017-11-23 14:42:00'),
(8, 805302, '2017-11-23', '278802', '0.030128908687886', '84', '0.01', '0.0', '0.0', '0', '0.0', '0.84', 'USD', '2017-11-23 14:42:00', '2017-11-23 14:42:00'),
(9, 395518, '2017-11-22', '1674860', '0.0698565850280023', '1170', '0.08', '0.05', '27.521367521367523', '322', '0.28', '91.23', 'USD', '2017-11-23 14:42:04', '2017-11-23 14:42:04'),
(10, 395518, '2017-11-23', '1303844', '0.0827552989468065', '1079', '0.08', '0.06', '1.2974976830398517', '14', '5.98', '83.72', 'USD', '2017-11-23 14:42:04', '2017-11-23 14:42:04'),
(11, 622264, '2017-11-22', '782735', '0.6648482564341699', '5204', '0.01', '0.07', '1.6141429669485012', '84', '0.62', '52.24', 'USD', '2017-11-23 14:42:04', '2017-11-23 14:42:04'),
(12, 622264, '2017-11-23', '1317140', '0.1235252137206371', '1627', '0.02', '0.02', '0.1843884449907806', '3', '8.28', '24.84', 'USD', '2017-11-23 14:42:04', '2017-11-23 14:42:04'),
(13, 718747, '2017-11-22', '243947', '0.3492561908939237', '852', '0.01', '0.03', '0.0', '0', '0.0', '8.52', 'USD', '2017-11-23 14:42:19', '2017-11-23 14:42:19'),
(14, 718749, '2017-11-22', '1361486', '0.0373121721413221', '508', '0.01', '0.0', '0.0', '0', '0.0', '5.08', 'USD', '2017-11-23 14:42:19', '2017-11-23 14:42:19'),
(15, 718747, '2017-11-23', '68333', '0.3629285996517056', '248', '0.01', '0.04', '0.0', '0', '0.0', '2.48', 'USD', '2017-11-23 14:42:19', '2017-11-23 14:42:19'),
(16, 718749, '2017-11-23', '278791', '0.0423256130936795', '118', '0.01', '0.0', '0.0', '0', '0.0', '1.18', 'USD', '2017-11-23 14:42:19', '2017-11-23 14:42:19'),
(17, 802483, '2017-11-22', '548464', '0.0712900026255142', '391', '0.11', '0.08', '1.0230179028132993', '4', '10.54', '42.15', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(18, 802499, '2017-11-22', '205517', '0.4578696652831639', '941', '0.02', '0.09', '0.0', '0', '0.0', '18.82', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(19, 802483, '2017-11-23', '140738', '0.113686424419844', '160', '0.1', '0.11', '0.0', '0', '0.0', '16.0', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(20, 802499, '2017-11-23', '192559', '0.2014966841331748', '388', '0.02', '0.04', '0.0', '0', '0.0', '7.76', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(21, 731183, '2017-11-22', '0', '0.0', '0', '0.0', '0.0', '0.0', '0', '0.0', '0.0', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(22, 731218, '2017-11-23', '0', '0.0', '0', '0.0', '0.0', '0.0', '0', '0.0', '0.0', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(23, 731218, '2017-11-22', '0', '0.0', '0', '0.0', '0.0', '0.0', '0', '0.0', '0.0', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(24, 731183, '2017-11-23', '0', '0.0', '0', '0.0', '0.0', '0.0', '0', '0.0', '0.0', 'USD', '2017-11-23 14:42:35', '2017-11-23 14:42:35'),
(25, 755004, '2017-11-22', '497809', '0.0920031578376446', '458', '0.11', '0.1', '1.091703056768559', '5', '9.94', '49.72', 'USD', '2017-11-23 14:42:47', '2017-11-23 14:42:47'),
(26, 757069, '2017-11-22', '52327', '0.6669596957593594', '349', '0.04', '0.27', '0.8595988538681948', '3', '4.69', '14.08', 'USD', '2017-11-23 14:42:47', '2017-11-23 14:42:47'),
(27, 755004, '2017-11-23', '98308', '0.0915490092362778', '90', '0.12', '0.11', '0.0', '0', '0.0', '10.37', 'USD', '2017-11-23 14:42:47', '2017-11-23 14:42:47'),
(28, 757069, '2017-11-23', '54381', '0.1636601018738162', '89', '0.05', '0.08', '1.1235955056179776', '1', '4.38', '4.38', 'USD', '2017-11-23 14:42:47', '2017-11-23 14:42:47');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
