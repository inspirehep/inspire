-- MySQL dump 10.15  Distrib 10.0.17-MariaDB, for Linux (x86_64)
--
-- Host: inspire01    Database: inspirehep
-- ------------------------------------------------------
-- Server version	10.0.22-MariaDB-log

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
-- Table structure for table `idxINDEX`
--

DROP TABLE IF EXISTS `idxINDEX`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxINDEX` (
  `id` mediumint(9) unsigned NOT NULL,
  `name` varchar(50) NOT NULL DEFAULT '',
  `description` varchar(255) NOT NULL DEFAULT '',
  `last_updated` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `stemming_language` varchar(10) NOT NULL DEFAULT '',
  `indexer` varchar(10) NOT NULL DEFAULT 'native',
  `synonym_kbrs` varchar(255) NOT NULL DEFAULT '',
  `remove_stopwords` varchar(255) NOT NULL DEFAULT '',
  `remove_html_markup` varchar(10) NOT NULL DEFAULT '',
  `remove_latex_markup` varchar(10) NOT NULL DEFAULT '',
  `tokenizer` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxINDEXNAME`
--

DROP TABLE IF EXISTS `idxINDEXNAME`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxINDEXNAME` (
  `id_idxINDEX` mediumint(9) unsigned NOT NULL,
  `ln` char(5) NOT NULL DEFAULT '',
  `type` char(3) NOT NULL DEFAULT 'sn',
  `value` varchar(255) NOT NULL,
  PRIMARY KEY (`id_idxINDEX`,`ln`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxINDEX_field`
--

DROP TABLE IF EXISTS `idxINDEX_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxINDEX_field` (
  `id_idxINDEX` mediumint(9) unsigned NOT NULL,
  `id_field` mediumint(9) unsigned NOT NULL,
  `regexp_punctuation` varchar(255) NOT NULL DEFAULT '[.,:;?!"]',
  `regexp_alphanumeric_separators` varchar(255) NOT NULL DEFAULT '[!"#$\\%&''()*+,-./:;<=>?@[\\]^\\_`{|}~]',
  PRIMARY KEY (`id_idxINDEX`,`id_field`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxINDEX_idxINDEX`
--

DROP TABLE IF EXISTS `idxINDEX_idxINDEX`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxINDEX_idxINDEX` (
  `id_virtual` mediumint(9) unsigned NOT NULL,
  `id_normal` mediumint(9) unsigned NOT NULL,
  PRIMARY KEY (`id_virtual`,`id_normal`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR01F`
--

DROP TABLE IF EXISTS `idxPAIR01F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR01F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=10236867 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR01Q`
--

DROP TABLE IF EXISTS `idxPAIR01Q`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR01Q` (
  `id` mediumint(10) unsigned NOT NULL AUTO_INCREMENT,
  `runtime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `id_bibrec_low` mediumint(9) unsigned NOT NULL,
  `id_bibrec_high` mediumint(9) unsigned NOT NULL,
  `index_name` varchar(50) NOT NULL DEFAULT '',
  `mode` varchar(50) NOT NULL DEFAULT 'update',
  PRIMARY KEY (`id`),
  KEY `index_name` (`index_name`),
  KEY `runtime` (`runtime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR01R`
--

DROP TABLE IF EXISTS `idxPAIR01R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR01R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR02F`
--

DROP TABLE IF EXISTS `idxPAIR02F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR02F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=66 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR02R`
--

DROP TABLE IF EXISTS `idxPAIR02R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR02R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR03F`
--

DROP TABLE IF EXISTS `idxPAIR03F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR03F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=965899 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR03R`
--

DROP TABLE IF EXISTS `idxPAIR03R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR03R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR04F`
--

DROP TABLE IF EXISTS `idxPAIR04F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR04F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=231494 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR04R`
--

DROP TABLE IF EXISTS `idxPAIR04R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR04R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR05F`
--

DROP TABLE IF EXISTS `idxPAIR05F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR05F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=2261314 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR05R`
--

DROP TABLE IF EXISTS `idxPAIR05R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR05R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR06F`
--

DROP TABLE IF EXISTS `idxPAIR06F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR06F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=774476 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR06R`
--

DROP TABLE IF EXISTS `idxPAIR06R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR06R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR07F`
--

DROP TABLE IF EXISTS `idxPAIR07F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR07F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1208166 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR07R`
--

DROP TABLE IF EXISTS `idxPAIR07R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR07R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR08F`
--

DROP TABLE IF EXISTS `idxPAIR08F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR08F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=4240 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR08R`
--

DROP TABLE IF EXISTS `idxPAIR08R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR08R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR09F`
--

DROP TABLE IF EXISTS `idxPAIR09F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR09F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(255) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1720744 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR09R`
--

DROP TABLE IF EXISTS `idxPAIR09R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR09R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR10F`
--

DROP TABLE IF EXISTS `idxPAIR10F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR10F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=87084 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR10R`
--

DROP TABLE IF EXISTS `idxPAIR10R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR10R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR11F`
--

DROP TABLE IF EXISTS `idxPAIR11F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR11F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=7052 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR11R`
--

DROP TABLE IF EXISTS `idxPAIR11R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR11R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR12F`
--

DROP TABLE IF EXISTS `idxPAIR12F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR12F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=960918 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR12R`
--

DROP TABLE IF EXISTS `idxPAIR12R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR12R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR13F`
--

DROP TABLE IF EXISTS `idxPAIR13F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR13F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR13R`
--

DROP TABLE IF EXISTS `idxPAIR13R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR13R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR14F`
--

DROP TABLE IF EXISTS `idxPAIR14F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR14F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=4427687 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR14R`
--

DROP TABLE IF EXISTS `idxPAIR14R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR14R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR15F`
--

DROP TABLE IF EXISTS `idxPAIR15F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR15F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=764799 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR15R`
--

DROP TABLE IF EXISTS `idxPAIR15R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR15R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR16F`
--

DROP TABLE IF EXISTS `idxPAIR16F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR16F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=73702 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR16R`
--

DROP TABLE IF EXISTS `idxPAIR16R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR16R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR17F`
--

DROP TABLE IF EXISTS `idxPAIR17F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR17F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=397 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR17R`
--

DROP TABLE IF EXISTS `idxPAIR17R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR17R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR18F`
--

DROP TABLE IF EXISTS `idxPAIR18F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR18F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1343 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR18R`
--

DROP TABLE IF EXISTS `idxPAIR18R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR18R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR19F`
--

DROP TABLE IF EXISTS `idxPAIR19F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR19F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=764748 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR19R`
--

DROP TABLE IF EXISTS `idxPAIR19R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR19R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR20F`
--

DROP TABLE IF EXISTS `idxPAIR20F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR20F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=282920 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR20R`
--

DROP TABLE IF EXISTS `idxPAIR20R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR20R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR21F`
--

DROP TABLE IF EXISTS `idxPAIR21F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR21F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR21R`
--

DROP TABLE IF EXISTS `idxPAIR21R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR21R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR22F`
--

DROP TABLE IF EXISTS `idxPAIR22F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR22F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=453389 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR22R`
--

DROP TABLE IF EXISTS `idxPAIR22R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR22R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR23F`
--

DROP TABLE IF EXISTS `idxPAIR23F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR23F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=636 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR23R`
--

DROP TABLE IF EXISTS `idxPAIR23R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR23R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR25F`
--

DROP TABLE IF EXISTS `idxPAIR25F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR25F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1379847 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR25R`
--

DROP TABLE IF EXISTS `idxPAIR25R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR25R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR26F`
--

DROP TABLE IF EXISTS `idxPAIR26F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR26F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=118 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR26R`
--

DROP TABLE IF EXISTS `idxPAIR26R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR26R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR27F`
--

DROP TABLE IF EXISTS `idxPAIR27F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR27F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=147290 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR27R`
--

DROP TABLE IF EXISTS `idxPAIR27R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR27R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR31F`
--

DROP TABLE IF EXISTS `idxPAIR31F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR31F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(100) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=854 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPAIR31R`
--

DROP TABLE IF EXISTS `idxPAIR31R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPAIR31R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE01F`
--

DROP TABLE IF EXISTS `idxPHRASE01F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE01F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text COLLATE utf8_unicode_520_ci,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=8692955 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE01Q`
--

DROP TABLE IF EXISTS `idxPHRASE01Q`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE01Q` (
  `id` mediumint(10) unsigned NOT NULL AUTO_INCREMENT,
  `runtime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `id_bibrec_low` mediumint(9) unsigned NOT NULL,
  `id_bibrec_high` mediumint(9) unsigned NOT NULL,
  `index_name` varchar(50) NOT NULL DEFAULT '',
  `mode` varchar(50) NOT NULL DEFAULT 'update',
  PRIMARY KEY (`id`),
  KEY `index_name` (`index_name`),
  KEY `runtime` (`runtime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE01R`
--

DROP TABLE IF EXISTS `idxPHRASE01R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE01R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE02F`
--

DROP TABLE IF EXISTS `idxPHRASE02F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE02F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=102 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE02R`
--

DROP TABLE IF EXISTS `idxPHRASE02R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE02R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE03F`
--

DROP TABLE IF EXISTS `idxPHRASE03F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE03F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text COLLATE utf8_unicode_520_ci,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=2817148 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE03R`
--

DROP TABLE IF EXISTS `idxPHRASE03R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE03R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE04F`
--

DROP TABLE IF EXISTS `idxPHRASE04F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE04F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=383196 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE04R`
--

DROP TABLE IF EXISTS `idxPHRASE04R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE04R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE05F`
--

DROP TABLE IF EXISTS `idxPHRASE05F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE05F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=3595666 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE05R`
--

DROP TABLE IF EXISTS `idxPHRASE05R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE05R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE06F`
--

DROP TABLE IF EXISTS `idxPHRASE06F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE06F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=1012312 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE06R`
--

DROP TABLE IF EXISTS `idxPHRASE06R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE06R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE07F`
--

DROP TABLE IF EXISTS `idxPHRASE07F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE07F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=1429807 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE07R`
--

DROP TABLE IF EXISTS `idxPHRASE07R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE07R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE08F`
--

DROP TABLE IF EXISTS `idxPHRASE08F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE08F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=22161 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE08R`
--

DROP TABLE IF EXISTS `idxPHRASE08R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE08R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE09F`
--

DROP TABLE IF EXISTS `idxPHRASE09F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE09F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=1725326 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE09R`
--

DROP TABLE IF EXISTS `idxPHRASE09R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE09R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE10F`
--

DROP TABLE IF EXISTS `idxPHRASE10F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE10F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=74069 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE10R`
--

DROP TABLE IF EXISTS `idxPHRASE10R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE10R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE11F`
--

DROP TABLE IF EXISTS `idxPHRASE11F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE11F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=6732 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE11R`
--

DROP TABLE IF EXISTS `idxPHRASE11R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE11R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE12F`
--

DROP TABLE IF EXISTS `idxPHRASE12F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE12F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text COLLATE utf8_unicode_520_ci,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=1020950 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE12R`
--

DROP TABLE IF EXISTS `idxPHRASE12R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE12R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE13F`
--

DROP TABLE IF EXISTS `idxPHRASE13F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE13F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE13R`
--

DROP TABLE IF EXISTS `idxPHRASE13R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE13R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE14F`
--

DROP TABLE IF EXISTS `idxPHRASE14F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE14F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=2077917 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE14R`
--

DROP TABLE IF EXISTS `idxPHRASE14R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE14R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE15F`
--

DROP TABLE IF EXISTS `idxPHRASE15F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE15F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text COLLATE utf8_unicode_520_ci,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=1860682 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE15R`
--

DROP TABLE IF EXISTS `idxPHRASE15R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE15R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE16F`
--

DROP TABLE IF EXISTS `idxPHRASE16F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE16F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=65228 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE16R`
--

DROP TABLE IF EXISTS `idxPHRASE16R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE16R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE17F`
--

DROP TABLE IF EXISTS `idxPHRASE17F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE17F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=3112 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE17R`
--

DROP TABLE IF EXISTS `idxPHRASE17R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE17R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE18F`
--

DROP TABLE IF EXISTS `idxPHRASE18F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE18F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=540 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE18R`
--

DROP TABLE IF EXISTS `idxPHRASE18R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE18R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE19F`
--

DROP TABLE IF EXISTS `idxPHRASE19F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE19F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text COLLATE utf8_unicode_520_ci,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=771497 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE19R`
--

DROP TABLE IF EXISTS `idxPHRASE19R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE19R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE20F`
--

DROP TABLE IF EXISTS `idxPHRASE20F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE20F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=282910 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE20R`
--

DROP TABLE IF EXISTS `idxPHRASE20R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE20R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE21F`
--

DROP TABLE IF EXISTS `idxPHRASE21F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE21F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=8129 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE21R`
--

DROP TABLE IF EXISTS `idxPHRASE21R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE21R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE22F`
--

DROP TABLE IF EXISTS `idxPHRASE22F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE22F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=189008 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE22R`
--

DROP TABLE IF EXISTS `idxPHRASE22R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE22R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE23F`
--

DROP TABLE IF EXISTS `idxPHRASE23F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE23F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=470 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE23R`
--

DROP TABLE IF EXISTS `idxPHRASE23R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE23R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE25F`
--

DROP TABLE IF EXISTS `idxPHRASE25F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE25F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=2407792 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE25R`
--

DROP TABLE IF EXISTS `idxPHRASE25R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE25R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE26F`
--

DROP TABLE IF EXISTS `idxPHRASE26F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE26F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=508 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE26R`
--

DROP TABLE IF EXISTS `idxPHRASE26R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE26R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE27F`
--

DROP TABLE IF EXISTS `idxPHRASE27F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE27F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=147292 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE27R`
--

DROP TABLE IF EXISTS `idxPHRASE27R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE27R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE31F`
--

DROP TABLE IF EXISTS `idxPHRASE31F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE31F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` text,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  KEY `term` (`term`(50))
) ENGINE=MyISAM AUTO_INCREMENT=854 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxPHRASE31R`
--

DROP TABLE IF EXISTS `idxPHRASE31R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxPHRASE31R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD01F`
--

DROP TABLE IF EXISTS `idxWORD01F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD01F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=8141481 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD01Q`
--

DROP TABLE IF EXISTS `idxWORD01Q`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD01Q` (
  `id` mediumint(10) unsigned NOT NULL AUTO_INCREMENT,
  `runtime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `id_bibrec_low` mediumint(9) unsigned NOT NULL,
  `id_bibrec_high` mediumint(9) unsigned NOT NULL,
  `index_name` varchar(50) NOT NULL DEFAULT '',
  `mode` varchar(50) NOT NULL DEFAULT 'update',
  PRIMARY KEY (`id`),
  KEY `index_name` (`index_name`),
  KEY `runtime` (`runtime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD01R`
--

DROP TABLE IF EXISTS `idxWORD01R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD01R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD02F`
--

DROP TABLE IF EXISTS `idxWORD02F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD02F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=158 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD02R`
--

DROP TABLE IF EXISTS `idxWORD02R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD02R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD03F`
--

DROP TABLE IF EXISTS `idxWORD03F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD03F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=528794 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD03R`
--

DROP TABLE IF EXISTS `idxWORD03R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD03R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD04F`
--

DROP TABLE IF EXISTS `idxWORD04F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD04F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=79389 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD04R`
--

DROP TABLE IF EXISTS `idxWORD04R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD04R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD05F`
--

DROP TABLE IF EXISTS `idxWORD05F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD05F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=3800009 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD05R`
--

DROP TABLE IF EXISTS `idxWORD05R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD05R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD06F`
--

DROP TABLE IF EXISTS `idxWORD06F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD06F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1420539 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD06R`
--

DROP TABLE IF EXISTS `idxWORD06R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD06R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD07F`
--

DROP TABLE IF EXISTS `idxWORD07F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD07F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=279459 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD07R`
--

DROP TABLE IF EXISTS `idxWORD07R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD07R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD08F`
--

DROP TABLE IF EXISTS `idxWORD08F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD08F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=21101 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD08R`
--

DROP TABLE IF EXISTS `idxWORD08R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD08R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD09F`
--

DROP TABLE IF EXISTS `idxWORD09F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD09F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(255) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1659740 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD09R`
--

DROP TABLE IF EXISTS `idxWORD09R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD09R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD10F`
--

DROP TABLE IF EXISTS `idxWORD10F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD10F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=42644 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD10R`
--

DROP TABLE IF EXISTS `idxWORD10R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD10R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD11F`
--

DROP TABLE IF EXISTS `idxWORD11F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD11F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=7021 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD11R`
--

DROP TABLE IF EXISTS `idxWORD11R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD11R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD12F`
--

DROP TABLE IF EXISTS `idxWORD12F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD12F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=574014 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD12R`
--

DROP TABLE IF EXISTS `idxWORD12R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD12R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD13F`
--

DROP TABLE IF EXISTS `idxWORD13F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD13F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD13R`
--

DROP TABLE IF EXISTS `idxWORD13R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD13R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD14F`
--

DROP TABLE IF EXISTS `idxWORD14F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD14F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=2814426 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD14R`
--

DROP TABLE IF EXISTS `idxWORD14R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD14R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD15F`
--

DROP TABLE IF EXISTS `idxWORD15F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD15F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=465214 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD15R`
--

DROP TABLE IF EXISTS `idxWORD15R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD15R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD16F`
--

DROP TABLE IF EXISTS `idxWORD16F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD16F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=39269 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD16R`
--

DROP TABLE IF EXISTS `idxWORD16R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD16R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD17F`
--

DROP TABLE IF EXISTS `idxWORD17F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD17F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=3540 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD17R`
--

DROP TABLE IF EXISTS `idxWORD17R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD17R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD18F`
--

DROP TABLE IF EXISTS `idxWORD18F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD18F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=1315 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD18R`
--

DROP TABLE IF EXISTS `idxWORD18R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD18R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD19F`
--

DROP TABLE IF EXISTS `idxWORD19F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD19F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) COLLATE utf8_unicode_520_ci DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=496359 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD19R`
--

DROP TABLE IF EXISTS `idxWORD19R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD19R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD20F`
--

DROP TABLE IF EXISTS `idxWORD20F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD20F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=282923 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD20R`
--

DROP TABLE IF EXISTS `idxWORD20R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD20R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD21F`
--

DROP TABLE IF EXISTS `idxWORD21F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD21F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=8129 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD21R`
--

DROP TABLE IF EXISTS `idxWORD21R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD21R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD22F`
--

DROP TABLE IF EXISTS `idxWORD22F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD22F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=183115 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD22R`
--

DROP TABLE IF EXISTS `idxWORD22R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD22R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD23F`
--

DROP TABLE IF EXISTS `idxWORD23F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD23F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=648 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD23R`
--

DROP TABLE IF EXISTS `idxWORD23R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD23R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD25F`
--

DROP TABLE IF EXISTS `idxWORD25F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD25F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=301834 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD25R`
--

DROP TABLE IF EXISTS `idxWORD25R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD25R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD26F`
--

DROP TABLE IF EXISTS `idxWORD26F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD26F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=569 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD26R`
--

DROP TABLE IF EXISTS `idxWORD26R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD26R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD27F`
--

DROP TABLE IF EXISTS `idxWORD27F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD27F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=147288 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD27R`
--

DROP TABLE IF EXISTS `idxWORD27R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD27R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD31F`
--

DROP TABLE IF EXISTS `idxWORD31F`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD31F` (
  `id` mediumint(9) unsigned NOT NULL AUTO_INCREMENT,
  `term` varchar(50) DEFAULT NULL,
  `hitlist` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `term` (`term`)
) ENGINE=MyISAM AUTO_INCREMENT=854 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idxWORD31R`
--

DROP TABLE IF EXISTS `idxWORD31R`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idxWORD31R` (
  `id_bibrec` mediumint(9) unsigned NOT NULL,
  `termlist` longblob,
  `type` enum('CURRENT','FUTURE','TEMPORARY') NOT NULL DEFAULT 'CURRENT',
  PRIMARY KEY (`id_bibrec`,`type`),
  KEY `type` (`type`)
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

-- Dump completed on 2016-01-05 14:10:38
