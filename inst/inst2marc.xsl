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

		<xsl:for-each select="*">			
			<xsl:if test="name()='inst.catch.name'">
        	    		<datafield tag="110" ind1=" " ind2=" ">
                	       		<subfield code="a"><xsl:value-of select="."/></subfield>
                    		</datafield>
			</xsl:if>

			<xsl:if test="name()='department'">
        	    		<datafield tag="110" ind1=" " ind2=" ">
                	       		<subfield code="b"><xsl:value-of select="."/></subfield>
                    		</datafield>
                	</xsl:if>
	
			<xsl:if test="name()='desy.aff'">
        	    		<datafield tag="595" ind1="" ind2=" ">
                	       		<subfield code="a"><xsl:value-of select="."/></subfield>
                	       		<subfield code="9">DESY</subfield>
                    		</datafield>
                	</xsl:if>


			<xsl:if test="name()='note1'">
        	    		<datafield tag="500" ind1="" ind2=" ">
                	       		<subfield code="a"><xsl:value-of select="."/></subfield>
                    		</datafield>
                	</xsl:if>
			<xsl:if test="name()='url'">
        	    		<datafield tag="856" ind1="" ind2=" ">
                	       		<subfield code="u"><xsl:value-of select="."/></subfield>
                    		</datafield>
                	</xsl:if>
			<xsl:if test="name()='type'">
          	    		<datafield tag="980" ind1="" ind2=" ">				
				<xsl:call-template name="output-tokens">
					<xsl:with-param name="list"><xsl:value-of select="."/></xsl:with-param>
					<xsl:with-param name="delimiter">, </xsl:with-param>
					<xsl:with-param name="code">a</xsl:with-param>
				</xsl:call-template>
				</datafield>
                	</xsl:if>

		</xsl:for-each>



		<xsl:if test="xtra-index">
	    		<datafield tag="595" ind1="" ind2=" ">
			<xsl:for-each select="*">               
				<xsl:if test="name()='xtra-index'">
	       				<subfield code="b"><xsl:value-of select="."/></subfield>
				</xsl:if>
			</xsl:for-each>	
               		</datafield>
                </xsl:if>

		<xsl:if test="desylookup or oaff">
       	    		<datafield tag="595" ind1="" ind2=" ">
			<xsl:for-each select="*">               	
				<xsl:if test="name()='desylookup'">
               	       			<subfield code="a"><xsl:value-of select="."/></subfield>
	                	</xsl:if>
				<xsl:if test="name()='oaff'">
               	       			<subfield code="a"><xsl:value-of select="."/></subfield>
	                	</xsl:if>
			</xsl:for-each>
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
                        <subfield code="a">INSTITUTIONS</subfield>
                </datafield>         
            </record>
<xsl:text>
</xsl:text>
           
        </xsl:for-each> 
    </collection>

</xsl:template>



<xsl:template name="output-tokens">
<xsl:param name="list"/>
<xsl:param name="delimiter"/>
<xsl:param name="code"/>
<xsl:variable name="newlist">
<xsl:choose>
<xsl:when test="contains($list, $delimiter)">
<xsl:value-of select="normalize-space($list)"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="concat(normalize-space($list), $delimiter)"/>
</xsl:otherwise>
</xsl:choose>
</xsl:variable>
<xsl:variable name="first" select="substring-before($newlist, $delimiter)"/>
<xsl:variable name="remaining" select="substring-after($newlist, $delimiter)"/>
<subfield>
<xsl:attribute name = "code">
<xsl:value-of select="$code"/>
</xsl:attribute>
<xsl:value-of select="$first"/>
</subfield>
<xsl:if test="$remaining">
<xsl:call-template name="output-tokens">
<xsl:with-param name="list" select="$remaining"/>
<xsl:with-param name="delimiter">
<xsl:value-of select="$delimiter"/>
</xsl:with-param>
<xsl:with-param name="code">
<xsl:value-of select="$code"/>
</xsl:with-param>
</xsl:call-template>
</xsl:if>
</xsl:template>





</xsl:stylesheet>
