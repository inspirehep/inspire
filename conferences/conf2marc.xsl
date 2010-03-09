<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id$ -->
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="UTF-8"/>
<xsl:template match="/">
    <collection xmlns="http://www.loc.gov/MARC21/slim">
        <xsl:for-each select="//goal_record">
            <record>
                <xsl:if test="./mconf">
                    <datafield tag="970" ind1=" " ind2=" ">
                        <subfield code="a">CONF-<xsl:value-of select="./mconf"/></subfield>
                    </datafield>
                </xsl:if>


                <xsl:for-each select="*">
	            <xsl:if test="name()='c-number'">
		     <datafield tag="111" ind1=" " ind2=" ">
                        <subfield code="g"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>

	            <xsl:if test="name()='dates'">
		     <datafield tag="111" ind1=" " ind2=" ">
                        <subfield code="d"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>

	            <xsl:if test="name()='date-qual'">
		     <datafield tag="269" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>

	            <xsl:if test="name()='place'">
		     <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='place'">
		     <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='title'">
		     <datafield tag="245" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='attendance-info'">
		     <datafield tag="912" ind1=" " ind2=" ">
                        <subfield code="i"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='info-address'">
		     <datafield tag="912" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='source'">
		     <datafield tag="111" ind1=" " ind2=" ">
                        <subfield code="9"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='ppf'">
		     <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>



	            <xsl:if test="name()='other-title'">
		     <datafield tag="210" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='email'">
		     <datafield tag="912" ind1=" " ind2=" ">
                        <subfield code="m"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='phone'">
		     <datafield tag="912" ind1=" " ind2=" ">
                        <subfield code="k"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='fax'">
		     <datafield tag="912" ind1=" " ind2=" ">
                        <subfield code="j"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='url'">
		     <datafield tag="856" ind1="4" ind2=" ">
                        <subfield code="u"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='newurl'">
		     <datafield tag="856" ind1="4" ind2=" ">
                        <subfield code="u"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='pbn'">
		     <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="x"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
			            <xsl:if test="name()='series'">
		     <datafield tag="490" ind1="4" ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>
	            <xsl:if test="name()='note'">
		     <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
		     </datafield>
                    </xsl:if>


		</xsl:for-each>

                <!--add collection id-->
                <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a">CONFERENCES</subfield>
                </datafield>


            </record>

<xsl:text>
</xsl:text>

        </xsl:for-each>
    </collection>

</xsl:template>

</xsl:stylesheet>
