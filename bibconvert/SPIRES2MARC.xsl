<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id$ -->
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="UTF-8"/>
<xsl:template match="/">
    <collection xmlns="http://www.loc.gov/MARC21/slim">
        <xsl:for-each select="//goal_record">    
            <record>
                <xsl:if test="./doc-type">
                    <datafield tag="690" ind1="C" ind2=" ">
                        <subfield code="a"><xsl:value-of select="./doc-type"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:for-each select="./report-num">
                    <datafield tag="037" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./astr/astr1">
                    <datafield tag="100" ind1=" " ind2=" ">
                            <subfield code="a"><xsl:value-of select="./author"/></subfield>
                            
			<xsl:if test="../affiliation">
				  <xsl:for-each select="../affiliation">
                                <subfield code="u"><xsl:value-of select="."/>
                            </subfield>
                              </xsl:for-each>

                            </xsl:if>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./corp-author">
                    <datafield tag="110" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./col-note">
                    <datafield tag="710" ind1=" " ind2=" ">
                        <subfield code="g"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:if test="./title">
                    <datafield tag="245" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./title"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:for-each select="./pub-note">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./slac-topics">
                    <datafield tag="650" ind1="2" ind2="7">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                        <subfield code="2">SLAC author</subfield>
                    </datafield>
                </xsl:for-each> 
                <xsl:for-each select="./date">
                    <datafield tag="269" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:if test="./jour-sub">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./jour-sub"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./language">
                    <datafield tag="041" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./language"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./ppf-subject">
                    <datafield tag="650" ind1="1" ind2="7">
                        <subfield code="a"><xsl:value-of select="./ppf-subject"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./holdings">
                    <datafield tag="866" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./holdings"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./p">
                    <datafield tag="300" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./p"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:for-each select="./citation">
                    <datafield tag="999" ind1="C" ind2="5">
                        <subfield code="m"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./meeting-note">
                    <datafield tag="111" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./note">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:if test="./report-cancel">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="c">DELETED</subfield>
                    </datafield>
                </xsl:if>
                <xsl:for-each select="./citation">
                    <datafield tag="999" ind1="C" ind2="5">
                        <subfield code="t"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:if test="./experiment">
                    <datafield tag="693" ind1=" " ind2=" ">
                        <subfield code="e"><xsl:value-of select="./experiment"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:for-each select="./desy-pub-note">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./desy-keywords">
                    <datafield tag="653" ind1="1" ind2=" ">
                        <subfield code="9">DESY</subfield>
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./desy-abs-num">
                    <datafield tag="088" ind1=" " ind2=" ">
                        <subfield code="9">DESY</subfield>
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./title-variant">
                    <datafield tag="210" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./old-title">
                    <datafield tag="246" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./other-author">
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./tt">
                    <datafield tag="246" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./bull">
                    <datafield tag="037" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./date-added">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="x"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./date-updated">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./url-str">
                    <datafield tag="856" ind1="4" ind2=" ">
                        <subfield code="u"><xsl:value-of select="./urldoc"/></subfield>
                        <subfield code="y"><xsl:value-of select="./url"/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./free-keywords">
                    <datafield tag="653" ind1="1" ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./doi">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:if test="./irn">
                    <datafield tag="970" ind1=" " ind2=" ">
                        <subfield code="a">SPIRES-<xsl:value-of select="./irn"/></subfield>
                    </datafield>
                </xsl:if>
            </record>
        </xsl:for-each> 
    </collection>

</xsl:template>

</xsl:stylesheet>
