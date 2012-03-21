-- MySQL dump 10.11
--
-- Host: localhost    Database: inspiretest
-- ------------------------------------------------------
-- Server version	5.0.95-log
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `idxINDEX`
--

INSERT INTO `idxINDEX` VALUES (1,'global','global','2012-10-19 12:30:29','en');
INSERT INTO `idxINDEX` VALUES (2,'collection','collection','2012-08-06 17:52:28','');
INSERT INTO `idxINDEX` VALUES (3,'author','author','2012-04-22 20:33:21','');
INSERT INTO `idxINDEX` VALUES (4,'keyword','keyword','2012-04-22 20:35:22','');
INSERT INTO `idxINDEX` VALUES (5,'reference','reference','2012-04-22 20:35:37','');
INSERT INTO `idxINDEX` VALUES (6,'reportnumber','reportnumber','2012-04-22 20:34:12','');
INSERT INTO `idxINDEX` VALUES (7,'title','title','2012-04-22 20:34:12','en');
INSERT INTO `idxINDEX` VALUES (8,'year','year','2012-04-22 20:34:12','');
INSERT INTO `idxINDEX` VALUES (9,'journal','journal','2012-04-22 20:34:12','');
INSERT INTO `idxINDEX` VALUES (10,'affiliation','affiliation','2012-04-22 20:34:12','');
INSERT INTO `idxINDEX` VALUES (11,'collaboration','collaboration','2012-04-22 20:34:12','');
INSERT INTO `idxINDEX` VALUES (12,'exactauthor','exactauthor','2012-04-22 20:33:21','');
INSERT INTO `idxINDEX` VALUES (14,'caption','caption','2012-04-22 20:34:12','en');
INSERT INTO `idxINDEX` VALUES (13,'fulltext','fulltext','2012-04-22 20:35:37','en');
INSERT INTO `idxINDEX` VALUES (15,'firstauthor','firstauthor','2012-04-22 20:33:21','en');
INSERT INTO `idxINDEX` VALUES (16,'address','address','2012-04-22 20:34:12','en');
INSERT INTO `idxINDEX` VALUES (17,'postalcode','postal code','2012-04-22 20:34:12','');
INSERT INTO `idxINDEX` VALUES (18,'subject','subject','2012-04-22 20:34:12','en');
INSERT INTO `idxINDEX` VALUES (19,'exactfirstauthor','exactfirstauthor','2012-04-22 20:33:21','');
INSERT INTO `idxINDEX` VALUES (20,'authorcount','This index contains number of authors of the record.','2012-04-22 20:33:21','');
INSERT INTO `idxINDEX` VALUES (21,'hepdataparent','link for HepData records','2012-10-19 14:15:41','');
INSERT INTO `idxINDEX` VALUES (22,'note','','0000-00-00 00:00:00','');

--
-- Dumping data for table `idxINDEX_field`
--

INSERT INTO `idxINDEX_field` VALUES (1,1,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (2,9,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (3,3,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (4,5,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (5,8,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (6,6,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (7,2,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (8,10,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (9,13,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (10,15,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (11,16,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (12,17,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (14,23,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (13,22,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (15,24,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (16,25,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (17,26,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (10,30,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (1,25,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (19,38,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (18,7,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (20,39,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (21,43,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` VALUES (22,44,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-11-01 10:03:39
