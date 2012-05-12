-- MySQL dump 10.13  Distrib 5.1.52, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: billing
-- ------------------------------------------------------
-- Server version	5.1.52

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `metrics`
--

DROP TABLE IF EXISTS `metrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metrics` (
  `mtype` varchar(36) NOT NULL,
  `time_type` int(11) NOT NULL,
  `aggregate` bit(1) NOT NULL,
  `time_dimention_koef` int(11) NOT NULL,
  `count_dimention_koef` int(11) NOT NULL,
  `count_dimention_type` varchar(45) NOT NULL,
  PRIMARY KEY (`mtype`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue_skeleton`
--

DROP TABLE IF EXISTS `queue_skeleton`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue_skeleton` (
  `uuid` varchar(36) NOT NULL,
  `customer` varchar(36) NOT NULL,
  `rid` varchar(36) NOT NULL,
  `rate` bigint(20) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `state` enum('DONE','PROCESSING','AGGREGATE') NOT NULL,
  `value` bigint(20) NOT NULL DEFAULT '1',
  `time_now` int(11) NOT NULL,
  `time_check` int(11) NOT NULL,
  `time_create` int(11) NOT NULL,
  `time_destroy` int(11) NOT NULL,
  `target_user` varchar(36) DEFAULT NULL,
  `target_uuid` varchar(36) DEFAULT NULL,
  `target_description` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  UNIQUE KEY `uuid_UNIQUE` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rates`
--

DROP TABLE IF EXISTS `rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rates` (
  `rid` varchar(36) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `mtype` varchar(36) NOT NULL,
  `tariff_id` varchar(36) NOT NULL,
  `rate_value` bigint(20) NOT NULL,
  `rate_currency` enum('RUR','USD','EUR') NOT NULL,
  `state` enum('ACTIVE','ARCHIVE','UPDATING') NOT NULL,
  `time_create` int(11) NOT NULL,
  `time_destroy` int(11) NOT NULL,
  `arg` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`rid`),
  UNIQUE KEY `rid_UNIQUE` (`rid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tariffs`
--

DROP TABLE IF EXISTS `tariffs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tariffs` (
  `tariff_id` varchar(36) NOT NULL,
  `name` varchar(45) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `currency` enum('RUR','USD','EUR') NOT NULL,
  `create_time` int(11) NOT NULL,
  `state` enum('ARCHIVE','ACTIVE') NOT NULL,
  PRIMARY KEY (`tariff_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-05-10 18:41:26
