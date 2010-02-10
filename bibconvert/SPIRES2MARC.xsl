<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id$ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8"/>
  <xsl:template match="/">
    <collection xmlns="http://www.loc.gov/MARC21/slim">
      <xsl:for-each select="//goal_record">    
	<!-- xsl:sort select="date"/ -->
	<!-- uncomment if you want to sort by insertion date-->

	<record>
	  <xsl:text>&#10;</xsl:text>	  

	  <xsl:if test="string(./irn)">
	    <datafield tag="970" ind1=" " ind2=" ">
	      <subfield code="a">
		<xsl:text>SPIRES-</xsl:text>
		<xsl:value-of select="normalize-space(./irn)"/>
	      </subfield>
	    </datafield>
	  </xsl:if>

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
		
		<subfield code="a">
		  <xsl:value-of select="normalize-space(./author)"/>
		</subfield>      
		
		<!--test for desy-author string, used to store INSPIRE ids-->
		<xsl:choose> 
		  <xsl:when test="contains(./desy-author,'INSPIRE-')">
		    <subfield code="i">
		      <xsl:value-of select="normalize-space(./desy-author)"/>
		    </subfield>
		  </xsl:when>
		  <xsl:when test="contains(./desy-author,'SLAC-')">
		    <subfield code="j">
		      <xsl:value-of select="normalize-space(./desy-author)"/>
		    </subfield>                                
		  </xsl:when>
		  <xsl:otherwise>
		    <xsl:if test="string(./desy-author)">
		      <subfield code="q">
			<xsl:value-of select="normalize-space(./desy-author)"/>
		      </subfield>            
                    </xsl:if>
		  </xsl:otherwise>
		</xsl:choose>
		<!--process affils that are connected explicitly to
			    this author, currently store all in 100u-->
		<xsl:if test="string(../affiliation)">
		  <xsl:for-each select="../affiliation">
		    <xsl:if test="string(normalize-space(.))">
		      <xsl:if test="@type='AUTHAFF'">
			<subfield code="u">
			  <xsl:value-of select='normalize-space(.)'/>
			</subfield>
		      </xsl:if>
		    </xsl:if>
		  </xsl:for-each>
		</xsl:if>
	      </datafield>
	      <xsl:text>&#10;</xsl:text>
	    </xsl:if>
	  </xsl:for-each>
	  
	  <xsl:for-each select="./astr">                            
	    <xsl:if test="string(normalize-space(./affiliation))">
	      <xsl:for-each select="./affiliation">
		<xsl:if test="@type='RECAFF'">
		  <datafield tag="902" ind1=" " ind2=" ">
		    <subfield code="a">
		      <xsl:value-of select="normalize-space(.)"/>
		    </subfield>
		  </datafield>
		  <xsl:text>&#10;</xsl:text>
		</xsl:if>
	      </xsl:for-each>
	    </xsl:if>
	  </xsl:for-each>
	  
	  <xsl:for-each select="./jour-info">
	    <xsl:choose>
	      <xsl:when test= "./jname='Conf.Proc.' or ./jname = 'eConf'">           
		<datafield tag="773" ind1=" " ind2=" ">
		  <xsl:if test="string(normalize-space(./jvol))">
		    <subfield code="w">
		      <xsl:value-of select="normalize-space(./jvol)"/>
		    </subfield>
		  </xsl:if>
		  <xsl:if test="string(normalize-space(./jpage))">
		    <subfield code="c">
		      <xsl:value-of select="normalize-space(./jpage)"/>
		    </subfield>
		  </xsl:if>
		  <xsl:if test="string(normalize-space(./jyear))">
		    <subfield code="y">
		      <xsl:value-of select="normalize-space(./jyear)"/>
		    </subfield>
		  </xsl:if>
		  <!-- If there is one doi and one publication we put them in the same 773 field -->
		  <xsl:if test="count(descendant::doi) = 1 and count(descendant::jpage) =1 and  string(normalize-space(./doi))">	
		    <subfield code="a">
		      <xsl:value-of select="normalize-space(./doi)"/>
		    </subfield>
		  </xsl:if>
		</datafield>
		<xsl:text>&#10;</xsl:text>
	      </xsl:when>
	      <xsl:otherwise>
		<datafield tag="773" ind1=" " ind2=" ">
		  <xsl:if test="string(normalize-space(./jname))">
		    <subfield code="p">
		      <xsl:value-of select="normalize-space(./jname)"/>
		    </subfield>
		  </xsl:if>
		  <xsl:if test="string(normalize-space(./jvol))">
		    <subfield code="v">
		      <xsl:value-of select="normalize-space(./jvol)"/>
		    </subfield>
		  </xsl:if>
		  <xsl:if test="string(normalize-space(./jpage))">
		    <subfield code="c">
		      <xsl:value-of select="normalize-space(./jpage)"/>
		    </subfield>
		  </xsl:if>
		  <xsl:if test="string(normalize-space(./jyear))">
		    <subfield code="y">
		      <xsl:value-of select="normalize-space(./jyear)"/>
		    </subfield>
		  </xsl:if>
		  <!-- If there is one doi and one publication we put them in the same 773 field -->
		  <xsl:if test="count(descendant::doi) = 1 and count(descendant::jpage) =1 and  string(normalize-space(./doi))">	
		    <subfield code="a">
		      <xsl:value-of select="normalize-space(./doi)"/>
		    </subfield>
		  </xsl:if>
		</datafield>
		<xsl:text>&#10;</xsl:text>
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:for-each>

	  <!-- if we are not able to determine which DOIs go with which publications -->
	  <!-- we put all dois here -->

	  <xsl:if test="count(descendant::doi) &gt; 1 or not(count(descendant::jpage)=1)">
	    <xsl:for-each select="descendant::doi">
	      <xsl:if test="string(normalize-space(.))">
		<datafield tag="773" ind1=" " ind2=" ">     
		  <subfield code="a">
		    <xsl:value-of select="normalize-space(.)"/>
		  </subfield>
		</datafield>
	      </xsl:if>
	      <xsl:text>&#10;</xsl:text>
	    </xsl:for-each>
	  </xsl:if>  
	  
	  <xsl:for-each select="./conf">
	    <xsl:if test="string(./conf-code) or string(./conf-pub) or string(./conf-page) or string(./conf-type)">
	      <datafield tag="773" ind1=" " ind2=" ">
		<xsl:if test="string(./conf-code)">
		  <subfield code="w">
		    <xsl:value-of select="normalize-space(./conf-code)"/>
		  </subfield>
		</xsl:if>
		<xsl:if test="string(./conf-page)">
		  <subfield code="c">
		    <xsl:value-of select="normalize-space(./conf-page)"/>
		  </subfield>
		</xsl:if>
		<xsl:if test="string(./conf-type)">
		  <subfield code="t">
		    <xsl:value-of select="normalize-space(./conf-type)"/>
		  </subfield>
		</xsl:if>
		<xsl:if test="count(../descendant::cpn) = 1">
		  <xsl:call-template name = "parse-cpn">
		    <xsl:with-param name="cpn">
		      <xsl:value-of select="normalize-space(../cpn/conf-pub-note)"/>
		    </xsl:with-param>
		  </xsl:call-template>
		</xsl:if>
	      </datafield>
	      <xsl:text>&#10;</xsl:text>
	    </xsl:if>
	  </xsl:for-each>

	  <xsl:text>&#10;</xsl:text>
	  <xsl:if test="string(./field-code)">
	    <xsl:call-template name="output-tokens">
	      <xsl:with-param name="list">
		<xsl:value-of select="normalize-space(./field-code)"/>
	      </xsl:with-param>
	      <xsl:with-param name="delimiter">, </xsl:with-param>
	      <xsl:with-param name="code">a</xsl:with-param>
	      <xsl:with-param name="tag">650</xsl:with-param>
	      <xsl:with-param name="ind1">1</xsl:with-param>
	      <xsl:with-param name="ind2">7</xsl:with-param>
	      <xsl:with-param name="sub2">2</xsl:with-param>
	      <xsl:with-param name="sub2_val">INSPIRE</xsl:with-param>
	    </xsl:call-template>  
	    <xsl:text>&#10;</xsl:text>
	  </xsl:if>

	  <xsl:if test="string(./type-code)">
	    <xsl:call-template name="output-tokens">
	      <xsl:with-param name="list">
		<xsl:value-of select="normalize-space(./type-code)"/>
	      </xsl:with-param>
	      <xsl:with-param name="delimiter">, </xsl:with-param>
	      <xsl:with-param name="code">a</xsl:with-param>
	      <xsl:with-param name="tag">690</xsl:with-param>
	      <xsl:with-param name="ind1">C</xsl:with-param>
	      <xsl:with-param name="sub2">2</xsl:with-param>
	      <xsl:with-param name="sub2_val">INSPIRE</xsl:with-param>
	    </xsl:call-template>
	    <xsl:text>&#10;</xsl:text>
	  </xsl:if>

	  <xsl:for-each select="./citation">
	    <!--do not print empty headers-->
	    <xsl:if test="string(./fullref) or string(./aref) or string(./jref)">
	      <datafield tag="999" ind1="C" ind2="5">
		<xsl:if test="string(./aref)">
		  <subfield code="r">
		    <xsl:value-of select="normalize-space(./aref)"/>
		  </subfield>
		</xsl:if>
		<xsl:if test="string(./jref)">
		  <subfield code="s">
		    <xsl:value-of select="normalize-space(./jref)"/>
		  </subfield>
		</xsl:if>
	      </datafield>
	    </xsl:if>
	    <xsl:text>&#10;</xsl:text>
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
		  <xsl:choose>
		    <xsl:when test="normalize-space(./abstract-source)='arxiv'">
		      <xsl:text>arXiv</xsl:text>
		    </xsl:when>
		    <xsl:otherwise>
		      <xsl:value-of select='normalize-space(./abstract-source)'/>
		    </xsl:otherwise>
		  </xsl:choose>
		  </subfield>
		</xsl:if>                        
	      </datafield>
	    </xsl:if>
	    <xsl:text>&#10;</xsl:text>	   
	  </xsl:for-each>

	  <xsl:for-each select="./url-str">
	    <!--do not print tags for empty values-->
	    <xsl:if test="string(./urldoc) or string(./url) or string(./turl)">
	      <datafield tag="856" ind1="4" ind2=" ">
		<xsl:if test="string(./urldoc)">
		  <subfield code="w">
		    <xsl:value-of select="normalize-space(./urldoc)"/>
		  </subfield>
		</xsl:if>
		<xsl:if test="string(./url)">
		  <subfield code="y">
		    <xsl:value-of select="normalize-space(./url)"/>
		  </subfield>
		</xsl:if>
		<xsl:if test="string(./turl)">
		  <subfield code="u">
		    <xsl:value-of select="normalize-space(./turl)"/>
		  </subfield>
		</xsl:if>
	      </datafield>
	    </xsl:if>
	    <xsl:text>&#10;</xsl:text>
	  </xsl:for-each>
	  
	  <xsl:for-each select="./lanl">
	    <!--do not print tags for empty values-->
	    <xsl:if test="string-length(./bull) > 3 and string(./cat)">
	      <datafield tag="037" ind1=" " ind2=" ">
		<xsl:if test="string(./bull)">
		  <subfield code="a">
		    <xsl:value-of select="normalize-space(./bull)"/>
		  </subfield>			
		</xsl:if>
		<subfield code="9">arXiv</subfield>
		<xsl:if test="string(./cat)">
		  <subfield code="c">
		    <xsl:value-of select="normalize-space(./cat)"/>
		  </subfield>
		</xsl:if>
	      </datafield>
	      <datafield tag="035" ind1=" " ind2=" ">
		<subfield code="z">
		  <xsl:text>oai:arXiv.org:</xsl:text>
		  <xsl:choose>
		    <xsl:when test="contains(./bull, ':')">		
			<xsl:value-of select="normalize-space(substring-after(./bull,':'))"
				      />
		    </xsl:when>
		    <xsl:otherwise>
		      <xsl:value-of select="normalize-space(./bull)" />
		    </xsl:otherwise>
		  </xsl:choose>
		</subfield>
		<subfield code="9">arXiv</subfield>
	      </datafield>
	      <xsl:text>&#10;</xsl:text>	  
	    </xsl:if>
	  </xsl:for-each>


	  <xsl:if test="./report-cancel">
	    <datafield tag="980" ind1=" " ind2=" ">
	      <subfield code="c">DELETED</subfield>
	    </datafield>
	    <xsl:text>&#10;</xsl:text>	   
	  </xsl:if>

          <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./report-num" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">037</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./corp-author" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">710</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./col-note" />
	    <xsl:with-param name="code">g</xsl:with-param>
	    <xsl:with-param name="tag">710</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./title" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">245</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./jour-sub" />
	    <xsl:with-param name="code">p</xsl:with-param>
	    <xsl:with-param name="tag">773</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./language" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">041</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./p" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">300</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./note" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">500</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./experiment" />
	    <xsl:with-param name="code">e</xsl:with-param>
	    <xsl:with-param name="tag">693</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./desy-pub-note" />
	    <xsl:with-param name="code">x</xsl:with-param>
	    <xsl:with-param name="tag">773</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./desy-keywords" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">695</xsl:with-param>
	    <xsl:with-param name="sub2">2</xsl:with-param>
	    <xsl:with-param name="sub2_val">INSPIRE</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./desy-abs-num" />
	    <xsl:with-param name="code">z</xsl:with-param>
	    <xsl:with-param name="tag">035</xsl:with-param>
	    <xsl:with-param name="source">DESY</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./cernkey" />
	    <xsl:with-param name="code">z</xsl:with-param>
	    <xsl:with-param name="tag">035</xsl:with-param>
	    <xsl:with-param name="source">CERNKEY</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./title-variant" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">210</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./old-title" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">246</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./other-author" />
	    <xsl:with-param name="code">q</xsl:with-param>
	    <xsl:with-param name="tag">700</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./tt" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">246</xsl:with-param>
	    <xsl:with-param name="source">arXiv</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./archive-cat" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">650</xsl:with-param>
	    <xsl:with-param name="ind1">1</xsl:with-param>
	    <xsl:with-param name="ind1">7</xsl:with-param>
	    <xsl:with-param name="sub2">2</xsl:with-param>
	    <xsl:with-param name="sub2_val">arXiv</xsl:with-param>	    
	    <xsl:with-param name="source">arXiv</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./pacs" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">650</xsl:with-param>
	    <xsl:with-param name="ind1">1</xsl:with-param>
	    <xsl:with-param name="ind1">7</xsl:with-param>
	    <xsl:with-param name="sub2">2</xsl:with-param>
	    <xsl:with-param name="sub2_val">PACS</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./hidden-note" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">595</xsl:with-param>
	    <xsl:with-param name="source">SPIRES-HIDDEN</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./free-keywords" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">653</xsl:with-param>
	    <xsl:with-param name="ind1">1</xsl:with-param>
	    <xsl:with-param name="source">author</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./uniquetex" />
	    <xsl:with-param name="code">z</xsl:with-param>
	    <xsl:with-param name="tag">035</xsl:with-param>
	    <xsl:with-param name="source">SPIRESTeX</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./collection" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">980</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./topic" />
	    <xsl:with-param name="code">a</xsl:with-param>
	    <xsl:with-param name="tag">980</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./date" />
	    <xsl:with-param name="code">c</xsl:with-param>
	    <xsl:with-param name="tag">269</xsl:with-param>
	  </xsl:call-template>

	  <!--remove these two once ported to INSPIRE, then maintain this in the bibrec table-->

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./date-added" />
	    <xsl:with-param name="code">x</xsl:with-param>
	    <xsl:with-param name="tag">961</xsl:with-param>
	  </xsl:call-template>

	  <xsl:call-template name="basic-element">
	    <xsl:with-param name="select" select="./date-updated" />
	    <xsl:with-param name="code">c</xsl:with-param>
	    <xsl:with-param name="tag">961</xsl:with-param>
	  </xsl:call-template>

	</record>
      </xsl:for-each> 
    </collection>   
  </xsl:template>

  <xsl:template name="output-tokens">
    <xsl:param name="list"/>
    <xsl:param name="delimiter"/>
    <xsl:param name="code"/>
    <xsl:param name="source"/>
    <xsl:param name="tag"/>
    <xsl:param name="ind1"><xsl:text> </xsl:text></xsl:param>
    <xsl:param name="ind2"><xsl:text> </xsl:text></xsl:param>
    <xsl:param name="sub2"/>
    <xsl:param name="sub2_val" />
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


    <datafield>
      <xsl:attribute name = "tag">
	<xsl:value-of select="$tag"/>
      </xsl:attribute>
      <xsl:attribute name = "ind1">
	<xsl:value-of select="$ind1"/>
      </xsl:attribute>
      <xsl:attribute name = "ind2">
	<xsl:value-of select="$ind2"/>
      </xsl:attribute>
      <subfield>
	<xsl:attribute name = "code">
	  <xsl:value-of select="$code"/>
	</xsl:attribute>
	<xsl:value-of select="normalize-space($first)"/>
      </subfield>
      <xsl:if test="string($source)">
	<subfield code="9">
	  <xsl:value-of select="$source"/>
	</subfield>
      </xsl:if>
      <xsl:if test="string($sub2_val)">
	<subfield>
	    <xsl:attribute name = "code">
	      <xsl:value-of select="$sub2"/>
	    </xsl:attribute>
	    <xsl:value-of select="$sub2_val"/>
	</subfield>
      </xsl:if>
	
    </datafield>
    
    <xsl:if test="$remaining">
      <xsl:call-template name="output-tokens">
	<xsl:with-param name="list" select="$remaining"/>
	<xsl:with-param name="delimiter">
	  <xsl:value-of select="$delimiter"/>
	</xsl:with-param>
	<xsl:with-param name="code">
	  <xsl:value-of select="$code"/>
	</xsl:with-param>
	
	<xsl:with-param name="tag">
	  <xsl:value-of select="$tag"/>
	</xsl:with-param>
	<xsl:with-param name="ind1">
	  <xsl:value-of select="$ind1"/>
	</xsl:with-param>
	<xsl:with-param name="ind2">
	  <xsl:value-of select="$ind2"/>
	</xsl:with-param>
	<xsl:with-param name="sub2">
	  <xsl:value-of select="$sub2"/>
	</xsl:with-param>
	<xsl:with-param name="sub2_val">
	  <xsl:value-of select="$sub2_val"/>
	</xsl:with-param>

	<xsl:with-param name="source">
	  <xsl:value-of select="$source"/>
	</xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
  


  <xsl:template name="parse-cpn">
    <xsl:param name="cpn"/>
    <xsl:param name="type"/>
    <xsl:variable name = "tmpcpn"  select="normalize-space(substring-after(substring-after($cpn,'*'),'*'))" />
    
    <xsl:choose>
      <xsl:when test = "string-length($tmpcpn)>0">
	<xsl:choose>
          <xsl:when test= "$type = 'all'">
	    
            <subfield code="c">
	      <xsl:value-of select="$tmpcpn"/>
	    </subfield>
            <subfield code="x">
              <xsl:value-of select="$cpn"/> 
            </subfield>
            <subfield code="y">
	    </subfield>
	    
          </xsl:when>
          <xsl:otherwise> 
            <subfield code="c">
	      <xsl:value-of select="$tmpcpn"/>
	    </subfield>
          </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name = "plain-cpn">
          <xsl:with-param name="cpn">
            <xsl:value-of select="$cpn"/>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template name="plain-cpn">
    <xsl:param name="cpn"/>
    <subfield code = "x">
      <xsl:value-of select = "$cpn" />
    </subfield>
  </xsl:template>



  <xsl:template name="basic-element">
    <xsl:param name = "select"/>
    <xsl:param name = "tag"/>
    <xsl:param name = "ind1"><xsl:text> </xsl:text></xsl:param>
    <xsl:param name = "ind2"><xsl:text> </xsl:text></xsl:param>
    <xsl:param name = "subfield"/>
    <xsl:param name = "source" />
    <xsl:param name = "sub2"/>
    <xsl:param name = "sub2_val" />
    <xsl:for-each select="$select">
      <!--do not print tags for empty values-->
      <xsl:if test="string(.)">
	<datafield>
	  <xsl:attribute name = "tag">
	    <xsl:value-of select="$tag"/>
	  </xsl:attribute>
	  <xsl:attribute name = "ind1">
	    <xsl:value-of select="$ind1"/>
	  </xsl:attribute>
	  <xsl:attribute name = "ind2">
	    <xsl:value-of select="$ind2"/>
	  </xsl:attribute>
	  <subfield>
	    <xsl:attribute name = "code">
	      <xsl:value-of select="$code"/>
	    </xsl:attribute>
	    <xsl:value-of select="normalize-space(.)"/>
	  </subfield>
	  <xsl:if test="string($source)">
	    <subfield code="9">
	      <xsl:value-of select="$source"/>
	    </subfield>
	  </xsl:if>
	  <xsl:if test="string($sub2_val)">
	    <subfield>
	      <xsl:attribute name = "code">
		<xsl:value-of select="$sub2"/>
	      </xsl:attribute>
	      <xsl:value-of select="$sub2_val"/>
	    </subfield>
	  </xsl:if>
	</datafield>
      </xsl:if>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>


</xsl:stylesheet>
