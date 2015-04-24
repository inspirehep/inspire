-- MySQL dump 10.15  Distrib 10.0.17-MariaDB, for Linux (x86_64)
--
-- Host: inspire01    Database: inspirehep
-- ------------------------------------------------------
-- Server version	10.0.17-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `idxINDEX`
--

INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (1,'global','global','2015-04-24 09:23:32','en','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (2,'collection','collection','2015-04-24 09:42:21','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (3,'author','author','2015-04-23 23:43:10','','native','','No','No','No','BibIndexAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (4,'keyword','keyword','2015-04-24 09:37:04','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (5,'reference','reference','2015-04-24 09:46:53','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (6,'reportnumber','reportnumber','2015-04-24 09:43:42','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (7,'title','title','2015-04-24 09:36:43','en','native','INDEX-SYNONYM-TITLE,exact','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (8,'year','year','2015-04-24 09:52:50','','native','','No','No','No','BibIndexYearTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (9,'journal','journal','2015-04-24 09:42:41','','native','','No','No','No','BibIndexJournalTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (10,'affiliation','affiliation','2015-04-24 09:44:22','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (11,'collaboration','collaboration','2015-04-24 09:45:18','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (12,'exactauthor','exactauthor','2015-04-24 05:29:10','','native','','No','No','No','BibIndexExactAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (14,'caption','caption','2015-04-24 09:47:03','en','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (13,'fulltext','fulltext','2015-04-23 18:31:36','en','SOLR','','No','No','No','BibIndexFulltextTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (15,'firstauthor','firstauthor','2015-04-24 05:29:10','','native','','No','No','No','BibIndexAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (16,'address','address','2015-04-24 09:56:58','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (17,'postalcode','postal code','2015-04-24 09:43:57','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (18,'subject','subject','2015-04-24 09:59:36','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (19,'exactfirstauthor','exactfirstauthor','2015-04-24 05:29:10','','native','','No','No','No','BibIndexExactAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (20,'authorcount','This index contains number of authors of the record.','2015-04-24 05:29:10','','native','','No','No','No','BibIndexAuthorCountTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (21,'hepdataparent','','2015-04-24 09:09:13','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (22,'note','','2015-04-24 09:49:58','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (23,'publisher','','2015-04-24 10:06:16','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (25,'exacttitle','','2015-04-24 09:52:30','','native','','No','No','No','BibIndexDefaultTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (26,'country','This index contains country names of the affiliated institutes of the authors.','2015-04-24 10:02:29','','native','','','','','BibIndexCountryTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (27,'journalpage','','2015-04-24 10:17:31','','native','','','','','BibIndexJournalPageTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (24,'firstauthor_unicode','','2015-03-23 15:53:18','','native','','','No','No','BibIndexAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (28,'exactfirstauthor_unicode','','2015-03-23 15:53:18','','native','','','No','No','BibIndexExactAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (29,'author_cloned','author','2015-03-29 23:07:21','','native','','No','No','No','BibIndexAuthorTokenizer');
INSERT INTO `idxINDEX` (`id`, `name`, `description`, `last_updated`, `stemming_language`, `indexer`, `synonym_kbrs`, `remove_stopwords`, `remove_html_markup`, `remove_latex_markup`, `tokenizer`) VALUES (30,'exactauthor_cloned','exactauthor','2015-03-29 23:07:21','','native','','No','No','No','BibIndexExactAuthorTokenizer');

--
-- Dumping data for table `idxINDEX_field`
--

INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (1,1,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (2,9,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (3,3,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (4,5,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (5,8,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (6,6,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (7,2,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (8,10,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (9,13,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (10,15,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (11,16,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (12,17,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (14,23,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (13,22,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (15,24,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (16,25,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (17,26,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (10,30,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (1,25,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (19,38,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (18,7,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (20,39,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (21,43,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (22,44,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (23,46,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (25,49,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (26,27,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (27,54,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (28,38,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (24,24,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (29,3,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
INSERT INTO `idxINDEX_field` (`id_idxINDEX`, `id_field`, `regexp_punctuation`, `regexp_alphanumeric_separators`) VALUES (30,17,'[.,:;?!\"]','[!\"#$\\%&\'()*+,-./:;<=>?@[\\]^\\_`{|}~]');
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-04-24 10:19:01
