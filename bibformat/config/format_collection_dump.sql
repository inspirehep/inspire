-- MySQL dump 10.13  Distrib 5.1.69, for redhat-linux-gnu (x86_64)
--
-- Host: 188.184.3.55    Database: inspirehep
-- ------------------------------------------------------
-- Server version	5.5.32-MariaDB-log

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
-- Dumping data for table `format`
--

INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (1,'HTML brief','hb','HTML brief output format, used for search results pages.','text/html',1,'2013-11-27 11:41:09');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (2,'HTML detailed','hd','HTML detailed output format, used for Detailed record pages.','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (3,'MARC','hm','HTML MARC.','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (4,'Dublin Core','xd','XML Dublin Core.','text/xml',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (5,'MARCXML','xm','XML MARC.','text/xml',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (6,'portfolio','hp','HTML portfolio-style output format for photos.','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (7,'photo captions only','hc','HTML caption-only output format for photos.','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (8,'BibTeX','hx','BibTeX.','text/html',1,'2013-11-27 11:43:28');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (9,'EndNote','xe','XML EndNote.','text/xml',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (10,'NLM','xn','XML NLM.','text/xml',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (11,'Excel','excel','Excel csv output','application/ms-excel',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (12,'HTML similarity','hs','Very short HTML output for similarity box (<i>people also viewed..</i>).','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (13,'RSS','xr','RSS.','text/xml',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (14,'OAI DC','xoaidc','OAI DC.','text/xml',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (15,'File mini-panel','hdfile','Used to show fulltext files in mini-panel of detailed record pages.','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (16,'Actions mini-panel','hdact','Used to display actions in mini-panel of detailed record pages.','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (17,'References tab','hdref','Display record references in References tab.','text/html',0,'2013-11-27 11:45:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (18,'HTML citesummary','hcs','HTML cite summary format, used for search results pages.','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (19,'RefWorks','xw','RefWorks.','text/xml',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (20,'MODS','xo','Metadata Object Description Schema','application/xml',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (21,'LaTeX (EU)','hlxe','LaTeX formatted reference (EU style)','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (22,'LaTeX (US)','hlxu','LaTeX formatted reference (US Style)','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (23,'INSPIRE Citation Format','hca','Very brief cite-as format used by reference submission form.','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (24,'INSPIRE Reference Submission Form','hrf','Reference submission form, used for user updates to reference lists.','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (25,'LaTeX CV','tlcv','A LaTeX CV','text/plain',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (26,'text CV','htcv','A plaintext CV','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (27,'HTML CV','hcv','A CV with hyperlinks','text/html',1,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (28,'Podcast','xp','Sample format suitable for multimedia feeds, such as podcasts','application/rss+xml',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (29,'AID HTML very brief','ha','AID HTML very brief output format, used by BAI.','text/html',0,'2013-11-27 11:42:45');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (30,'WebAuthorProfile','hwap','A WebAuthorProfile format.','text/html',0,'2013-02-05 00:00:00');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (31,'WebAuthorProfile data helper','wapdat','cPickled dicts','text',0,'2013-11-27 11:43:07');
INSERT INTO `format` (`id`, `name`, `code`, `description`, `content_type`, `visibility`, `last_updated`) VALUES (32,'WebAuthorProfile affiliations helper','wapaff','cPickled dicts','text',0,'2013-11-27 11:43:23');

--
-- Dumping data for table `collection_format`
--

INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (2,1,130);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (2,2,120);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,18,110);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,8,100);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,21,90);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,22,80);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,9,50);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,19,10);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,1,130);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (1,2,120);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (3,1,130);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (3,2,120);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (4,1,130);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (4,2,120);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (5,1,130);
INSERT INTO `collection_format` (`id_collection`, `id_format`, `score`) VALUES (5,2,120);
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-11-27 11:46:20
