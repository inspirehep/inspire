<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id$

     This file is part of Invenio.
     Copyright (C) 2007, 2008, 2009, 2010, 2011 CERN.

     Invenio is free software; you can redistribute it and/or
     modify it under the terms of the GNU General Public License as
     published by the Free Software Foundation; either version 2 of the
     License, or (at your option) any later version.

     Invenio is distributed in the hope that it will be useful, but
     WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
     General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with Invenio; if not, write to the Free Software Foundation, Inc.,
     59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
-->
<!--
<name>RSS</name>
<description>RSS</description>
-->
<!--

This stylesheet transforms a MARCXML input into a RSS output.
This stylesheet is provided only as an example of transformation.

-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:fn="http://cdsweb.cern.ch/bibformat/fn" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" version="1.0" exclude-result-prefixes="marc fn dc dcterms">
  <xsl:output method="xml" indent="yes" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <xsl:if test="collection">
      <xsl:for-each select="collection">
        <xsl:for-each select="record">
          <item>
            <xsl:apply-templates select="."/>
          </item>
        </xsl:for-each>
      </xsl:for-each>
    </xsl:if>
    <xsl:if test="record">
      <item>
        <xsl:apply-templates/>
      </item>
    </xsl:if>
  </xsl:template>
  <xsl:template match="record">
    <!-- match case insensitive -->
    <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'"/>
    <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
    <xsl:variable name="CC">
    <xsl:for-each select="datafield[@tag='980']">
      <xsl:if test="'CORE' != normalize-space(translate(subfield[@code='a'], $lowercase, $uppercase))">
	  <xsl:value-of select="normalize-space(translate(subfield[@code='a'], $lowercase, $uppercase))"/>
	  <xsl:text>+</xsl:text>
      </xsl:if>
    </xsl:for-each>
    </xsl:variable>
    <xsl:variable name="SPIRES">
      <xsl:value-of select="normalize-space(translate(datafield[@tag='970']/subfield[@code='a'], $lowercase, $uppercase))"/>
    </xsl:variable>
    <!--
	RSS for HEP collection: 980__a:HEP and 970__a:SPIRES-\d+
    -->
    <xsl:choose>
      <xsl:when test="contains($CC, 'HEP+') or contains($SPIRES, 'SPIRES-')">
        <title>
          <xsl:for-each select="datafield[@tag='245']">
            <xsl:value-of select="subfield[@code='a']"/>
            <xsl:if test="subfield[@code='b']">
              <xsl:text>: </xsl:text>
              <xsl:value-of select="subfield[@code='b']"/>
            </xsl:if>
            <xsl:if test="datafield[@tag='710']/subfield[@code='g']">
              <xsl:text>, </xsl:text>
              <xsl:value-of select="datafield[@tag='710']/subfield[@code='g']"/>
            </xsl:if>
          </xsl:for-each>
          <xsl:for-each select="datafield[@tag='111']">
            <xsl:value-of select="subfield[@code='a']"/>
          </xsl:for-each>
        </title>
        <link>
          <xsl:value-of select="fn:eval_bibformat(controlfield[@tag=001],'&lt;BFE_SERVER_INFO var=&quot;recurl&quot;&gt;')"/>
        </link>
        <xsl:if test="datafield[@tag='037']/subfield[@code='c']">
          <category>
            <xsl:value-of select="datafield[@tag='037']/subfield[@code='c']"/>
          </category>
        </xsl:if>
        <description>
          <xsl:if test="datafield[@tag='037']/subfield[@code='a']">
            <xsl:for-each select="datafield[@tag='037']">
              <xsl:value-of select="subfield[@code='a']"/>
              <xsl:text>&lt;br /&gt;</xsl:text>
            </xsl:for-each>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="datafield[@tag='773']/subfield[@code='p']!=''">
              <xsl:for-each select="datafield[@tag='773']">
                <xsl:if test="subfield[@code='p']!=''">
                  <xsl:if test="subfield[@code='p']">
                    <xsl:value-of select="subfield[@code='p']"/>
                    <xsl:if test="subfield[@code='v']">
                      <xsl:text> </xsl:text>
                      <xsl:value-of select="subfield[@code='v']"/>
                    </xsl:if>
                    <xsl:if test="subfield[@code='y']">
                      <xsl:text> (</xsl:text>
                      <xsl:value-of select="subfield[@code='y']"/>
                      <xsl:text>)</xsl:text>
                    </xsl:if>
                    <xsl:if test="subfield[@code='c']">
                      <xsl:text> </xsl:text>
                      <xsl:value-of select="subfield[@code='c']"/>
                    </xsl:if>
                    <xsl:text>&lt;br /&gt;</xsl:text>
                  </xsl:if>
                </xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:if test="datafield[@tag='773']/subfield[@code='x']">
                <xsl:value-of select="datafield[@tag='773']/subfield[@code='x']"/>
                <xsl:text>&lt;br /&gt;</xsl:text>
              </xsl:if>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:if test="datafield[(@tag='100' or @tag='110' or @tag='710')]/subfield[@code='a']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:text>by: </xsl:text>
            <xsl:value-of select="datafield[(@tag='100' or @tag='110' or @tag='710')]/subfield[@code='a']"/>
          </xsl:if>
          <xsl:if test="datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='u']">
            <xsl:text> (</xsl:text>
            <xsl:value-of select="datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='u']"/>
            <xsl:text>)</xsl:text>
            <xsl:if test="datafield[@tag='700']/subfield[@code='a']">
              <xsl:text> et al.</xsl:text>
            </xsl:if>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='520']/subfield[@code='a']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:text>&lt;strong&gt;Abstract:&lt;/strong&gt; </xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='520']/subfield[@code='a']"/>
          </xsl:if>
        </description>
        <xsl:choose>
          <xsl:when test="contains(datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='a'], '@')">
            <!-- Email address: we can use author -->
            <author>
              <xsl:value-of select="datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='a']"/>
            </author>
          </xsl:when>
          <xsl:otherwise>
            <dc:creator>
              <xsl:value-of select="datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='a']"/>
            </dc:creator>
          </xsl:otherwise>
        </xsl:choose>
        <pubDate>
          <xsl:value-of select="fn:creation_date(controlfield[@tag=001], '%a, %d %b %Y %H:%M:%S GMT')"/>
        </pubDate>
        <guid>
          <xsl:value-of select="fn:eval_bibformat(controlfield[@tag=001],'&lt;BFE_SERVER_INFO var=&quot;recurl&quot;&gt;')"/>
        </guid>
        <!-- Additional Dublic Core tags. Mainly used for books -->
        <xsl:for-each select="datafield[@tag='020' and @ind1=' ' and @ind2=' ']">
          <!-- ISBN -->
          <xsl:if test="subfield[@code='a']">
            <dc:identifier>urn:ISBN:<xsl:value-of select="subfield[@code='a']"/></dc:identifier>
          </xsl:if>
        </xsl:for-each>
        <xsl:for-each select="datafield[@tag='022' and @ind1=' ' and @ind2=' ']">
          <!-- ISSN -->
          <xsl:if test="subfield[@code='a']">
            <dc:identifier>urn:ISSN:<xsl:value-of select="subfield[@code='a']"/></dc:identifier>
          </xsl:if>
        </xsl:for-each>
        <xsl:if test="datafield[@tag='260' and @ind1=' ' and @ind2=' ']/subfield[@code='b']">
          <!-- Publisher -->
          <dc:publisher>
            <xsl:value-of select="datafield[@tag='260' and @ind1=' ' and @ind2=' ']/subfield[@code='b']"/>
          </dc:publisher>
        </xsl:if>
        <xsl:if test="datafield[@tag='260' and @ind1=' ' and @ind2=' ']/subfield[@code='c']">
          <!-- Date -->
          <dcterms:issued>
            <xsl:value-of select="datafield[@tag='260' and @ind1=' ' and @ind2=' ']/subfield[@code='c']"/>
          </dcterms:issued>
        </xsl:if>
      </xsl:when>
      <!--
RSS for JOB
-->
      <xsl:when test="contains($CC, 'JOB+')">
        <title>
          <xsl:if test="datafield[@tag='245']/subfield[@code='a']">
            <xsl:value-of select="datafield[@tag='245']/subfield[@code='a']"/>
            <xsl:if test="datafield[@tag='656']/subfield[@code='a']">
              <xsl:text> - </xsl:text>
            </xsl:if>
          </xsl:if>
          <xsl:if test="datafield[@tag='656']/subfield[@code='a']">
            <xsl:value-of select="datafield[@tag='656']/subfield[@code='a']"/>
          </xsl:if>
          <xsl:if test="datafield[@tag='110']/subfield[@code='a']">
            <xsl:if test="datafield[@tag='245']/subfield[@code='a'] or datafield[@tag='656']/subfield[@code='a']">
              <xsl:text> at </xsl:text>
            </xsl:if>
            <xsl:value-of select="datafield[@tag='110']/subfield[@code='a']"/>
          </xsl:if>
        </title>
        <link>
          <xsl:text>http://inspirehep.net/record/</xsl:text>
          <xsl:value-of select="controlfield[@tag='001']"/>
        </link>
        <xsl:if test="datafield[@tag='270']/subfield[@code='m']">
          <author>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
          </author>
        </xsl:if>
        <description>
          <xsl:if test="datafield[@tag='650' and @ind1='1' and @ind2='7']/subfield[@code='a']">
            <xsl:text>&lt;strong&gt;Field of Interest:&lt;/strong&gt;</xsl:text>
            <xsl:for-each select="datafield[@tag='650' and @ind1='1' and @ind2='7']">
              <xsl:value-of select="subfield[@code='a']"/>
              <xsl:if test="position()!=last()">
                <xsl:text>, </xsl:text>
              </xsl:if>
            </xsl:for-each>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='693']/subfield[@code='e']">
            <xsl:text>&lt;strong&gt;Experiments:&lt;/strong&gt; </xsl:text>
            <xsl:for-each select="datafield[@tag='693']">
              <xsl:text>&lt;a href="/search?cc=Experiments&amp;p=119__a%3A</xsl:text>
              <xsl:value-of select="subfield[@code='e']"/>
              <xsl:text>&amp;of=hd"&gt;</xsl:text>
              <xsl:value-of select="subfield[@code='e']"/>
              <xsl:text>&lt;/a&gt;</xsl:text>
              <xsl:if test="position()!=last()">
                <xsl:text>, </xsl:text>
              </xsl:if>
            </xsl:for-each>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='046']">
            <xsl:text>&lt;strong&gt;Deadline: &lt;/strong&gt;</xsl:text>
            <xsl:choose>
              <xsl:when test="datafield[@tag='046']/subfield[@code='i']='8888'">
                <xsl:text>OPEN UNTIL FILLED</xsl:text>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="datafield[@tag='046']/subfield[@code='i']"/>
              </xsl:otherwise>
            </xsl:choose>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='043']">
            <xsl:text>&lt;strong&gt;Region: &lt;/strong&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='043']/subfield[@code='a']"/>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:text>&lt;br /&gt;</xsl:text>
          <xsl:if test="datafield[@tag='520']">
            <xsl:text>&lt;strong&gt;Job description: &lt;/strong&gt;&lt;br /&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='520']/subfield[@code='a']"/>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:text>&lt;br /&gt;</xsl:text>
          <xsl:if test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
            <!-- PROBLEM READING THIS FIELD-->
            <xsl:text>&lt;strong&gt;More Information:&lt;/strong&gt; </xsl:text>
            <xsl:text>&lt;a href="</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>&lt;/a&gt;</xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
        </description>
      </xsl:when>
      <!--
RSS for EXPERIMENT
-->
      <xsl:when test="contains($CC, 'EXPERIMENT+')">
        <title>
          <xsl:if test="datafield[@tag='119']/subfield[@code='a']">
            <xsl:for-each select="datafield[@tag='119']">
              <xsl:value-of select="subfield[@code='a']"/>
              <xsl:text> </xsl:text>
            </xsl:for-each>
          </xsl:if>
          <xsl:if test="datafield[@tag='119']/subfield[@code='u']">
            <xsl:text> (</xsl:text>
            <xsl:value-of select="datafield[@tag='119']/subfield[@code='u']"/>
            <xsl:text>) </xsl:text>
          </xsl:if>
        </title>
	<xsl:if test="datafield[@tag='270']/subfield[@code='m']">
	  <author>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
	  </author>
	</xsl:if>
        <link>
          <xsl:if test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
          </xsl:if>
        </link>
        <description>
          <xsl:if test="datafield[@tag='245']/subfield[@code='a']">
            <xsl:text>&lt;strong&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='245']/subfield[@code='a']"/>
            <xsl:text>&lt;/strong&gt;</xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='046']/subfield[@code='q']">
            <xsl:text>(Proposed: </xsl:text>
            <xsl:value-of select="datafield[@tag='046']/subfield[@code='q']"/>
            <xsl:if test="datafield[@tag='046']/subfield[@code='t']='9999'">
              <xsl:text>, Still Running</xsl:text>
            </xsl:if>
            <xsl:if test="datafield[@tag='046']/subfield[@code='r']">
              <xsl:text>, Approved: </xsl:text>
              <xsl:value-of select="datafield[@tag='046']/subfield[@code='r']"/>
              <xsl:if test="datafield[@tag='046']/subfield[@code='s']">
                <xsl:text>, Started: </xsl:text>
                <xsl:value-of select="datafield[@tag='046']/subfield[@code='s']"/>
              </xsl:if>
            </xsl:if>
            <xsl:text>)</xsl:text>
          </xsl:if>
          <xsl:text>&lt;br /&gt;&lt;br /&gt;</xsl:text>
          <xsl:if test="(datafield[@tag='702']/subfield[@code='a']) or (datafield[@tag='702']/subfield[@code='a']!='')">
            <xsl:text>&lt;strong&gt;Spokesperson:&lt;/strong&gt; </xsl:text>
            <xsl:for-each select="datafield[@tag='702']">
              <xsl:value-of select="subfield[@code='a']"/>
              <xsl:if test="position()!=last()">
                <xsl:text>; </xsl:text>
              </xsl:if>
            </xsl:for-each>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='270']/subfield[@code='m']">
            <xsl:text>&lt;strong&gt;Contact Email:&lt;/strong&gt; </xsl:text>
            <xsl:text>&lt;a href="mailto:</xsl:text>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
            <xsl:text>&lt;/a&gt;</xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
            <!-- PROBLEM READING THIS FIELD-->
            <xsl:text>&lt;strong&gt;URL:&lt;/strong&gt; </xsl:text>
            <xsl:text>&lt;a href="</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>&lt;/a&gt;</xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:text>&lt;br /&gt;</xsl:text>
          <xsl:if test="datafield[@tag='520']/subfield[@code='a']">
            <xsl:value-of select="datafield[@tag='520']/subfield[@code='a']"/>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
        </description>
      </xsl:when>
      <!--
RSS for HEPNAMES
-->
      <xsl:when test="contains($CC, 'HEPNAMES+')">
        <title>
          <xsl:if test="datafield[@tag='100']/subfield[@code='q']">
            <xsl:value-of select="datafield[@tag='100']/subfield[@code='q']"/>
          </xsl:if>
        </title>
        <link>
          <xsl:if test="datafield[@tag='371']/subfield[@code='m']">
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='m']"/>
          </xsl:if>
        </link>
        <xsl:if test="datafield[@tag='371']/subfield[@code='m']">
          <author>
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='m']"/>
          </author>
        </xsl:if>
        <description>
          <xsl:if test="datafield[@tag='371']/subfield[@code='a']">
            <xsl:text>&lt;a href= "/search?cc=Institutions&amp;cc=Institutions&amp;p=110__u%3A%22</xsl:text>
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='a']"/>
            <xsl:text>%22&amp;action_search=Search&amp;sf=&amp;so=d&amp;rm=&amp;rg=25&amp;sc=0&amp;of=hd"&gt;(</xsl:text>
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='a']"/>
            <xsl:text>)</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='371']/subfield[@code='m']">
            <xsl:text>&lt;br /&gt;&lt;br /&gt;</xsl:text>
            <xsl:text>E-Mail: </xsl:text>
            <xsl:text>&lt;a href="mailto:</xsl:text>
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='m']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='m']"/>
            <xsl:text>&lt;/a&gt;&lt;br /&gt;</xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
        </description>
      </xsl:when>
      <!--
RSS for INSTITUTIONS
-->
      <xsl:when test="contains($CC, 'INSTITUTION+')">
        <title>
          <xsl:if test="datafield[@tag='110']/subfield[@code='u']">
            <xsl:value-of select="datafield[@tag='110']/subfield[@code='u']"/>
          </xsl:if>
        </title>
        <link>
          <xsl:choose>
            <xsl:when test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
              <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>http://inspirehep.net/collection/Institutions</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </link>
        <xsl:if test="datafield[@tag='270']/subfield[@code='m']">
          <author>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
          </author>
        </xsl:if>
        <description>
          <xsl:if test="datafield[@tag='110']/subfield[@code='t']">
            <xsl:text> [Future INSPIRE ID: </xsl:text>
            <xsl:value-of select="datafield[@tag='110']/subfield[@code='t']"/>
            <xsl:text>] </xsl:text>
            <xsl:text>&lt;br /&gt;&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='110']/subfield[@code='a']">
            <xsl:value-of select="datafield[@tag='110']/subfield[@code='a']"/>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='110']/subfield[@code='b']">
            <xsl:value-of select="datafield[@tag='110']/subfield[@code='b']"/>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='371']/subfield[@code='a']">
            <xsl:for-each select="datafield[@tag='371']/subfield[@code='a']">
              <xsl:text>&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;</xsl:text>
              <xsl:value-of select="."/>
              <xsl:text>&lt;br /&gt;</xsl:text>
            </xsl:for-each>
          </xsl:if>
          <xsl:if test="datafield[@tag='371']/subfield[@code='d']">
            <xsl:text>&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;</xsl:text>
            <xsl:value-of select="datafield[@tag='371']/subfield[@code='d']"/>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:text>&lt;a href="</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>&lt;/a&gt;</xsl:text>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='410']/subfield[@code='a']">
            <xsl:text>Name Variants: </xsl:text>
            <xsl:for-each select="datafield[@tag='410']/subfield[@code='a']">
              <xsl:value-of select="."/>
              <xsl:if test="position()!=last()">
                <xsl:text>; </xsl:text>
              </xsl:if>
            </xsl:for-each>
            <xsl:text>&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='510']/subfield[@code='a']">
            <xsl:text>Parent Institution: </xsl:text>
            <xsl:text>&lt;a href="/record/</xsl:text>
            <xsl:value-of select="datafield[@tag='510']/subfield[@code='0']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='510']/subfield[@code='a']"/>
            <xsl:text>&lt;/a&gt;</xsl:text>
          </xsl:if>
        </description>
      </xsl:when>
      <!--
RSS for CONFERENCES
-->
      <xsl:when test="contains($CC, 'CONFERENCES+')">
        <title>
          <xsl:if test="datafield[@tag='111']/subfield[@code='a']">
            <xsl:value-of select="datafield[@tag='111']/subfield[@code='a']"/>
          </xsl:if>
        </title>
        <link>
          <xsl:choose>
	    <xsl:when test="controlfield[@tag='001']">
	      <xsl:text>http://inspirehep.net/record/</xsl:text>
	      <xsl:value-of select="controlfield[@tag='001']" />
	    </xsl:when>
            <xsl:when test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
              <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>http://inspirehep.net/collection/Conferences</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </link>
        <xsl:if test="datafield[@tag='270']/subfield[@code='m']">
          <author>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
          </author>
        </xsl:if>
        <description>
          <xsl:if test="datafield[@tag='111']/subfield[@code='d']">
            <xsl:value-of select="datafield[@tag='111']/subfield[@code='d']"/>
            <xsl:text>. </xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='111']/subfield[@code='c']">
            <xsl:value-of select="datafield[@tag='111']/subfield[@code='c']"/>
            <xsl:text>. </xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='111']/subfield[@code='g']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:text>HEP records: </xsl:text>
            <xsl:text>&lt;a href="/search?p=773__w%3A</xsl:text>
	    <xsl:value-of select="translate(datafield[@tag='111']/subfield[@code='g'], '-', '/')" />
            <xsl:text> or 773__w%3A</xsl:text>
            <xsl:value-of select="datafield[@tag='111']/subfield[@code='g']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='111']/subfield[@code='g']"/>
            <xsl:text>&lt;/a&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='856' and @ind1='4']/subfield[@code='u']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:text>&lt;a href="</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='856' and @ind1='4']/subfield[@code='u']"/>
            <xsl:text>&lt;/a&gt;&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='270']/subfield[@code='m']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:text>E-Mail: </xsl:text>
            <xsl:text>&lt;a href="mailto:</xsl:text>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
            <xsl:text>"&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='270']/subfield[@code='m']"/>
            <xsl:text>&lt;/a&gt;&lt;br /&gt;</xsl:text>
          </xsl:if>
          <xsl:if test="datafield[@tag='773']/subfield[@code='x']">
            <xsl:text>&lt;br /&gt;</xsl:text>
            <xsl:value-of select="datafield[@tag='773']/subfield[@code='x']"/>
          </xsl:if>
	  <xsl:text>&lt;br /&gt;</xsl:text>
        </description>
      </xsl:when>
      <!--
   records which don't match any specific group
-->
      <xsl:otherwise>
        <title>
          <xsl:for-each select="datafield[@tag='245']">
            <xsl:value-of select="subfield[@code='a']"/>
            <xsl:if test="subfield[@code='b']">
              <xsl:text>: </xsl:text>
              <xsl:value-of select="subfield[@code='b']"/>
            </xsl:if>
          </xsl:for-each>
          <xsl:for-each select="datafield[@tag='111']">
            <xsl:value-of select="subfield[@code='a']"/>
          </xsl:for-each>
        </title>
        <link>
          <xsl:value-of select="fn:eval_bibformat(controlfield[@tag=001],'&lt;BFE_SERVER_INFO var=&quot;recurl&quot;&gt;')"/>
        </link>
        <description>
          <xsl:value-of select="fn:eval_bibformat(controlfield[@tag=001],'&lt;BFE_ABSTRACT print_lang=&quot;auto&quot;            separator_en=&quot; &quot;   separator_fr=&quot; &quot;  escape=&quot;4&quot; &gt;')"/>
        </description>
        <xsl:choose>
          <xsl:when test="contains(datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='a'], '@')">
            <!-- Email address: we can use author -->
            <author>
              <xsl:value-of select="datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='a']"/>
            </author>
          </xsl:when>
          <xsl:otherwise>
            <dc:creator>
              <xsl:value-of select="datafield[(@tag='100' or @tag='110' or @tag='700' or @tag='710')]/subfield[@code='a']"/>
            </dc:creator>
          </xsl:otherwise>
        </xsl:choose>
        <pubDate>
          <xsl:value-of select="fn:creation_date(controlfield[@tag=001], '%a, %d %b %Y %H:%M:%S GMT')"/>
        </pubDate>
        <guid>
          <xsl:value-of select="fn:eval_bibformat(controlfield[@tag=001],'&lt;BFE_SERVER_INFO var=&quot;recurl&quot;&gt;')"/>
        </guid>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
