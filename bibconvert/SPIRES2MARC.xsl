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
                       <datafield  ind1=" " ind2=" ">
		<xsl:choose>
                   <xsl:when test="position()=1">
			<xsl:attribute name="tag">100</xsl:attribute>
		   </xsl:when>
		   <xsl:otherwise>
			<xsl:attribute name="tag">700</xsl:attribute>
		   </xsl:otherwise>
		   </xsl:choose>	
                   
                         <subfield code="a"><xsl:value-of select="./author"/></subfield>      
			<xsl:if test="../affiliation">
				<xsl:for-each select="../affiliation">
					<xsl:if test="@type='AUTHAFF'">
                                	<subfield code="u"><xsl:value-of select="."/>
                            		</subfield>
                                	<subfield code="i"><xsl:value-of select="@key"/>
                            		</subfield>
					</xsl:if>
                              </xsl:for-each>
                        </xsl:if>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./astr">                            
			<xsl:if test="./affiliation">
				<xsl:for-each select="./affiliation">
					<xsl:if test="@type='RECAFF'">
					 <datafield tag="902" ind1=" " ind2=" ">
                                	<subfield code="a"><xsl:value-of select="."/>
                            		</subfield>
                                	<subfield code="i"><xsl:value-of select="@key"/>
                            		</subfield>
					</datafield>
					</xsl:if>
                                </xsl:for-each>
                        </xsl:if>
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
		<!--this really should not be empty-->
    		    <xsl:if test="string(./title)">
                    <datafield tag="245" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./title"/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:if>
                <xsl:for-each select="./pub-note">
                    <xsl:if test="string(.)">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./date">
                    <xsl:if test="string(.)">
                    <datafield tag="269" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/>
			</subfield>
                    </datafield>
		    <datafield tag="260" ind1=" " ind2=" ">
			<subfield code="c">
			<xsl:value-of select='substring(., 1, 4)'/>
                        </subfield>
		     </datafield>
                     </xsl:if>                     
                </xsl:for-each>
                <xsl:if test="./jour-sub">
                    <xsl:if test="string(./jour-sub)">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./jour-sub"/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:if>
                <xsl:if test="./language">
                    <xsl:if test="string(./language)">
                    <datafield tag="041" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./language"/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:if>
                <xsl:if test="./ppf-subject">
                    <xsl:if test="string(./ppf-subject)">
                    <datafield tag="650" ind1="1" ind2="7">
                        <subfield code="a"><xsl:value-of select="./ppf-subject"/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:if>
                <xsl:if test="./p">
		  <xsl:if test="./p">
                    <datafield tag="300" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./p"/></subfield>
                    </datafield>
                   </xsl:if>
                </xsl:if>
                <xsl:for-each select="./citation">
		   <!--check that fullref, aref or jref actually has a value - not just empty tag-->
	           <xsl:if test="string(./fullref) or string(./aref) or string(./jref)">
		   <datafield tag="999" ind1="C" ind2="5">
  			 <xsl:if test="./fullref">
	                    <subfield code="b"><xsl:value-of select="./fullref"/></subfield>
	                </xsl:if>
			 <xsl:if test="./aref">
	                    <subfield code="r"><xsl:value-of select="./aref"/></subfield>
	                </xsl:if>
			 <xsl:if test="./jref">
	                    <subfield code="t"><xsl:value-of select="./jref"/></subfield>
	                </xsl:if>

                    </datafield>
                    </xsl:if>
                </xsl:for-each> <!--citations-->
                <xsl:for-each select="./meeting-note">
	            <xsl:if test="string(.)">
                    <datafield tag="111" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
		    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./note">
	            <xsl:if test="string(.)">
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
		    </xsl:if>
                </xsl:for-each>
                <xsl:if test="./report-cancel">
	            <xsl:if test="string(./report-cancel)">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="c">DELETED</subfield>
                    </datafield>
                    </xsl:if>
                </xsl:if>
                <xsl:if test="./experiment">
	            <xsl:if test="string(./experiment)">
                    <datafield tag="693" ind1=" " ind2=" ">
                        <subfield code="e"><xsl:value-of select="./experiment"/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:if>
                <xsl:for-each select="./desy-pub-note">
	            <xsl:if test="string(.)">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./desy-keywords">
	            <xsl:if test="string(.)">
                    <datafield tag="653" ind1="1" ind2=" ">
                        <subfield code="9">DESY</subfield>
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./desy-abs-num">
	            <xsl:if test="string(.)">
                    <datafield tag="088" ind1=" " ind2=" ">
                        <subfield code="9">DESY</subfield>
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./title-variant">
	            <xsl:if test="string(.)">
                    <datafield tag="210" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./old-title">
	            <xsl:if test="string(.)">
                    <datafield tag="246" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
		    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./other-author">
	            <xsl:if test="string(.)">
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
		    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./tt">
		    <xsl:if test="string(.)">
                    <datafield tag="246" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./bull">
                    <datafield tag="037" ind1="" ind2="">
                        <subfield code="a"><xsl:value-of select="."/></subfield>			<subfield code="s">arxiv</subfield>
                    </datafield>
                </xsl:for-each>
                <xsl:for-each select="./date-added">
	            <xsl:if test="string(.)">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="x"><xsl:value-of select="."/></subfield>
                    </datafield>
		    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./date-updated">
	            <xsl:if test="string(.)">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </datafield>
		    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./abstract">
	           <xsl:if test="string(./abstract-source) or string(./abstract-text)">
                    <datafield tag="520" ind1=" " ind2=" ">
                        <xsl:if test="string(./abstract-text)">
                        <subfield code="a">
                           <xsl:value-of select="./abstract-text"/>
                        </subfield>
                        </xsl:if>
                        <xsl:if test="string(./abstract-source)">
                        <subfield code="s">
                           <xsl:value-of select="./abstract-source"/>
                        </subfield>
                        </xsl:if>
                    </datafield>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./url-str">
                    <!--check this thing has at least one of the fields below-->
		    <xsl:if test="string(./urldoc) or string(./url) or string(./turl)">
                    <datafield tag="856" ind1="4" ind2=" ">
		        <xsl:if test="string(./urldoc)">
                        <subfield code="x"><xsl:value-of select="./urldoc"/></subfield>
                        </xsl:if>
		        <xsl:if test="string(./url)">
                        <subfield code="y"><xsl:value-of select="./url"/></subfield>
                        </xsl:if>
			<xsl:if test="string(./turl)">
		 	<subfield code="u"><xsl:value-of select="./turl"/></subfield>
                        </xsl:if>
                    </datafield>
                    </xsl:if>
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
                <xsl:if test="./uniquetex">
                    <datafield tag="971" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                </xsl:if>
            </record>
        </xsl:for-each> 
    </collection>

</xsl:template>

</xsl:stylesheet>
