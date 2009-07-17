<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output indent="no" method="html" encoding="ISO-8859-1" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
              doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" omit-xml-declaration="yes" version="1.0"/>

  <xsl:template match="/">
    <html>
      <head>
        <style>
          .cap {
            display: none;
          }
        </style>
        <script language="JavaScript" src="allocation.js"/>
        <title>RIR - Network Graph</title>
      </head>
      <body>
	<center><h2><xsl:value-of select="/prefixes/@range"/></h2></center>
        <xsl:for-each select="/prefixes/error">
          <li><b class="color:red"><xsl:value-of select="text()"/></b></li>
        </xsl:for-each>
        <embed src="{/prefixes/@svg}" width="{/prefixes/@width}" height="{/prefixes/@height}" usemap="#map" type="image/svg+xml" pluginspage="http://www.adobe.com/svg/viewer/install/" />
        <map name="map">
          <xsl:for-each select="/prefixes/prefix">
            <area shape="rect" coords="{@xl},{@yl},{@xr},{@yr}" title="[{@netname}] {description/text()}"
             onMouseOver="showPrefix(this, 'a{@id}')"
             onMouseOut="hidePrefix()"
             onClick="showPrefixAlert(this, 'a{@id}')"
          />
          </xsl:for-each>
        </map>
        <div id="loc"/>
        <br/><br/><br/><br/><br/><br/><br/><br/><br/>
        <xsl:for-each select="/prefixes/prefix">
          <div class="cap" id="a{@id}">
            <h3><xsl:value-of select="@netname"/></h3>
            <xsl:for-each select="description">
              <b><xsl:value-of select="text()"/></b><br/>
            </xsl:for-each>
            <p><xsl:value-of select="@start"/> - <xsl:value-of select="@end"/></p>
          </div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>

