<?xml version="1.0" encoding="utf-8"?>
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
<!-- cds2inspire-cmsnotes.xsl converts MarcXML from CMS Notes in CDS to Inspire MarcXML -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                xmlns:marc="http://www.loc.gov/MARC21/slim"
                exclude-result-prefixes="marc str">
  <xsl:output method="xml" encoding="UTF-8"/>

  <xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'" />
  <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

  <!-- ************ FUNCTIONS ************ -->

  <!-- FUNCTION  add-punctuation-authorname -->
  <xsl:template name="add-author">
    <xsl:param name="field"/>
    <xsl:if test="not($field/@code = 'i' and $field = 'XX') and not($field/@code = 'j' and $field = 'YY')">
      <xsl:choose>
      <!-- If authorname, add punctuations -->
      <xsl:when test="@code = 'a'">
        <xsl:element name="{local-name($field)}">
            <xsl:copy-of select="@*"/>
            <xsl:call-template name="add-punctuation-authorname">
                <xsl:with-param name="author" select="$field"/>
            </xsl:call-template>
        </xsl:element>
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="{local-name($field)}">
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="$field" />
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- FUNCTION  add-author-thesis for 700->701 thesis supervisors -->
  <xsl:template name="add-author-thesis">
    <xsl:param name="field"/>
    <xsl:if test="not($field/@code = 'i' and $field = 'XX') and not($field/@code = 'j' and $field = 'YY')">
      <xsl:choose>
      <!-- If authorname, add punctuations -->
      <xsl:when test="@code = 'a'">
        <xsl:element name="{local-name($field)}">
            <xsl:copy-of select="@*"/>
            <xsl:call-template name="add-punctuation-authorname">
                <xsl:with-param name="author" select="$field"/>
            </xsl:call-template>
        </xsl:element>
      </xsl:when>
      <xsl:when test="@code != 'e'">
        <xsl:element name="{local-name($field)}">
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="$field" />
        </xsl:element>
      </xsl:when>
    </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- FUNCTION  add-punctuation-authorname -->
  <xsl:template name="add-punctuation-authorname">
    <xsl:param name="author"/>
    <xsl:choose>
        <xsl:when test="substring-before($author,' ') != ''">
            <xsl:value-of select="concat(substring-before($author,' '), ' ')" />
            <xsl:variable name="initials" select="substring-after($author,' ')" />
            <xsl:choose>
              <xsl:when test="contains($initials, '.')">
                <xsl:call-template name="replace-string">
                  <xsl:with-param name="text" select="$initials" />
                  <xsl:with-param name="from" select="' '" />
                  <xsl:with-param name="to" select="''" />
                </xsl:call-template>
                <xsl:text>.</xsl:text>
              </xsl:when>
              <xsl:when test="string-length($initials) = 1">
                <xsl:value-of select="$initials" /><xsl:text>.</xsl:text>
              </xsl:when>
              <xsl:when test="string-length(substring-before($initials, ' ')) = 1">
                <xsl:call-template name="replace-string">
                  <xsl:with-param name="text" select="$initials" />
                  <xsl:with-param name="from" select="' '" />
                  <xsl:with-param name="to" select="'.'" />
                </xsl:call-template>
                <xsl:text>.</xsl:text>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$initials"/>
              </xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$author"/>
        </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- FUNCTION  replace-string -->
  <xsl:template name="replace-string">
    <xsl:param name="text"/>
    <xsl:param name="from"/>
    <xsl:param name="to"/>
    <xsl:choose>
      <xsl:when test="contains($text, $from)">
        <xsl:variable name="before" select="substring-before($text, $from)"/>
        <xsl:variable name="after" select="substring-after($text, $from)"/>
        <xsl:variable name="prefix" select="concat($before, $to)"/>

        <xsl:value-of select="$before"/>
        <xsl:value-of select="$to"/>
        <xsl:call-template name="replace-string">
          <xsl:with-param name="text" select="$after"/>
          <xsl:with-param name="from" select="$from"/>
          <xsl:with-param name="to" select="$to"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- FUNCTION  reformat-date : from 3 params (YYYY,MM,DD)  to "DD Mmm YYYY" -->
  <xsl:template name="reformat-date">
    <xsl:param name="year"/>
    <xsl:param name="month"/>
    <xsl:param name="d"/>
    <xsl:variable name="day">
      <xsl:if test="string-length($d) != 0">
        <xsl:text>-</xsl:text>
      </xsl:if>
      <xsl:if test="string-length($d) = 1">
        <xsl:text>0</xsl:text>
      </xsl:if>
      <xsl:value-of select="$d" />
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$month='Jan'">
        <xsl:value-of select="concat($year,'-01',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Feb'">
        <xsl:value-of select="concat($year,'-02',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Mar'">
        <xsl:value-of select="concat($year,'-03',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Apr'">
        <xsl:value-of select="concat($year,'-04',$day)"/>
      </xsl:when>
      <xsl:when test="$month='May'">
        <xsl:value-of select="concat($year,'-05',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Jun'">
        <xsl:value-of select="concat($year,'-06',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Jul'">
        <xsl:value-of select="concat($year,'-07',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Aug'">
        <xsl:value-of select="concat($year,'-08',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Sep'">
        <xsl:value-of select="concat($year,'-09',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Oct'">
        <xsl:value-of select="concat($year,'-10',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Nov'">
        <xsl:value-of select="concat($year,'-11',$day)"/>
      </xsl:when>
      <xsl:when test="$month='Dec'">
        <xsl:value-of select="concat($year,'-12',$day)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="concat($year, '-', $month, $day)" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- FUNCTION  translate-categories will translate subject categories from CDS to Inspire -->
  <xsl:template name="translate-categories">
    <xsl:param name="text"/>
    <xsl:if test="$text != ''">
      <xsl:variable name="kb" select="document('cds_inspire_categories_65017.xml')/categories"/>
      <xsl:variable name="newcat">
        <xsl:for-each select="$kb/category">
          <xsl:if test="./cds=$text">
            <xsl:value-of select="./inspire" />
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
        <datafield tag="650" ind1="1" ind2="7">
          <subfield code="a"><xsl:value-of select="$text"/></subfield>
          <subfield code="2">INSPIRE</subfield>
        </datafield>
      </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- FUNCTION  translate-language will translate subject categories from CDS to Inspire -->
  <xsl:template name="translate-language">
    <xsl:param name="text"/>
    <xsl:if test="$text != ''">
      <xsl:variable name="kb" select="document('cds_inspire_languages.xml')/languages"/>
      <xsl:variable name="newlang">
        <xsl:for-each select="$kb/language">
          <xsl:if test="contains(./cds,$text)">
            <xsl:value-of select="./inspire" />
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <xsl:if test="$newlang != ''">
        <datafield tag="041" ind1=" " ind2=" ">
          <subfield code="a"><xsl:value-of select="$newlang"/></subfield>
        </datafield>
      </xsl:if> 
    </xsl:if>
  </xsl:template>

  <!-- FUNCTION   output-773p-subfields -->
  <xsl:template name="output-773p-subfield">
    <xsl:param name="title" />
    <xsl:if test="$title != ''">
      <xsl:variable name="kb" select="document('cds_inspire_journal_abbreviations.xml')/mappings"/>
      <xsl:variable name="newtitle">
        <xsl:for-each select="$kb/journal-title">
          <xsl:if test="./cds = $title">
            <xsl:value-of select="./inspire" />
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <xsl:choose>
        <xsl:when test="$newtitle != ''">
          <subfield code="p"><xsl:value-of select="$newtitle" /></subfield>
        </xsl:when>
        <xsl:otherwise>
          <subfield code="p"><xsl:value-of select="$title" /></subfield>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- ************ MAIN  ************ -->

  <xsl:key name="collection" match="//marc:datafield[@tag='980']/marc:subfield[@code='a']" use="text()" />

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
     
      <datafield tag="035" ind1=" " ind2=" ">
        <subfield code="9">CDS</subfield>
        <subfield code="a"><xsl:value-of select="./marc:controlfield[@tag='001']"/></subfield>
      </datafield>
      <!--<datafield tag="595" ind1=" " ind2=" ">
          <subfield code="9">CERN</subfield>
          <subfield code="a">CDS-<xsl:value-of select="./marc:controlfield[@tag='001']"/></subfield>
      </datafield>
    -->
      <xsl:apply-templates select="@*|./node()"/>
      <xsl:variable name="recid" select="./marc:controlfield[@tag='001']"/>
      <!-- Thesis -->
      <xsl:if test="key('collection', 'THESIS')">
        <datafield tag="690" ind1="C" ind2=" ">
          <subfield code="a">THESIS</subfield>
        </datafield>
      </xsl:if>
      <datafield tag="690" ind1="C" ind2=" ">
        <subfield code="a">NOTE</subfield>
      </datafield>
      <xsl:if test="./marc:datafield[@tag='690']/marc:subfield[code='a']='INTNOTE'">
        <!-- 690C Add NOTE -->

        <!-- 856 Add fulltext URL indicator (CMS Note Specific) -->
        <xsl:if test="contains(./marc:datafield[@tag='088']/marc:subfield[@code='a'], 'CMS')">
            <datafield tag="856" ind1="4" ind2=" ">
               <subfield code="u"><xsl:text>http://weblib.cern.ch/abstract?CERN-CMS</xsl:text>
               <xsl:value-of select="substring-after(./marc:subfield[@code='a'], 'CMS')"/>
               </subfield>
            </datafield>
        </xsl:if>
      </xsl:if>

      <xsl:for-each select="./marc:datafield[@tag='856'][contains(marc:subfield[@code='z'], 'Figure')][not(contains(marc:subfield[@code='u'], 'subformat'))]">
        <datafield tag="FFT" ind1="" ind2="">
          <subfield code="a">/afs/cern.ch/project/inspire/uploads/cms-pas/<xsl:value-of select="$recid"/>_<xsl:value-of select="./marc:subfield[@code='y']" />.png</subfield>
          <subfield code="n"><xsl:value-of select="./marc:subfield[@code='y']" /></subfield>
	  <subfield code="f">.png</subfield>
          <subfield code="d">0000<xsl:value-of select="position()"/><xsl:text> </xsl:text><xsl:value-of select="./marc:subfield[@code='y']" /></subfield>
          <subfield code="t">Plot</subfield>
          <subfield code="z">KEEP-OLD-VALUE</subfield>
          <subfield code="r">KEEP-OLD-VALUE</subfield>
        </datafield>
      </xsl:for-each>

      <!-- 980 Add collection indicators  -->

      <!-- Thesis -->
      <xsl:if test="key('collection', 'THESIS')">
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Thesis</subfield>
        </datafield>
      </xsl:if>

      <!-- Journal -->
      <xsl:if test="./marc:datafield[@tag='980']/marc:subfield[@code='a'] and ./marc:datafield[@tag='773']/marc:subfield[@code='p']">
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Published</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Citeable</subfield>
        </datafield>
      </xsl:if>

      <!-- ArXiv -->
      <xsl:if test="contains(./marc:datafield[@tag='035']/marc:subfield[@code='a'], 'arXiv')">
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Arxiv</subfield>
        </datafield>
      </xsl:if>

      <!-- HEP (applies to all)  -->
      <datafield tag="980" ind1=" " ind2=" ">
        <subfield code="a">HEP</subfield>
      </datafield>
      <datafield tag="980" ind1=" " ind2=" ">
        <subfield code="a">CORE</subfield>
      </datafield>
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

<xsl:template match="marc:datafield[@tag=035]">
    <xsl:variable name="scnInst" select="translate(./marc:subfield[@code=9], $uppercase, $smallcase)" />
    <xsl:choose>
      <!-- Omit fields with only $9 parameter -->
      <xsl:when test="./marc:subfield[@code=9] and not(./marc:subfield[@code='a'])">
      </xsl:when>
      <xsl:when test="$scnInst='SPIRES'">
        <datafield tag="970" ind1=" " ind2=" ">
          <subfield code="a">SPIRES-<xsl:value-of select="./marc:subfield[@code='a']" /></subfield>
        </datafield>
      </xsl:when>
      <xsl:when test="not(contains(./marc:subfield[@code='a'],'CERCER')) and not(./marc:subfield[@code='a'] != '') and $scnInst!='inspire' and $scnInst!='xx' and $scnInst!='cern annual report' and $scnInst!='cds' and $scnInst!='cmscms' and $scnInst!='cercer' and $scnInst!='wai01'">
        <datafield tag="035" ind1=" " ind2=" ">
          <xsl:for-each select="./marc:subfield">
            <xsl:element name="{local-name(.)}">
              <xsl:copy-of select="@*"/>
              <xsl:value-of select="." />
            </xsl:element>
          </xsl:for-each>
        </datafield>
      </xsl:when>
    </xsl:choose>
</xsl:template>

<xsl:template match="marc:datafield[@tag=088]">
    <xsl:choose>
        <xsl:when test="starts-with(./marc:subfield[@code=9], 'P0') or starts-with(./marc:subfield[@code=9], 'CM-P0')">
            <!-- 595 Add barcodes etc. (CDS Theses Specific) -->
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="9">CERN</subfield>
                <subfield code="b"><xsl:value-of select="./marc:subfield[@code=9]"/></subfield>
            </datafield>
        </xsl:when>
        <xsl:when test="not(starts-with(./marc:subfield[@code='a'], 'SIS-')) and not(starts-with(./marc:subfield[@code='9'], 'SIS-'))">
            <datafield tag="037" ind1=" " ind2=" ">
              <subfield code="a">
                <xsl:value-of select="./marc:subfield" />
              </subfield>
            </datafield>
        </xsl:when>
    </xsl:choose>
</xsl:template>

<xsl:template match="marc:datafield[@tag=037]">
  <xsl:choose>
    <xsl:when test="contains(./marc:subfield[@code='a'],'arXiv')">
        <datafield tag="037" ind1=" " ind2=" ">
          <subfield code="a">
            <xsl:value-of select="./marc:subfield[@code='a']" />
          </subfield>
          <subfield code="9">arXiv</subfield>
          <xsl:if test="./marc:datafield[@tag='695']/marc:subfield[@code='a']">
              <subfield code="c">
                <xsl:value-of select="./marc:datafield[@tag='695']/marc:subfield[@code='a']"/>
              </subfield>
          </xsl:if>
        </datafield>
    </xsl:when>
    <xsl:when test="not(starts-with(./marc:subfield[@code='a'], 'SIS-')) and not(starts-with(./marc:subfield[@code='9'], 'SIS-'))">
      <xsl:element name="{local-name(.)}">
        <xsl:copy-of select="@*"/>
        <xsl:for-each select="./marc:subfield">
          <xsl:element name="{local-name(.)}">
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="normalize-space(.)"/>
          </xsl:element>
        </xsl:for-each>
      </xsl:element>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<xsl:template match="marc:datafield[@tag=242]">
    <datafield tag="246" ind1=" " ind2=" ">
      <xsl:for-each select="./marc:subfield">
        <xsl:element name="{local-name(.)}">
          <xsl:copy-of select="@*"/>
          <xsl:value-of select="normalize-space(.)"/>
        </xsl:element>
      </xsl:for-each>
    </datafield>
</xsl:template>

<xsl:template match="marc:datafield[@tag=260]">
    <xsl:if test="not(key('collection', 'THESIS'))">
      <datafield tag="269" ind1=" " ind2=" ">
        <subfield code="c"><xsl:value-of select="normalize-space(.)"/></subfield>
      </datafield>
    </xsl:if>
</xsl:template>

<xsl:template match="marc:datafield[@tag=269]">
    <xsl:if test="./marc:subfield[@code='c']">
    <datafield tag="269" ind1=" " ind2=" ">
      <xsl:for-each select="./marc:subfield[@code='c']">
        <!--<xsl:choose>
          <xsl:when test="@code='c'">
             Find the best place to fetch date 
            <xsl:choose>
              <xsl:when test="string-length(./marc:datafield[@tag='961']/marc:subfield[@code='x']) &gt; string-length(translate(.,' ', ''))">
                <xsl:variable name="datebase" select="./marc:datafield[@tag='961']/marc:subfield[@code='x']" />
                <xsl:variable name="year" select="substring($datebase,1, 4)"/>
                <xsl:variable name="month" select="substring($datebase, 5, 2)"/>
                <xsl:variable name="day" select="substring($datebase, 7, 2)"/>
                <subfield code='c'>
                  <xsl:call-template name="reformat-date">
                    <xsl:with-param name="year" select="$year" />
                    <xsl:with-param name="month" select="$month" />
                    <xsl:with-param name="d" select="$day" />
                  </xsl:call-template>
                </subfield>
              </xsl:when>
              <xsl:otherwise>
                <xsl:variable name="day" select="substring-before(.,' ')"/>
                <xsl:variable name="month" select="substring-before(substring-after(.,' '),' ')"/>
                <xsl:variable name="year" select="substring-after(substring-after(.,' '),' ')"/>
                <subfield code='c'>
                  <xsl:call-template name="reformat-date">
                    <xsl:with-param name="year" select="$year" />
                    <xsl:with-param name="month" select="$month" />
                    <xsl:with-param name="d" select="$day" />
                  </xsl:call-template>
                </subfield>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:otherwise>-->
            <xsl:element name="{local-name(.)}">
              <xsl:copy-of select="@*"/>
              <xsl:value-of select="." />
            </xsl:element>
          <!--</xsl:otherwise>
        </xsl:choose>-->
      </xsl:for-each>
    </datafield>
    </xsl:if>
</xsl:template>

<xsl:template match="marc:datafield[@tag=300]">
    <xsl:if test="./marc:subfield[@code='a'] != 'mult. p' and ./marc:subfield[@code='a'] != ' p'">
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">
          <xsl:value-of select="str:split(./marc:subfield[@code='a'], ' ')[1]"/>
        </subfield>
      </datafield>
    </xsl:if>
</xsl:template>

<xsl:template match="marc:datafield[@tag=100] | marc:datafield[@tag=700]">
    <xsl:choose>
      <xsl:when test="@tag='700' and key('collection', 'THESIS')">
          <datafield tag="701" ind1=" " ind2=" ">
          <xsl:for-each select="./marc:subfield">
            <xsl:call-template name="add-author-thesis">
              <xsl:with-param name="field" select="."/>
            </xsl:call-template>
          </xsl:for-each>
          </datafield>
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="{local-name(.)}">
          <xsl:copy-of select="@*"/>
          <xsl:for-each select="./marc:subfield">
            <xsl:call-template name="add-author">
              <xsl:with-param name="field" select="."/>
            </xsl:call-template>
          </xsl:for-each>
          <xsl:if test="@tag='100' and not(./marc:subfield[@code='u'])">
              <xsl:choose>
                  <xsl:when test="../marc:datafield[@tag='901']/marc:subfield[@code='u']">
                      <subfield code="u"><xsl:value-of select="../marc:datafield[@tag='901']/marc:subfield[@code='u']" /></subfield>
                  </xsl:when>
                  <xsl:when test="../marc:datafield[@tag='502']/marc:subfield[@code='b']">
                      <subfield code="u"><xsl:value-of select="../marc:datafield[@tag='502']/marc:subfield[@code='b']" /></subfield>
                  </xsl:when>
              </xsl:choose>
          </xsl:if>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="marc:datafield[@tag=502]">
    <datafield tag="502" ind1=" " ind2=" ">
      <xsl:for-each select="./marc:subfield">
        <xsl:choose>
          <xsl:when test="@code='a'">
            <subfield code="b"><xsl:value-of select="." /></subfield>
          </xsl:when>
          <xsl:when test="@code='b'">
            <subfield code="c"><xsl:value-of select="." /></subfield>
          </xsl:when>
          <xsl:when test="@code='c'">
            <subfield code="d"><xsl:value-of select="." /></subfield>
          </xsl:when>
          <xsl:otherwise>
            <xsl:element name="{local-name(.)}">
              <xsl:copy-of select="@*"/>
              <xsl:value-of select="." />
            </xsl:element>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      <xsl:if test="not(./marc:subfield[@code='c']) and ../marc:datafield[@tag=260]/marc:subfield[@code='c']">
          <subfield code="d"><xsl:value-of select="../marc:datafield[@tag=260]/marc:subfield[@code='c']" /></subfield>
      </xsl:if>
    </datafield>
</xsl:template>

<xsl:template match="marc:datafield[@tag=650 and @ind1='1' and @ind2='7']">
    <xsl:call-template name="translate-categories">
      <xsl:with-param name="text" select="./marc:subfield[@code='a']" />
    </xsl:call-template>
</xsl:template>

<xsl:template match="marc:datafield[@tag=653 and @ind1='1']">
  <datafield tag="653" ind1="1" ind2=" ">
    <subfield code="9">author</subfield>
    <subfield code="a"><xsl:value-of select="./marc:subfield[@code='a']" /></subfield>
  </datafield>
</xsl:template>

<xsl:template match="marc:datafield[@tag=693]">
  <xsl:if test="not(translate(./marc:subfield[@code='a'], $uppercase, $smallcase) = 'not applicable')">
      <xsl:if test="not(translate(./marc:subfield[@code='e'], $uppercase, $smallcase) = 'not applicable')">
        <xsl:element name="{local-name(.)}">
          <xsl:copy-of select="@*"/>
          <xsl:for-each select="./marc:subfield">
            <xsl:element name="{local-name(.)}">
              <xsl:copy-of select="@*"/>
              <xsl:value-of select="normalize-space(.)"/>
            </xsl:element>
          </xsl:for-each>
        </xsl:element>
      </xsl:if>
  </xsl:if>
</xsl:template>

<xsl:template match="marc:datafield[@tag=710]">
    <xsl:choose>
      <xsl:when test="not(./marc:subfield[@code='5'] and count(./marc:subfield)=1) and not(./marc:subfield[@code='a'] and starts-with(./marc:subfield[@code='a'],'CERN. Geneva') and count(./marc:subfield)=1)">
        <xsl:element name="{local-name(.)}">
          <xsl:copy-of select="@*"/>
          <xsl:for-each select="./marc:subfield">
            <xsl:if test="@code!='5' and not(@code='a' and starts-with(.,'CERN. Geneva'))">
              <xsl:element name="{local-name(.)}">
                <xsl:copy-of select="@*"/>
                <xsl:value-of select="normalize-space(.)"/>
              </xsl:element>
            </xsl:if>
          </xsl:for-each>
        </xsl:element>
      </xsl:when>
    </xsl:choose>
</xsl:template>

<xsl:template match="marc:datafield[@tag=773]">
    <datafield tag="773" ind1=" " ind2=" ">
      <xsl:for-each select="./marc:subfield">
        <xsl:choose>
          <xsl:when test="@code='p'">
            <xsl:call-template name="output-773p-subfield">
              <xsl:with-param name="title" select="." />
            </xsl:call-template>
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

<xsl:template match="marc:datafield[@tag=856 and @ind1='4']">
    <xsl:choose>
      <xsl:when test="contains(./marc:subfield[@code='u'], 'http://cdsweb.cern.ch') and not(./marc:subfield[@code='z'] = 'Figure') and substring(./marc:subfield[@code='u'], (string-length(./marc:subfield[@code='u']) - string-length('pdf')) + 1) = 'pdf'">
        <datafield tag="FFT" ind1="" ind2="">
          <subfield code="a">
            <xsl:value-of select="./marc:subfield[@code='u']" />
          </subfield>
          <subfield code="t">INSPIRE-PUBLIC</subfield>
        </datafield>
      </xsl:when>
      <xsl:when test="not(contains(./marc:subfield[@code='u'], 'http://cdsweb.cern.ch'))  and not(contains(./marc:subfield[@code='u'], 'http://cms.cern.ch')) and not(contains(./marc:subfield[@code='u'], 'http://cmsdoc.cern.ch')) and not(contains(./marc:subfield[@code='u'], 'http://documents.cern.ch')) and not(contains(./marc:subfield[@code='u'], 'http://preprints.cern.ch')) and not(substring(./marc:subfield[@code='u'], (string-length(./marc:subfield[@code='u']) - string-length('ps.gz')) + 1) = 'ps.gz')">
        <xsl:element name="{local-name(.)}">
          <xsl:copy-of select="@*"/>
          <xsl:for-each select="./marc:subfield">
            <xsl:element name="{local-name(.)}">
              <xsl:copy-of select="@*"/>
              <xsl:value-of select="normalize-space(.)"/>
            </xsl:element>
          </xsl:for-each>
        </xsl:element>
      </xsl:when>
    </xsl:choose>
</xsl:template>

<xsl:template match="marc:datafield[@tag=520] | marc:datafield[@tag=245] | marc:datafield[@tag=242] | marc:datafield[@tag=500]">
    <xsl:element name="{local-name(.)}">
      <xsl:copy-of select="@*"/>
      <xsl:for-each select="./marc:subfield">
        <xsl:element name="{local-name(.)}">
          <xsl:copy-of select="@*"/>
          <xsl:value-of select="normalize-space(.)"/>
        </xsl:element>
      </xsl:for-each>
    </xsl:element>
</xsl:template>
</xsl:stylesheet>
