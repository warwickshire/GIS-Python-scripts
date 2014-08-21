#Created by: Jonathan Moules; Warwickshire County Council
#Date: 2013-11-07
#License: CC BY 3.0 (Creative Commons Attribution 3.0 Unported)

#Version: 1.2
#	Gets Server name
#	Regexp Compilation optimisation
#Version: 1.1
#	Sorts alphabetically
#	Option to ignore layers
#Version: 1.0
#	Initial version.


#How to use:
#	Configure the below variables and save.
#	Then run it.


#Location of file this script creates
output_file = "//wcc-corp.ad/BuData/MSSystems/Cad\GIS_DATA/YY Direct Data Connections/Google Earth/All_Compass_Layers.kml";

#The root URL for WMS Server - no trailing slash
url_geoserver = 'http://compass/geoserver';

#Suffix of URL that will get the GetCapabilities. Works with 1.3.0; other versions untested.
url_to_wms_getcaps = url_geoserver + '/ows?service=wms&version=1.3.0&request=GetCapabilities';

#Suffix of URL for the network link. Probably don't need to change.
url_network_link = url_geoserver + '/wms/kml?layers=';

#List of layers that won't be included in the output KML.
#I.e. you probably don't want to include layer groups because they appear wrongly in Google Earth.
#Also don't really need them - that's what Google Earth is for after all.
ignore_layers_list = ['OS_Strategi_Group','OS_VMD_Group','OS_VML_Group','OS_Meridian_Group','OS_MasterMap_Group_VML_Style','Conwy_MasterMap','z_OS_Raster_Basemap','z_OS_Vector_Basemap'];


#####################
# END CONFIGURATION #
#####################

import re;
import urllib2;
import sys;


#open connection to URL
get_caps = urllib2.urlopen(url_to_wms_getcaps);

#Failure
if (get_caps.code >=400):
	sys.exit();

wms_getcaps = get_caps.read();

#clean up after ourselves.
get_caps.close();

wms_title_regexp = re.compile(".*<Service.*?<Title>(.*?)<\/Title>", re.DOTALL);
wms_title = wms_title_regexp.match(wms_getcaps);



output = ''; #output string


output += '<?xml version="1.0" encoding="UTF-8"?>';
output += '\n<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">';
output += '\n<Folder>';
output += '\n	<name>'+ wms_title.group(1) + '</name>';
output += '\n	<open>1</open>';


#Gets all of the layer declarations as a list of separate entities
#Stops at the first instance of "Title", so we don't get attribution & style names/titles
layers_regexp = re.compile("\s*<Layer queryable=.*?<\/Title>", re.DOTALL);

name_regexp = re.compile(".*<Name>(.*?)<\/Name>", re.DOTALL | re.MULTILINE);

title_regexp = re.compile(".*<Title>(.*?)<\/Title>", re.DOTALL | re.MULTILINE);

all_layers_list = [];


i=0;
for this_result in layers_regexp.findall(wms_getcaps):
	#Get the Layer name
	this_res = name_regexp.match(this_result);
	layer_name = this_res.group(1);

	#skip if it's in the list of things to ignore
	if(layer_name in ignore_layers_list):
		continue;

	#The title is "human readable", but Google Earth calls this the "name".
	this_res = title_regexp.match(this_result);
	layer_title = this_res.group(1);

	all_layers_list.append("");
	all_layers_list[i] = [layer_name, layer_title];

	i+=1;

#function for sorting alphabetically by the "Title" of a layer.
def miniSort( a ):
    return a[1]

all_layers_list.sort( key=miniSort )

#use the sorted list
for this_result in all_layers_list:

	#print layer_name + layer_title;

	output +='\n	<NetworkLink>';
	output +='\n		<name>' + this_result[1] + '</name>';
	output +='\n		<visibility>0</visibility>';
	output +='\n		<Link>';
	output +='\n		<href>' + url_network_link + this_result[0] + '</href>';
	output +='\n		</Link>';
	output +='\n	</NetworkLink>';



#end KML file
output += '\n</Folder>';
output += '\n</kml>';

#write to output file
output_file = open(output_file, "w");
print>>output_file, output;
output_file.close()

#print output;
