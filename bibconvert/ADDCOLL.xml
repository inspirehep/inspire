<?xml version="1.0" encoding="ISO-8859-1"?>
<!--creates records with collectionids to be added in Inspire -->
<!--by bibupload -a -->
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="UTF-8"/>
<xsl:template match="/">
    <collection xmlns="http://www.loc.gov/MARC21/slim">
        <xsl:for-each select="//record">    
            <record>
                <xsl:if test="./irn">
                    <datafield tag="970" ind1=" " ind2=" ">
                        <subfield code="a">SPIRES-<xsl:value-of select="./irn"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./collection">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="b"><xsl:value-of select="./collection"/></subfield>
                    </datafield>
                </xsl:if>
                <xsl:if test="./topic">
                    <datafield tag="650" ind1="2" ind2="7">
                        <subfield code="a"><xsl:value-of select="./topic"/></subfield>
                    </datafield>
                </xsl:if>

            </record>
            <xsl:text>

            </xsl:text>
        </xsl:for-each> 
    </collection>

</xsl:template>

</xsl:stylesheet>
