<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id$
This file is part of CDS Invenio.
Copyright (C) 2002-2010 CERN.

CDS Invenio is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

CDS Invenio is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
-->
<!-- inspire2cds.xsl converts from Inspire to CDS MarcXML

 *** IMPORTANT NOTICE - DEPENDENCIES ***

This XSLT stylesheet depends on the following XML files, they should exist
in the same directory as this XSL file:
 - cds_inspire_693.xml
 - cds_inspire_categories_65017.xml
 - cds_inspire_journal_abbreviations.xml
 - cds_inspire_languages.xml

Ensure that these files are here or else the conversion will not work!!!
 -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:marc="http://www.loc.gov/MARC21/slim"
                xmlns:date="http://exslt.org/dates-and-times"
                xmlns:str="http://exslt.org/strings"
                exclude-result-prefixes="marc date str">
<xsl:output method="xml" encoding="UTF-8"  omit-xml-declaration="yes" indent="yes"/>

<xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'" />
<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />
<xsl:variable name="letters" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'" />
<xsl:variable name="numbers" select="'0123456789'"/>
<xsl:variable name="symbols" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-. '" />

<!-- ************ FUNCTIONS ************ -->

<!-- FUNCTION   output-65017a-subfields -->
<xsl:template name="output-65017-subfields">
  <xsl:param name="text" />
  <xsl:if test="$text != ''">
    <datafield tag="650" ind1="1" ind2="7">
      <subfield code="a"><xsl:value-of select="substring-after($text, ':')" /></subfield>
      <subfield code="2"><xsl:value-of select="substring-before($text, ':')" /></subfield>
    </datafield>
  </xsl:if>
</xsl:template>

<!-- FUNCTION   output-693ae-subfields TODO: KB for accelerator/experiment-->
<xsl:template name="output-693-subfields">
  <xsl:param name="text" />
  <xsl:if test="$text != ''">
    <xsl:variable name="newexp" select="translate($text, $numbers, '')" />
    <xsl:variable name="newnum" select="translate($text, $symbols, '')" />
    <xsl:variable name="nodes" select="document('cds_inspire_693.xml')/experiments/experiment/inspire[translate(translate(., '-', ''), $uppercase, $smallcase) = translate(translate($newexp, '-', ''), $uppercase, $smallcase)]"/>
      <xsl:choose>
        <xsl:when test="$nodes != ''">
          <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="a"><xsl:value-of select="str:split($nodes/preceding-sibling::*[1], '---')[1]" /></subfield>
            <subfield code="e"><xsl:value-of select="str:split($nodes/preceding-sibling::*[1], '---')[2]" /><xsl:value-of select="$newnum" /></subfield>
          </datafield>
        </xsl:when>
        <xsl:otherwise>
          <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="a"><xsl:value-of select="$text" /></subfield>
            <subfield code="e"><xsl:value-of select="$text" /></subfield>
          </datafield>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:if>
</xsl:template>

  <!-- FUNCTION   773p-to-cds-format -->
  <xsl:template name="journal-title-to-cds-format">
    <xsl:param name="title" />
    <xsl:param name="volume" />
    <xsl:if test="$title != ''">
      <xsl:variable name="newvolume" select="translate($volume, $numbers, '')" />
      <xsl:variable name="nodes" select="document('cds_inspire_journal_abbreviations.xml')/mappings/journal-title/inspire[translate(., ' ', '') = translate($title, ' ', '')]"/>
      <xsl:variable name="newtitle">
          <xsl:for-each select="str:split($nodes/preceding-sibling::*[1], ' ')">
              <xsl:if test="not(position() = last() and string-length(.) = 1)">
                  <xsl:value-of select="normalize-space(.)"/>
                  <xsl:if test="not(position() = last())"><xsl:text> </xsl:text></xsl:if>
              </xsl:if>
          </xsl:for-each>
          <xsl:if test="$newvolume != '' and $newvolume != '-'">
              <xsl:text> </xsl:text><xsl:value-of select="$newvolume" />
          </xsl:if>
      </xsl:variable> 
      <xsl:choose>
        <xsl:when test="$title = 'PoS'">
          <xsl:value-of select="$title" />
        </xsl:when>
        <xsl:when test="$newtitle != ''">
          <xsl:value-of select="normalize-space($newtitle)" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$title" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

<!-- FUNCTION  reformat-date : from 3 params (YYYY,MM,DD)  to "DD Mmm YYYY" -->
<xsl:template name="reformat-date">
  <xsl:param name="year"/>
  <xsl:param name="month"/>
  <xsl:param name="nday"/>
  <xsl:variable name="day">
    <xsl:if test="string-length($nday) = 1">
      <xsl:text>0</xsl:text>
    </xsl:if>
    <xsl:value-of select="$nday" />
    <xsl:if test="string-length($nday) != 0">
      <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="$month='01'">
      <xsl:value-of select="concat($day,'Jan ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='02'">
      <xsl:value-of select="concat($day,'Feb ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='03'">
      <xsl:value-of select="concat($day,'Mar ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='04'">
      <xsl:value-of select="concat($day,'Apr ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='05'">
      <xsl:value-of select="concat($day,'May ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='06'">
      <xsl:value-of select="concat($day,'Jun ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='07'">
      <xsl:value-of select="concat($day,'Jul ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='08'">
      <xsl:value-of select="concat($day,'Aug ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='09'">
      <xsl:value-of select="concat($day,'Sep ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='10'">
      <xsl:value-of select="concat($day,'Oct ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='11'">
      <xsl:value-of select="concat($day,'Nov ',$year)"/>
    </xsl:when>
    <xsl:when test="$month='12'">
      <xsl:value-of select="concat($day,'Dec ',$year)"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$year"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<!-- FUNCTION cern-detect : returns the appropriatate 690C subfield if it is a CERN paper and nothing otherwise -->
<xsl:template name="cern-detect">
  <xsl:param name="record" />
  <xsl:variable name="cern-690">
    <datafield tag="690" ind1="C" ind2=" ">
      <subfield code="a">CERN</subfield>
    </datafield>
  </xsl:variable>
  <xsl:if test="contains(//marc:datafield[@tag='037']/marc:subfield[@code='a'], 'CERN') or contains(//marc:datafield[@tag='037']/marc:subfield[@code='a'], 'CMS')">
    <datafield tag="690" ind1="C" ind2=" ">
      <subfield code="a">CERN</subfield>
    </datafield>
  </xsl:if>
</xsl:template>

  <!-- FUNCTION  translate-categories will translate subject categories from CDS to Inspire -->
  <xsl:template name="translate-categories">
    <xsl:param name="text"/>
    <xsl:if test="$text != ''">
      <xsl:variable name="kb" select="document('cds_inspire_categories_65017.xml')/categories"/>
      <xsl:variable name="newcat">
        <xsl:for-each select="$kb/category">
          <xsl:if test="./inspire=$text">
            <xsl:value-of select="./cds" />
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <xsl:choose>
      <xsl:when test="$newcat != ''">
        <datafield tag="650" ind1="1" ind2="7">
          <subfield code="a"><xsl:value-of select="$newcat"/></subfield>
          <subfield code="2">INSPIRE</subfield>
        </datafield>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="result">
        <xsl:choose>
            <xsl:when test="contains($text, 'Gravitation and Cosmology')">
              <xsl:text>arXiv:General Relativity and Cosmology</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'General Physics')">
              <xsl:text>arXiv:General Theoretical Physics</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Instrumentation')">
              <xsl:text>SzGeCERN:Detectors and Experimental Techniques</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Accelerators')">
              <xsl:text>SzGeCERN:Accelerators and Storage Rings</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Computing')">
              <xsl:text>SzGeCERN:Computing and Computers</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Math and Math Physics')">
              <xsl:text>arXiv:Mathematical Physics and Mathematics</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Astrophysics')">
              <xsl:text>arXiv:Astrophysics and Astronomy</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Other')">
              <xsl:text>SzGeCERN:Other Subjects</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Experiment-HEP')">
              <xsl:text>arXiv:Particle Physics - Experiment</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Phenomenology-HEP')">
              <xsl:text>arXiv:Particle Physics - Phenomenology</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Theory-HEP')">
              <xsl:text>arXiv:Particle Physics - Theory</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Lattice')">
              <xsl:text>arXiv:Particle Physics - Lattice</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Experiment-Nucl')">
              <xsl:text>arXiv:Nuclear Physics - Experiment-Nucl</xsl:text>
            </xsl:when>
            <xsl:when test="contains($text, 'Theory-Nucl')">
              <xsl:text>arXiv:Nuclear Physics - Theory-Nucl</xsl:text>
            </xsl:when>
        </xsl:choose>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="$result != ''">
              <datafield tag="650" ind1="1" ind2="7">
                <subfield code="a"><xsl:value-of select="$result"/></subfield>
                <subfield code="2">INSPIRE</subfield>
              </datafield>
          </xsl:when>
          <xsl:otherwise>
              <datafield tag="650" ind1="1" ind2="7">
                <subfield code="a"><xsl:value-of select="$text"/></subfield>
                <subfield code="2">INSPIRE</subfield>
              </datafield>
          </xsl:otherwise>
        </xsl:choose>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>
 
  <!-- FUNCTION  translate-language will translate subject categories from Inspire -->
  <xsl:template name="translate-language">
    <xsl:param name="text"/>
    <xsl:if test="$text != ''">
      <xsl:variable name="kb" select="document('cds_inspire_languages.xml')/languages"/>
      <xsl:variable name="newlang">
        <xsl:for-each select="$kb/language">
          <xsl:if test="contains(./inspire,$text)">
            <xsl:value-of select="./cds" />
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <xsl:choose>
        <xsl:when test="$newlang != ''">
            <datafield tag="041" ind1=" " ind2=" ">
              <subfield code="a"><xsl:value-of select="$newlang"/></subfield>
            </datafield>
        </xsl:when>
        <xsl:otherwise>
            <datafield tag="041" ind1=" " ind2=" ">
              <subfield code="a">eng</subfield>
            </datafield>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

<!-- ************ MAIN  ************ -->

<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="marc:collection">
  <xsl:element name="{local-name(.)}">
      <xsl:apply-templates select="@*|./node()"/>
  </xsl:element>
</xsl:template>

<xsl:template match="marc:record">
  <xsl:element name="{local-name(.)}">
    <!-- MARC FIELD 003  -->
    <controlfield tag="003">SzGeCERN</controlfield>

    <datafield tag="035" ind1=" " ind2=" ">
      <subfield code="9">Inspire</subfield>
      <subfield code="a"><xsl:value-of select="./marc:controlfield[@tag='001']"/></subfield>
    </datafield>

    <xsl:apply-templates select="@*|./node()"/>

    <!-- MARC FIELD 260_$$c/269_$$a,b,c (from 269_$$a,b,c) year of publication -->
    <xsl:if test="./marc:datafield[@tag='269']">
      <datafield tag="260" ind1=" " ind2=" ">
        <subfield code="c">
          <xsl:choose>
            <xsl:when test="./marc:datafield[@tag='773']/marc:subfield[@code='y']">
              <xsl:value-of select="./marc:datafield[@tag='773']/marc:subfield[@code='y']" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="substring(./marc:datafield[@tag='269']/marc:subfield[@code='c'], 1, 4)" />
            </xsl:otherwise>
          </xsl:choose>
        </subfield>
      </datafield>
      <xsl:variable name="record" select="."/>
      <datafield tag="269" ind1=" " ind2=" ">
        <xsl:for-each select="./marc:datafield[@tag='269']/marc:subfield">
          <xsl:choose>
            <xsl:when test="@code='c'">
              <xsl:variable name="datebase">
                <xsl:value-of select="." />
                <!-- Find the best place to fetch date 
                <xsl:choose>
                  <xsl:when test="string-length($record/marc:datafield[@tag='961']/marc:subfield[@code='x']) &gt; string-length(@code='c')">
                    <xsl:value-of select="$record/marc:datafield[@tag='961']/marc:subfield[@code='x']" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="." />
                  </xsl:otherwise>
                </xsl:choose>-->
              </xsl:variable>
              <xsl:variable name="year" select="substring($datebase,1, 4)"/>
              <xsl:variable name="month" select="substring($datebase, 6, 2)"/>
              <xsl:variable name="day" select="substring($datebase, 9, 2)"/>
              <subfield code='c'>
                <xsl:call-template name="reformat-date">
                  <xsl:with-param name="year" select="$year" />
                  <xsl:with-param name="month" select="$month" />
                  <xsl:with-param name="nday" select="$day" />
                </xsl:call-template>
              </subfield>
            </xsl:when>
            <xsl:otherwise>
              <xsl:element name="{local-name(.)}">
                <xsl:copy-of select="@*"/>
                <xsl:value-of select="." />
              </xsl:element>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      </datafield>
    </xsl:if>

    <xsl:if test="./marc:datafield[@tag='100']/marc:subfield[@code='u']='CERN' or ./marc:datafield[@tag='700']/marc:subfield[@code='u']='CERN'">
      <datafield tag="690" ind1="C" ind2=" ">
        <subfield code="a">CERN</subfield>
      </datafield>
    </xsl:if>

    <!-- MARC FIELD 916$$a = creation date  -->
    <datafield tag="916" ind1=" " ind2=" ">
      <subfield code="s">n</subfield>
      <subfield code="w"><xsl:value-of select="date:year()" /><xsl:value-of select="format-number(date:week-in-year(),'00')" /></subfield>
    </datafield>

    <xsl:if test="./marc:datafield[@tag='773']/marc:subfield[@code='w']">
      <datafield tag="962" ind1=" " ind2=" ">
        <subfield code="b"><xsl:value-of select="./marc:datafield[@tag='773']/marc:subfield[@code='w']" /></subfield>
      </datafield>
    </xsl:if>

    <!-- MARC FIELD 963$$a = default value: public record  -->
    <datafield tag="963" ind1=" " ind2=" ">
      <subfield code="a">PUBLIC</subfield>
    </datafield>

    <!-- MARC FIELD 980 - base determination -->
    <xsl:choose>
      <xsl:when test="(./marc:datafield[@tag='773']/marc:subfield[@code='c'] and ./marc:datafield[@tag='773']/marc:subfield[@code='p']) or ./marc:datafield[@tag='773']/marc:subfield[@code='x']">

        <datafield tag="690" ind1="C" ind2=" ">
          <subfield code="a">ARTICLE</subfield>
        </datafield>

        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">ARTICLE</subfield>
        </datafield>

        <!-- MARC FIELD 960$$a the base field -->
        <datafield tag="960" ind1=" " ind2=" ">
          <subfield code="a">13</subfield>
        </datafield>

      </xsl:when>
      <xsl:when test="./marc:datafield[@tag='980']/marc:subfield[@code='a']='Thesis'">

        <!-- MARC FIELDS 690C$$a and 980$$a NB: 980$$a enables searching  -->
        <datafield tag="690" ind1="C" ind2=" ">
          <subfield code="a">THESIS</subfield>
        </datafield>

        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">THESIS</subfield>
        </datafield>

        <!-- MARC FIELD 960$$a the base field -->
        <datafield tag="960" ind1=" " ind2=" ">
          <subfield code="a">14</subfield>
        </datafield>

      </xsl:when>

      <xsl:otherwise>

        <!-- MARC FIELDS 690C$$a and 980$$a NB: 980$$a enables searching  -->
        <datafield tag="690" ind1="C" ind2=" ">
          <subfield code="a">PREPRINT</subfield>
        </datafield>

        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">PREPRINT</subfield>
        </datafield>

        <!-- MARC FIELD 960$$a the base field  -->
        <datafield tag="960" ind1=" " ind2=" ">
          <subfield code="a">11</subfield>
        </datafield>

      </xsl:otherwise>
    </xsl:choose>

  </xsl:element>
</xsl:template>

<xsl:template match="marc:controlfield"/>
<xsl:template match="marc:datafield"/>
<xsl:template match="comment()"/>

<xsl:template match="marc:datafield[@tag=041]">
    <xsl:call-template name="translate-language">
      <xsl:with-param name="text" select="./marc:subfield[@code='a']" />
    </xsl:call-template>
</xsl:template>


<!-- MARC FIELD 024_$$a,2 DOI -->
<xsl:template match="marc:datafield[@tag=024]">
    <xsl:if test="contains(./marc:subfield[@code='2'], 'DOI')">
      <datafield tag="024" ind1="7" ind2=" ">
          <subfield code="2">DOI</subfield>
          <subfield code="a"><xsl:value-of select="./marc:subfield[@code='a']" /></subfield>
      </datafield>
    </xsl:if>
</xsl:template>

<xsl:template match="marc:datafield[@tag=035]">
    <!-- MARC FIELD 035_$$9,a SYSTEM CONTROL NUMBER -->
    <xsl:if test="contains(./marc:subfield[@code='9'], 'arXiv')">
      <datafield tag="035" ind1=" " ind2=" ">
          <subfield code="9"><xsl:value-of select="./marc:subfield[@code='9']" /></subfield>
          <xsl:choose>
            <xsl:when test="./marc:subfield[@code='a']">
                <subfield code="a"><xsl:value-of select="./marc:subfield[@code='a']" /></subfield>
            </xsl:when>
            <xsl:when test="./marc:subfield[@code='z']">
                <subfield code="a"><xsl:value-of select="./marc:subfield[@code='z']" /></subfield>
            </xsl:when>
          </xsl:choose>
      </datafield>
    </xsl:if>
</xsl:template>

    <!-- MARC FIELD 037_$$a arXiv no. -->
<xsl:template match="marc:datafield[@tag='037']">
      <xsl:choose>
        <xsl:when test="contains(./marc:subfield[@code='a'], 'arXiv')">
          <datafield tag="037" ind1=" " ind2=" ">
            <subfield code="a"><xsl:value-of select="./marc:subfield[@code='a']" /></subfield>
          </datafield>
        </xsl:when>
        <!-- MARC FIELD 088_$$a (from 037_$$a) report number -->
        <xsl:otherwise>
          <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="a"><xsl:value-of select="./marc:subfield[@code='a']" /></subfield>
          </datafield>
        </xsl:otherwise>
      </xsl:choose>
</xsl:template>

    <!-- MARC FIELD 100_$$a,u author, first -->
<xsl:template match="marc:datafield[@tag='100']">
      <datafield tag="100" ind1=" " ind2=" ">
        <xsl:for-each select="./marc:subfield">
          <xsl:choose>
            <xsl:when test="@code='a'">
              <subfield code="a">
                <xsl:value-of select="normalize-space(translate(., '.', ' '))" />
              </subfield>
            </xsl:when>
            <xsl:when test="@code='u'">
              <subfield code="u">
                <xsl:value-of select="." />
              </subfield>
            </xsl:when>
            <xsl:otherwise>
              <xsl:element name="{local-name(.)}">
                <xsl:copy-of select="@*"/>
                <xsl:value-of select="." />
              </xsl:element>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      </datafield>
</xsl:template>

    <!-- Directly copy identical tags -->
<xsl:template match="marc:datafield[@tag='245']">
  <xsl:element name="{local-name(.)}">
    <xsl:copy-of select="@*"/>
    <xsl:for-each select="./marc:subfield">
      <xsl:element name="{local-name(.)}">
        <xsl:copy-of select="@*"/>
        <xsl:value-of select="."/>
      </xsl:element>
    </xsl:for-each>
  </xsl:element>
</xsl:template>

    <!-- MARC FIELD 300_$$a Number of pages -->
<xsl:template match="marc:datafield[@tag='300']">
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a"><xsl:value-of select="./marc:subfield[@code='a']" /> p</subfield>
      </datafield>
</xsl:template>

    <!-- Directly copy identical tags -->
<xsl:template match="marc:datafield[@tag='500'] | marc:datafield[@tag='520']">
  <xsl:element name="{local-name(.)}">
    <xsl:copy-of select="@*"/>
    <xsl:for-each select="./marc:subfield">
      <xsl:element name="{local-name(.)}">
        <xsl:copy-of select="@*"/>
        <xsl:value-of select="."/>
      </xsl:element>
    </xsl:for-each>
  </xsl:element>
</xsl:template>

    <!-- MARC FIELD 502_$$abc Thesis information -->
<xsl:template match="marc:datafield[@tag=502]">
    <datafield tag="502" ind1=" " ind2=" ">
      <xsl:for-each select="./marc:subfield">
        <xsl:choose>
          <xsl:when test="@code='b'">
            <subfield code="a"><xsl:value-of select="." /></subfield>
          </xsl:when>
          <xsl:when test="@code='c'">
            <subfield code="b"><xsl:value-of select="." /></subfield>
          </xsl:when>
          <xsl:when test="@code='d'">
            <subfield code="c"><xsl:value-of select="." /></subfield>
          </xsl:when>
          <xsl:otherwise>
            <xsl:element name="{local-name(.)}">
              <xsl:copy-of select="@*"/>
              <xsl:value-of select="." />
            </xsl:element>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </datafield>
</xsl:template>

    <!-- MARC FIELD 65017$$a,2 Subject category -->
<xsl:template match="marc:datafield[@tag='650']">
        <xsl:call-template name="translate-categories">
          <xsl:with-param name="text" select="./marc:subfield[@code='a']" />
        </xsl:call-template>
</xsl:template>

    <!-- MARC FIELD 693_$$a,e ACCELERATOR/EXPERIMENT -->
<xsl:template match="marc:datafield[@tag='693']">
        <xsl:call-template name="output-693-subfields">
          <xsl:with-param name="text" select="./marc:subfield[@code='e']" />
        </xsl:call-template>
</xsl:template>

    <!-- MARC FIELD 700_$$a,u author, rest -->
<xsl:template match="marc:datafield[@tag='700']">
      <datafield tag="700" ind1=" " ind2=" ">
        <xsl:for-each select="./marc:subfield">
          <xsl:choose>
            <xsl:when test="@code='a'">
              <subfield code="a">
                <xsl:value-of select="normalize-space(translate(., '.', ' '))" />
              </subfield>
            </xsl:when>
            <xsl:when test="@code='u'">
              <subfield code="u">
                <xsl:value-of select="." />
              </subfield>
            </xsl:when>
            <xsl:otherwise>
              <xsl:element name="{local-name(.)}">
                <xsl:copy-of select="@*"/>
                <xsl:value-of select="." />
              </xsl:element>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      </datafield>
</xsl:template>

    <!-- Directly copy identical tags -->
<xsl:template match="marc:datafield[@tag='710'] | marc:datafield[@tag='701']">
  <xsl:element name="{local-name(.)}">
    <xsl:copy-of select="@*"/>
    <xsl:for-each select="./marc:subfield">
      <xsl:element name="{local-name(.)}">
        <xsl:copy-of select="@*"/>
        <xsl:value-of select="."/>
      </xsl:element>
    </xsl:for-each>
  </xsl:element>
</xsl:template>

    <!-- MARC FIELD 773_$$ journal info, map titles -->
<xsl:template match="marc:datafield[@tag=773]">
    <xsl:variable name="volume" select="./marc:subfield[@code='v']" />
    <xsl:variable name="journal">
        <xsl:call-template name="journal-title-to-cds-format">
          <xsl:with-param name="title" select="./marc:subfield[@code='p']" />
          <xsl:with-param name="volume" select="$volume" />
        </xsl:call-template>
    </xsl:variable>
    <xsl:if test="not(./marc:subfield[@code='x'])">
        <datafield tag="773" ind1=" " ind2=" ">
          <xsl:for-each select="./marc:subfield">
            <xsl:choose>
              <xsl:when test="@code='v' and $journal = 'PoS'">
                <subfield code="v"><xsl:value-of select="$volume"/></subfield>
              </xsl:when>
              <xsl:when test="@code='v'">
                <subfield code="v"><xsl:value-of select="translate($volume, $letters, '')"/></subfield>
              </xsl:when>
              <xsl:when test="@code='p'">
                <subfield code="p"><xsl:value-of select="$journal"/></subfield>
              </xsl:when>
              <xsl:when test="@code!='x'">
                <xsl:element name="{local-name(.)}">
                  <xsl:copy-of select="@*"/>
                  <xsl:value-of select="." />
                </xsl:element>
              </xsl:when>
            </xsl:choose>
          </xsl:for-each>
        </datafield>
    </xsl:if>
</xsl:template>

    <!-- Directly copy identical tags -->
<xsl:template match="marc:datafield[@tag='856']">
    <xsl:choose>
        <xsl:when test="contains(./marc:subfield[@code='u'], 'http://inspirebeta.net')">
            <datafield tag="FFT" ind1=" " ind2=" ">
              <xsl:if test="contains(./marc:subfield[@code='u'], '.png')">
                <subfield code="t">Plot</subfield>
              </xsl:if>
              <xsl:for-each select="./marc:subfield">
                 <xsl:choose>
                     <xsl:when test="@code='u'">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                     </xsl:when>
                     <xsl:when test="@code='y'">
                        <subfield code="d"><xsl:value-of select="."/></subfield>
                     </xsl:when>
                 </xsl:choose>
              </xsl:for-each>
            </datafield>
        </xsl:when>
        <xsl:otherwise>
          <xsl:element name="{local-name(.)}">
            <xsl:copy-of select="@*"/>
            <xsl:for-each select="./marc:subfield">
              <xsl:element name="{local-name(.)}">
                <xsl:copy-of select="@*"/>
                <xsl:value-of select="."/>
              </xsl:element>
            </xsl:for-each>
          </xsl:element>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

    <!-- Directly copy identical tags 
<xsl:template match="marc:datafield[@tag='999']">
  <xsl:element name="{local-name(.)}">
    <xsl:copy-of select="@*"/>
    <xsl:for-each select="./marc:subfield">
      <xsl:element name="{local-name(.)}">
        <xsl:copy-of select="@*"/>
        <xsl:value-of select="."/>
      </xsl:element>
    </xsl:for-each>
  </xsl:element>
</xsl:template>
-->
</xsl:stylesheet>
