<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id$ -->
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="UTF-8"/>
<xsl:template match="/">
    <collection xmlns="http://www.loc.gov/MARC21/slim">
        <xsl:for-each select="//goal_record">    
           <!-- xsl:sort select="date"/ -->
           <!-- uncomment if you want to sort by insertion date-->
<xsl:text>
</xsl:text>
            <record>
                <xsl:if test="string(./doc-type)">
                    <datafield tag="690" ind1="C" ind2=" ">
                        <subfield code="a"><xsl:value-of select="./doc-type"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:for-each select="./report-num">
                    <xsl:if test="string(.)">
                    <datafield tag="037" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./astr/astr1">
		       <!--these are author entries so do stuff only if author exists and is not empty-->
                       <xsl:if test="string(./author)">
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
			<xsl:if test="string(../affiliation)">
				<xsl:for-each select="../affiliation">
                                        <xsl:if test="string(normalize-space(.))">
					<xsl:if test="@type='AUTHAFF'">
                                	  <subfield code="u"><xsl:value-of select='normalize-space(.)'/>
                            		  </subfield>
                                	  <subfield code="i"><xsl:value-of select="@key"/>
                            		 </subfield>
					</xsl:if>
					</xsl:if>
                              </xsl:for-each>
                        </xsl:if>
                        </datafield>
<xsl:text>
</xsl:text>
                        </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./astr">                            
			<xsl:if test="string(normalize-space(./affiliation))">
				<xsl:for-each select="./affiliation">
					<xsl:if test="@type='RECAFF'">
					 <datafield tag="902" ind1=" " ind2=" ">
                                	<subfield code="a"><xsl:value-of select="normalize-space(.)"/>
                            		</subfield>
                                	<subfield code="i"><xsl:value-of select="@key"/>
                            		</subfield>
					</datafield>
<xsl:text>
</xsl:text>
					</xsl:if>
                                </xsl:for-each>
                        </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./corp-author">
                    <xsl:if test="string(.)">
                    <datafield tag="110" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                    </xsl:if>
                </xsl:for-each>
                <xsl:for-each select="./col-note">
                    <xsl:if test="string(.)">
                    <datafield tag="710" ind1=" " ind2=" ">
                        <subfield code="g"><xsl:value-of select="."/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
		    </xsl:if>
                </xsl:for-each>
                <xsl:if test="string(./title)">
                    <datafield tag="245" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./title"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:for-each select="./jour-info">
			<datafield tag="773" ind1=" " ind2=" ">
                               <xsl:if test="string(normalize-space(./jname))">
                                <subfield code="p"><xsl:value-of select="./jname"/>
                            	</subfield>
                               </xsl:if>
                               <xsl:if test="string(normalize-space(./jvol))">
                                <subfield code="v"><xsl:value-of select="./jvol"/>
                            	</subfield>
                               </xsl:if>
                               <xsl:if test="string(normalize-space(./jpage))">
                                <subfield code="c"><xsl:value-of select="./jpage"/>
                            	</subfield>
                               </xsl:if>
                               <xsl:if test="string(normalize-space(./jyear))">
                                <subfield code="y"><xsl:value-of select="./jyear"/>
                            	</subfield>
                               </xsl:if>
				<xsl:if test="string(normalize-space(./doi))">	
	                          <subfield code="a"><xsl:value-of select="./doi"/>
				  </subfield>
				</xsl:if>
			</datafield>
<xsl:text>
</xsl:text>
                </xsl:for-each>

                <xsl:for-each select="./conf">
                       <xsl:if test="string(./conf-code) or string(./conf-dates) or string(conf-place) or string(./conf-start)">
			<datafield tag="111" ind1=" " ind2=" ">
                                <xsl:if test="string(./conf-code)">
                                <subfield code="g"><xsl:value-of select="./conf-code"/></subfield>
                                </xsl:if>
                                <xsl:if test="string(./conf-dates)">
                                <subfield code="d"><xsl:value-of select="./conf-dates"/></subfield>
                                </xsl:if>
                                <xsl:if test="string(./conf-place)">
                                <subfield code="c"><xsl:value-of select="./conf-place"/></subfield>
                                </xsl:if>
                                <xsl:if test="string(./conf-start)">
                                <subfield code="9"><xsl:value-of select="./conf-start"/></subfield>
                                </xsl:if>
			</datafield>
                       </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./date">
                    <xsl:if test="string(.)">
                    <datafield tag="269" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/>
			</subfield>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>
		    <datafield tag="260" ind1=" " ind2=" ">
			<subfield code="c">
			<xsl:value-of select='substring(., 1, 4)'/>
                        </subfield>
		     </datafield>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:if test="string(./jour-sub)">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="p"><xsl:value-of select="./jour-sub"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:if test="string(./language)">
                    <datafield tag="041" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./language"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:if test="string(./ppf-subject)">
                    <datafield tag="650" ind1="1" ind2="7">
                        <subfield code="a"><xsl:value-of select="./ppf-subject"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:if test="string(./p)">
                    <datafield tag="300" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./p"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:for-each select="./citation">
                   <!--do not print empty headers-->
                   <xsl:if test="string(./fullref) or string(./aref) or string(./jref)">
		   <datafield tag="999" ind1="C" ind2="5">
  			<xsl:if test="string(./fullref)">
	                    <subfield code="m"><xsl:value-of select="./fullref"/></subfield>
	                </xsl:if>
			<xsl:if test="string(./aref)">
	                    <subfield code="r"><xsl:value-of select="./aref"/></subfield>
	                </xsl:if>
			<xsl:if test="string(./jref)">
	                    <subfield code="s"><xsl:value-of select="./jref"/></subfield>
	                </xsl:if>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./note">
		  <xsl:if test="string(normalize-space(./note))"> 
                    <datafield tag="500" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                  </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:if test="./report-cancel">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="c">DELETED</subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:if test="string(normalize-space(./experiment))">
                    <datafield tag="693" ind1=" " ind2=" ">
                        <subfield code="e"><xsl:value-of select="./experiment"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>
                </xsl:if>
                <xsl:for-each select="./desy-pub-note">
                   <xsl:if test="string(normalize-space(.))">
                    <datafield tag="773" ind1=" " ind2=" ">
                        <subfield code="x"><xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./desy-keywords">
                   <xsl:if test="string(normalize-space(.))">
                    <datafield tag="653" ind1="1" ind2=" ">
                        <subfield code="9">DESY</subfield>
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./desy-abs-num">
                   <xsl:if test="string(normalize-space(.))">
                    <datafield tag="970" ind1=" " ind2=" ">
                        <subfield code="9">DESY</subfield>
                        <subfield code="a">DESY-<xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./title-variant">
                   <xsl:if test="string(normalize-space(.))">
                    <datafield tag="210" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./old-title">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(normalize-space(.))">
                     <datafield tag="246" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                     </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./other-author">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(normalize-space(.))">
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./tt">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(normalize-space(.))">      
                    <datafield tag="246" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./lanl">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(./bull) or string(./cat)">
                    <datafield tag="037" ind1="" ind2="">
                        <xsl:if test="string(./bull)">
                         <subfield code="a"><xsl:value-of select="./bull"/></subfield>			
                        </xsl:if>
			<subfield code="9">arxiv</subfield>
                        <xsl:if test="string(./cat)">
               			<subfield code="c"><xsl:value-of select="./cat"/></subfield>
                        </xsl:if>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./date-added">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(.)">                    
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="x"><xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./date-updated">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(.)">
                    <datafield tag="961" ind1=" " ind2=" ">
                        <subfield code="c"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>
                </xsl:for-each>
                <xsl:for-each select="./abstract">
                    <!--do stuff only if there are real values-->
                    <xsl:if test="string(normalize-space(./abstract-text)) or string(normalize-space(./abstract-source))">
                    <datafield tag="520" ind1=" " ind2=" ">
                        <xsl:if test="string(normalize-space(./abstract-text))"> 
                         <subfield code="a">
                           <xsl:value-of select='normalize-space(./abstract-text)'/>
                         </subfield>
                        </xsl:if>
                        <xsl:if test="string(normalize-space(./abstract-source))">
                         <subfield code="9">
                           <xsl:value-of select='normalize-space(normalize-space(./abstract-source))'/>
                         </subfield>
                        </xsl:if>                        
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>
  		    <xsl:for-each select="./archive-cat">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(.)">
        	     	<datafield tag="694" ind1=" " ind2=" ">
                    	    <subfield code="a"><xsl:value-of select="."/></subfield>
		        	<subfield code="9">arxiv</subfield>              	
		    	</datafield>
                     </xsl:if>
<xsl:text>
</xsl:text>
	             </xsl:for-each>
                </xsl:for-each>
                <xsl:for-each select="./url-str">
                   <!--do not print tags for empty values-->
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
<xsl:text>
</xsl:text>        	 
                </xsl:for-each>
                <xsl:for-each select="./free-keywords">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(.)">
                    <datafield tag="653" ind1="1" ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                   </xsl:if>
<xsl:text>
</xsl:text>        	 
                </xsl:for-each>
                <xsl:if test="string(./irn)">
                    <datafield tag="970" ind1=" " ind2=" ">
                        <subfield code="a">SPIRES-<xsl:value-of select="./irn"/></subfield>
                    </datafield>
<xsl:text>
</xsl:text>        	 
                </xsl:if>
                <xsl:if test="string(./uniquetex)">
                    <datafield tag="035" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="./uniquetex"/></subfield>
                        <subfield code="9">SPIRESTeX</subfield>
                    </datafield>
<xsl:text>
</xsl:text>        	 
                </xsl:if>
                <xsl:for-each select="./collection">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(.)">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>        	 
		</xsl:for-each>
                <xsl:for-each select="./topic">
                   <!--do not print tags for empty values-->
                    <xsl:if test="string(.)">
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a"><xsl:value-of select="."/></subfield>
                    </datafield>
                    </xsl:if>
<xsl:text>
</xsl:text>        	 
		</xsl:for-each>
            </record>
        </xsl:for-each> 
    </collection>

</xsl:template>

</xsl:stylesheet>
