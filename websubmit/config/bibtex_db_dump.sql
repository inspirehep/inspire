-- bibtex dump 2013-02-08 17:35:22 v1
-- Extra:NAMES (the following dump contains rows in sbmALLFUNCDESCR, sbmFUNDESC, sbmFIELD and sbmFIELDDESC tables which are not specific to this submission, but that include keyword bibtex)

DELETE FROM sbmFUNDESC WHERE function LIKE 'bibtex%';
DELETE FROM sbmFIELD WHERE subname LIKE '%bibtex';
DELETE FROM sbmFIELDDESC WHERE name LIKE 'bibtex%';
DELETE FROM sbmALLFUNCDESCR WHERE function LIKE 'bibtex%';
DELETE FROM sbmDOCTYPE WHERE sdocname='bibtex';
DELETE FROM sbmCATEGORIES WHERE doctype ='bibtex';
DELETE FROM sbmFUNCTIONS WHERE doctype='bibtex';
DELETE FROM sbmIMPLEMENT WHERE docname='bibtex';
DELETE FROM sbmPARAMETERS WHERE doctype='bibtex';
INSERT INTO sbmALLFUNCDESCR VALUES ('Bibtex','Convert laTex to BibTex');
INSERT INTO sbmCATEGORIES VALUES ('bibtex','bibtex','BiblioTools',1);
INSERT INTO sbmDOCTYPE VALUES ('BiblioTools: Generating Your Bibliography','bibtex','2012-11-27','2012-12-13','How to use INSPIRE to generate a LaTeX bibliography or .bib file\r\n\r\n<br />\r\nCite papers in your LaTeX file in the following way:<br />\r\n\r\n1.      INSPIRE Texkeys, e.g. \\cite{Beacom:2010kk} <br />\r\n\r\n2.      Eprint numbers, e.g. \\cite{1004.3311} or \\cite{hep-th/9711200}<br />\r\n\r\n<br /><br />\r\nYou can then upload your LaTeX file here to generate a list of the references in the order they are cited in your paper. The system will understand cite fields with multiple papers such as \\cite{ Beacom:2010kk, hep-th/9711200}.\r\n');
INSERT INTO sbmFIELD VALUES ('SBIbibtex',1,1,'BibTex_info','','O','','','2013-02-08','2013-02-08',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIbibtex',1,2,'BibTex_input','LaTeX File Name:','M','File that contains the LaTex references','','2013-02-08','2013-02-08',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIbibtex',1,3,'BibTex_format','Output Format:','O','Output Format (LaTex US, LaTex EU, or BibTex)	','','2013-02-08','2013-02-08',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIbibtex',1,4,'BibTex_submit','','M','','','2012-11-27','2013-02-08',NULL,NULL);
INSERT INTO sbmFIELDDESC VALUES ('BibTex_format',NULL,'','S',NULL,NULL,NULL,NULL,NULL,'<select name=\"OUT_FORMAT\">\r\n   <option value=\'hlxu\' select=\'true\'>LaTex US</option>\r\n   <option value=\'hlxe\'>LaTex EU</option>\r\n   <option value=\'hx\'>BibTex</option>\r\n</select>','2013-02-08','2013-02-08',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BibTex_info',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<table bgcolor=\"#D3E3E2\">\r\n<tr><td>\r\n<div align=\"left\">\r\n<h1>BiblioTools: Generating Your Bibliography</h1>\r\n<h2>How to use INSPIRE to generate a LaTeX bibliography or .bib file</h2>\r\n<br /><br />\r\nCite papers in your LaTeX file in the following way:\r\n<ol>\r\n  <li>INSPIRE Texkeys, e.g. \\cite{Beacom:2010kk}</li>\r\n  <li>Eprint numbers, e.g. \\cite{1004.3311} or \\cite{hep-th/9711200}</li>\r\n</ol>\r\n<p>\r\nYou can then upload your LaTeX file here to generate a list of the references in the order they are cited in your paper. The system will understand cite fields with multiple papers such as \\cite{Beacom:2010kk, hep-th/9711200}. Note that if you combine multiple papers under a single texkey only the one belonging to the texkey will show up, the others will not.\r\n</p>\r\n</div>\r\n<br />\r\n','2013-02-08','2013-02-08',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BibTex_input',NULL,'','F',NULL,NULL,NULL,NULL,NULL,NULL,'2013-02-08','2013-02-08','File that contains the LaTex references',NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BibTex_submit',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<br /><br />\r\n<INPUT TYPE=\"button\" class=\"submissionbutton\" width=\"400\" height=\"50\" name=\"BibTex_submit\" value=\"Submit\" onclick=\"finish();\">\r\n</tr></td></table>\r\n','2012-11-27','2012-12-13',NULL,NULL,0);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','bibtex','Bibtex',10,1);
INSERT INTO sbmFUNDESC VALUES ('Bibtex','edsrn');
INSERT INTO sbmFUNDESC VALUES ('Bibtex','newrnin');
INSERT INTO sbmFUNDESC VALUES ('Bibtex','status');
INSERT INTO sbmIMPLEMENT VALUES ('bibtex','SBI','Y','SBIbibtex',1,'2012-11-27','2013-02-08',1,'','',0,0,'');
