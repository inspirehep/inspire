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
                        <subfield code="a">INST-<xsl:value-of select="./inst"/></subfield>
                    </datafield>
                </xsl:if>

                <!--print 270 - this will be there anyway unless there are no subtags-->
               <xsl:if test="imc or country.code or state.code or address or phone-number or city">
                <datafield tag="270" ind1=" " ind2=" ">
                <xsl:for-each select="*">
	            <xsl:if test="name()='imc'">
                        <subfield code="z"><xsl:value-of select="."/></subfield>
                    </xsl:if>
	            <xsl:if test="name()='country.code'">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </xsl:if>

	            <xsl:if test="name()='state.code'">
                        <subfield code="s"><xsl:value-of select="."/></subfield>
                    </xsl:if>

	            <xsl:if test="name()='address'">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </xsl:if>

	            <xsl:if test="name()='phone-number'">
                        <subfield code="l"><xsl:value-of select="."/></subfield>
                    </xsl:if>

	            <xsl:if test="name()='director-note'">
                        <subfield code="n"><xsl:value-of select="."/></subfield>
                    </xsl:if>

	            <xsl:if test="name()='director-date'">
                        <subfield code="d"><xsl:value-of select="."/></subfield>
                    </xsl:if>

	            <xsl:if test="name()='city'">
                        <subfield code="b"><xsl:value-of select="."/></subfield>
                    </xsl:if>

                </xsl:for-each>
                </datafield>
               </xsl:if>
                <!--add collection id-->
                <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a">DIRECTORY</subfield>
                </datafield>         
            </record>
<xsl:text>
</xsl:text>
           
        </xsl:for-each> 
    </collection>

</xsl:template>

</xsl:stylesheet>
