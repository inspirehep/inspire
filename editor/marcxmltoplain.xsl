<?xml version='1.0' encoding='UTF-8'?>
<!--
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option) any
later version.
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

<xsl:output method="text" encoding="utf-8"/>

<xsl:template match="/">
  <xsl:for-each select="/record">
    <!--get controlfield and its tag. no ids-->
    <xsl:for-each select="controlfield">
      <xsl:text>controlfield</xsl:text>
      <xsl:value-of select="@tag"/>
      <xsl:text>:</xsl:text>
      <xsl:value-of select="."/>
<xsl:text>
</xsl:text>
   </xsl:for-each>
    <!--get datafield and its tag and ids-->
    <xsl:for-each select="datafield">
	<xsl:for-each select="subfield"> <!--a datafield can have multiple subfields-->
	      <!--print everything-->
              <!-- <xsl:text>datafield</xsl:text> -->
	      <xsl:value-of select="../@tag"/> <!--datafield tage value-->
	      <xsl:choose> <!--datafield ind values or _-->
	      <xsl:when test="../@ind1=' '">
		<xsl:text>_</xsl:text>	
     	      </xsl:when>
              <xsl:otherwise>
	      <xsl:value-of select="../@ind1"/>
              </xsl:otherwise>
	      </xsl:choose>

	      <xsl:choose>
	      <xsl:when test="../@ind2=' '">
		<xsl:text>_</xsl:text>	
	      </xsl:when>
	      <xsl:otherwise>
	        <xsl:value-of select="../@ind2"/>
	      </xsl:otherwise>
	      </xsl:choose>

	      <xsl:value-of select="@code"/>
         	<xsl:text>:</xsl:text>	
	      <xsl:value-of select="."/> <!--print the content of subfield-->
<xsl:text>
</xsl:text>	
	</xsl:for-each>
   </xsl:for-each>


  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
