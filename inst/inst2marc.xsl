<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id$ -->
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="UTF-8"/>
<xsl:template match="/">
    <collection xmlns="http://www.loc.gov/MARC21/slim">
        <xsl:for-each select="//goal_record">    
            <record>
                <xsl:if test="./inst">
                    <datafield tag="970" ind1=" " ind2=" ">
                        <subfield code="b">INST-<xsl:value-of select="./inst"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./imc">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="z"><xsl:value-of select="./imc"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./country.code">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="./country.code"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./city">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="b"><xsl:value-of select="./city"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./state.code">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="s"><xsl:value-of select="./state-code"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./inst.catch.name">
                    <datafield tag="110" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./inst.catch.name"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./director">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="p"><xsl:value-of select="./phone.number"/></subfield>
                    </datafield>
                </xsl:if>

                <xsl:if test="./date-updated">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="./phone.number"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./director">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="x"><xsl:value-of select="./phone.number"/></subfield>
                    </datafield>
                </xsl:if>

                <xsl:for-each select="./address">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./phone-number">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="l"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./director-note">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="n"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./director-date">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="d"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./desy.aff">
                    <datafield tag="595" ind1=" " ind2=" ">
                        <subfield code="d"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./type">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./xtra-index">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="b"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./desylookup">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>

                <xsl:for-each select="./oaff-str/other.aff">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>


                <xsl:for-each select="./email.contact">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="m"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./note1">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./url">
                    <datafield tag="856" ind1=" " ind2=" ">
                        <subfield code="u"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./street-address">
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:for-each>
   	        <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a">DIRECTORY</subfield>
                </datafield>
	    </record>
	   <!--insert a blank line between records-->
<xsl:text>

</xsl:text>
        </xsl:for-each> 
    </collection>

</xsl:template>

</xsl:stylesheet>
