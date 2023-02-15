<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


<xsl:template match="/">
<xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'"/>
<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
<html>
  <body>

<h2> Test Case Execution Report</h2>

<hr/>
<h3 style="color: #34307a;"> Test Run Information</h3>
<ul style="font-family: Arial; font-size: 14px;">
	<li>Env: <xsl:value-of select="TestRunning/Info/TestEnvironment"/></li>
	<!-- <li>Website: <xsl:value-of select="TestRunning/Info/TestWebstie"/></li> -->
	<!-- <li>Account: <xsl:value-of select="TestRunning/Info/TestAccount"/></li> -->
	<li>Start: <xsl:value-of select="TestRunning/Info/TestRunDuration/@StartTime"/></li>
	<li>End  : <xsl:value-of select="TestRunning/Info/TestRunDuration/@EndTime"/></li>
	<li>Run time: <xsl:value-of select="TestRunning/Info/TestRunDuration"/></li>
    <li>Total Case: <xsl:value-of select="TestRunning/Info/ExecutionCaseCount/@AllCase"/> (PASS: <font color="green"><xsl:value-of select="TestRunning/Info/ExecutionCaseCount/CountPASS"/></font>, FAIL: <font color="red"><xsl:value-of select="TestRunning/Info/ExecutionCaseCount/CountFAIL"/></font>)</li>
    <li>TestRail Report: <xsl:value-of select="TestRunning/Info/TestRail"/></li>
</ul>

<hr/>
<h3 style="color: #34307a;"> Game Providers</h3>
<ul style="font-family: Arial; font-size: 14px;">
	<xsl:for-each select="TestRunning/GameProvider/*">
		<li><xsl:value-of select="name(.)"/>: <xsl:value-of select="."/></li>
	</xsl:for-each>
	<li>Game Providers with Game: <xsl:value-of select="TestRunning/GameProviderStatus/GameOpen"/></li>
	<li>Game Providers without Game: <xsl:value-of select="TestRunning/GameProviderStatus/GameClose"/></li>
</ul>

<hr/>
<h3 style="color: #34307a;"> Test Results</h3>

<xsl:for-each select="TestRunning/TestResults/TestFeature">
<p>* Feature: <b><xsl:value-of select="@Folder"/></b> </p>

<table border = "1" bordercolor= "#e5e1da" style="font-family: Arial; border-color:#efefef; padding:0px ">
    
	<tr bgcolor= "#ffeece" style="color: #2b2a28; font-size: 13px; ">
		<th width="100" style="border-color:#efefef; padding:1px " >TestRail CaseID</th>
		<th width="200" style="border-color:#efefef; padding:1px " >Test Case</th>
        <th width="450" style="border-color:#efefef; padding:1px " >Title</th>  
        <th width="100" style="border-color:#efefef; padding:1px " >Test Result</th>
        <!-- <th width="120" style="border-color:#efefef; padding:1px " >Note</th> -->
        <th width="150" style="border-color:#efefef; padding:1px " >Execution Time</th>  
	</tr>
	<xsl:for-each select="TestCase">
        <tr style="color: #2b2a28; font-size: 12px;">
				<td style="border-color:#efefef; padding:1px " ><xsl:value-of select="@TestCaseID"/></td>
				<td style="border-color:#efefef; padding:1px " ><xsl:value-of select="@File"/></td>
                <td style="border-color:#efefef; padding:1px " ><xsl:value-of select="@Title"/></td>
				
				<xsl:if test="@Result = 'FAIL'">
                       <td align="center" style="border-color:#efefef; padding:1px "><font color="red"><xsl:value-of select="@Result"/></font></td>
				</xsl:if>
                <xsl:if test="@Result = 'PASS'">	
				    <td align="center" style="border-color:#efefef; padding:1px "><font color="green"><xsl:value-of select="@Result"/></font></td>
				</xsl:if>
                
                <!-- <td style="border-color:#efefef; padding:1px " ><xsl:value-of select="CaseNote"/></td> -->
                <td style="border-color:#efefef; padding:1px " ><xsl:value-of select="ExecutionTime"/></td>  
		</tr>
    </xsl:for-each>
	
</table>
<br/><br/>
</xsl:for-each>

</body>
</html>



</xsl:template>
</xsl:stylesheet>