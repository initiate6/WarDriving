import xml.etree.ElementTree as ET
from lxml import etree
import re
import json
from datetime import datetime as dt
import traceback
import operator
import csv

probe = 0
infrastructure = 0
adhoc = 0

p_bssid = []
i_bssid = []
a_bssid = []
essid = []

data = {}

date_pattern = "%a %b %d %H:%M:%S %Y"

file_list = ['1.xml', '2.xml', '3.xml']
#file_list = ['2.xml']

parser = etree.XMLParser(recover=True)

for x in file_list:
	tree = etree.parse(x, parser=parser)
	root = tree.getroot()

	for child in root:
		#print(child.attrib)
		try:
			number = child.attrib['number']
			wtype = child.attrib['type']
			ftime = (dt.strptime(child.attrib['first-time'], date_pattern) - dt(1970,1,1)).total_seconds()
			ltime = (dt.strptime(child.attrib['last-time'], date_pattern) - dt(1970,1,1)).total_seconds()
			bssid = child.find('BSSID').text
			channel = child.find('channel').text

			gps_info = child.find('gps-info')
			if gps_info:
				avg_lat = gps_info.find('avg-lat').text
				avg_lon = gps_info.find('avg-lon').text
				avg_alt = gps_info.find('avg-alt').text
			else:
				avg_lat = None
				avg_lon = None
				avg_alt = None



			if wtype == 'infrastructure':
				encrypt_type = None
				wpa_version = None
				encrypt_details = None
				points = None
				essid = None
				wps = None
				cloaked = None

				SSID = child.find('SSID')
				if SSID:
					encrypt_details = []
					wpa_version = ''
					encrypt_type = SSID.find('encryption').text

					wps = SSID.find('wps').text

					if encrypt_type == 'WEP':
						points = 50
						encrypt_type = 'wep'

					elif 'WPA' in encrypt_type:

						for x in SSID.findall('encryption'):
							encrypt_details.append(x.text)

						wpa_version = SSID.find('wpa-version').text

						if 'WPA2' in wpa_version:
							encrypt_type = 'wpa2'
							points = 1

						else:
							encrypt_type = 'wpa'
							points = 5

					else:
						encrypt_type = 'open'
						points = 10

					if SSID.find('essid').text:
						essid = SSID.find('essid').text

					else:
						essid = ''

					if SSID.find('essid').get('cloaked') == 'false':
						cloaked = False
					else:
						cloaked = True
				#if not points:
					#print(ET.dump(child))

			elif wtype == 'probe':
				ssid = []
				wireless_client = child.findall('wireless-client')
				for client in wireless_client:
					#ssid.append(s.text)
					if client.findall('SSID'):
						SSID = client.findall('SSID')
						for s in SSID:
							s_text = s.find('ssid').text
							if s_text != '':
								ssid.append(s_text)

			elif wtype == 'ad-hoc':
				#print(ET.dump(child))
				carrier = None
				encoding = None
				if child.find('carrier'):
					carrier = child.find('carrier').text
				if child.find('encoding'):
					encoding = child.find('encoding').text

			elif wtype == 'data':
				#if wtype != 'infrastructure' or wtype != 'probe' or wtype != 'ad-hoc' or wtype != 'data':
					#print(ET.dump(child))
				pass
			else:
				pass
				#print(ET.dump(child))


			if wtype == 'infrastructure':
				key = 'i:%s:%s:%s' % (bssid, essid, encrypt_type)
				data[key] = {'network_type': wtype, 'bssid': bssid, 'number': number, 'first-time': ftime, 'last-time': ltime,
							 'channel': channel, 'gps_lat': avg_lat, 'gps_lon': avg_lon, 'gps_alt': avg_alt, 'encrypt_type': encrypt_type,
							 'wpa_version': wpa_version, 'encrypt_details': encrypt_details, 'points': points, 'essid': essid,
							 'wps': wps, 'cloaked': cloaked}

			elif wtype == 'probe':
				key = 'p:%s' % (bssid)
				data[key] = {'network_type': wtype, 'bssid': bssid, 'number': number, 'first-time': ftime, 'last-time': ltime,
							 'channel': channel, 'gps_lat': avg_lat, 'gps_lon': avg_lon, 'gps_alt': avg_alt, 'SSID_PROBE_REQUEST': ssid
							}

			elif wtype == 'ad-hoc':
				key = 'a:%s' % (bssid)
				data[key] = {'network_type': wtype, 'bssid': bssid, 'number': number, 'first-time': ftime, 'last-time': ltime,
							 'channel': channel, 'gps_lat': avg_lat, 'gps_lon': avg_lon, 'gps_alt': avg_alt, 'carrier': carrier,
							 'encoding': encoding}

			else:
				pass




		except Exception as e:
			#print('Error: %s' % e)
			#traceback.print_exc()
			pass


'''
def sort(list_obj):
	final = []
	list_obj.sort()
	temp = ""

	for item in list_obj:
		if item != temp:
			final.append(item)
			temp = item

	return final

def write(list_obj, name):

	with open(name, 'w') as f:
		f.writelines(list_obj)


pb = sort(p_bssid)
ib = sort(i_bssid)
ab = sort(a_bssid)

print('Probe Count: %s, BSSID Count: %s, Unique BSSID: %s' % (probe, len(p_bssid), len(pb)) )

print('Infrastructure Count: %s, BSSID Count: %s, Unique BSSID: %s' % (infrastructure, len(i_bssid), len(ib)) )

print('adhoc Count: %s, BSSID Count: %s, Unique BSSID: %s' % (adhoc, len(a_bssid), len(ab)) )


es = sort(essid)
filter_essid = []

def search(s):
	filter_list = [re.compile(r'^[aA][tT][tT]'), re.compile(r'^[cC]hromecast'), re.compile(r'^belkin'),
			re.compile(r'[gG]alaxy.*[\d]'), re.compile(r'^(NETGEAR|netgear)'), re.compile(r'roku'),
			re.compile(r'([cC]harter|[sS]pectrum|FiOS|[cC]isco_|HP|Print|PS4-|TWC)'), re.compile(r'^[dDtT][cCdDgGvV]([wW]|[\d])'),
			re.compile(r'^Zoo'), re.compile(r'^Zoya'), re.compile(r'^Zubrod'), re.compile(r'^Zero'), re.compile(r'Z[abe][vin]'),
			re.compile(r'^tl([\d]|a|b)'), re.compile(r'^ngHub'), re.compile(r'^island-'),
			re.compile(r'^e46'), re.compile(r'^dlink'), re.compile(r'^2WIRE'),
			re.compile(r'^WiFi Hotspot [\d]+'), re.compile(r'^WIFI[a-fA-F0-9]'), re.compile(r'^[vV]erizon'),
			re.compile(r'^U10'), re.compile(r'^Time[\s]*[wW]arner([\s]*[\d]+|)'), re.compile(r'^(TREND|TP-LINK)'),
			re.compile(r'^(T-Mobile|SYNC_|SBG6|NewThermostat|NTGR_|MotoVAP|MOTOROLA|Linksys[0-9_]|LEDnet|K7[\s]|Home[ _0-9NW-])'),
			re.compile(r'^(HT_|HTC |DIRECT[-V]|CellSpot_|CG3|Belkin[\._]|ALCATEL |3c1e)')
			]
	for pattern in filter_list:
		if re.search(pattern, s):
			return False
		else:
			pass
	return True


for s in es:
	if len(s) > 5:
		if search(s):
			#print(s)
			filter_essid.append(s)


print('SSID Count: %s, Unique SSID: %s, Filter Count: %s' % (len(essid), len(es), len(filter_essid) ) )
'''

total_pts = 0
total_open = 0
total_wep = 0
total_wpa = 0
total_wpa2 = 0
probe_count = 0
infrastructure_count = 0
adhoc_count = 0

channel_dict = {'c0': 0, 'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0, 'c5': 0, 'c6': 0,
				'c7': 0, 'c8': 0, 'c9': 0, 'c10': 0, 'c11': 0, 'c12': 0,
				'c161': 0, 'c48': 0, 'c40': 0, 'c52': 0, 'c44': 0, 'c157': 0,
				'c5660': 0, 'c56': 0, 'c116': 0, 'c108': 0, 'c104': 0, 'c36': 0,
				'c112': 0, 'c153': 0, 'c64': 0, 'c132': 0, 'c149': 0, 'c136': 0,
				'c100': 0, 'c165': 0, 'c60': 0, 'c140': 0, 'c35': 0, 'c5560': 0,
				'c5500': 0, 'c5540': 0, 'c37': 0, 'c5700': 0, 'c13': 0, 'c39': 0}

ichannel_dict = {'c0': 0, 'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0, 'c5': 0, 'c6': 0,
				'c7': 0, 'c8': 0, 'c9': 0, 'c10': 0, 'c11': 0, 'c12': 0,
				'c161': 0, 'c48': 0, 'c40': 0, 'c52': 0, 'c44': 0, 'c157': 0,
				'c5660': 0, 'c56': 0, 'c116': 0, 'c108': 0, 'c104': 0, 'c36': 0,
				'c112': 0, 'c153': 0, 'c64': 0, 'c132': 0, 'c149': 0, 'c136': 0,
				'c100': 0, 'c165': 0, 'c60': 0, 'c140': 0, 'c35': 0, 'c5560': 0,
				'c5500': 0, 'c5540': 0, 'c37': 0, 'c5700': 0, 'c13': 0, 'c39': 0}

c_other = []
encrypt_details_list = []

encrypt_details_dict = {'WPA+PSK': 0, 'WPA+AES-CCM': 0, 'WPA+TKIP': 0, 'WPA Migration Mode': 0, 'WEP40': 0, 'WEP104': 0}

cloaked_count = 0
not_cloaked = 0
wps_count = 0

probe_ssid_count = 0
probe_ssid_list = []

gps_dict = {}

with open('wardriving.csv', 'wb') as warfile:
	fieldnames = ['first-time', 'network_type', 'bssid', 'encrypt_type', 'encrypt_details', 'wpa_version', 'wps', 'gps_lat', 'gps_lon', 'gps_alt', 'points', 'cloaked', 'essid', 'channel', 'SSID_PROBE_REQUEST']
	writer = csv.DictWriter(warfile, fieldnames=fieldnames, restval='', extrasaction='ignore', dialect='excel')

	writer.writeheader()
	for k,v in data.iteritems():
		writer.writerow(v)



#print(len(list(data.keys())))
for k,v in data.iteritems():
	for x,y in v.iteritems():
		if x == 'first-time' and y:
			try:
				et = v['encrypt_type']
			except:
				et = v['network_type']

			if v['gps_lat']:
				gps_dict[y] = (v['gps_lat'], v['gps_lon'], v['gps_alt'], k, et )


		if x == 'points' and y:
			total_pts += y
		if x == 'encrypt_type' and y == 'open':
			total_open += 1
		if x == 'encrypt_type' and y == 'wep':
			total_wep += 1
		if x == 'encrypt_type' and y == 'wpa':
			total_wpa += 1
		if x == 'encrypt_type' and y == 'wpa2':
			total_wpa2 += 1
		if x == 'channel' and y:
			ch = 'c%s' %y
			if ch in channel_dict.keys():
				channel_dict[ch] += 1
				if k[0] == 'i':
					ichannel_dict[ch] += 1
			else:
				if ch not in c_other:
					c_other.append(ch)
		if x == 'network_type' and y:
			if y == 'probe':
				probe_count += 1
			if y == 'infrastructure':
				infrastructure_count += 1
			if y == 'ad-hoc':
				adhoc_count += 1
		if x == 'encrypt_details' and y:
			for ed in y:
				if ed in encrypt_details_dict.keys():
					encrypt_details_dict[ed] += 1

				else:
					if ed not in encrypt_details_list:
						encrypt_details_list.append(ed)
		if x == 'cloaked' and k[0] == 'i':
			if y:
				cloaked_count += 1
			else:
				not_cloaked += 1

		if x == 'wps' and y:
			if y == 'Configured':
				wps_count += 1

		if x == 'SSID_PROBE_REQUEST':
			for z in y:
				probe_ssid_count += 1
				probe_ssid_list.append(z)






print('Total Points: %s' % (total_pts))
print("Encryption Type Totals: Open: %s, WEP: %s, WPA: %s, WPA2: %s" % (total_open, total_wep, total_wpa, total_wpa2) )
print("Network Type Totals: Infrastructure: %s, Probe: %s, ad-hoc: %s" % (infrastructure_count, probe_count, adhoc_count) )
print("AP with Hidden SSID: %s" % (cloaked_count))
print("AP with SSID: %s" % (not_cloaked))
print("AP with WPS Configured: %s" % (wps_count))


print("\nChannels by count\n")
sorted_channel_list = sorted(channel_dict.items(), key=operator.itemgetter(1), reverse=True)
for c, count in sorted_channel_list:
	print("Channel: %s, Count: %s" % (c, count) )

print("\n(Infrastructure Only) Channels by count\n")
isorted_channel_list = sorted(ichannel_dict.items(), key=operator.itemgetter(1), reverse=True)
for ic, icount in isorted_channel_list:
	print("Channel: %s, Count: %s" % (ic, icount) )

print("\nAP Supported Encryption Algorithms by count\n")
sorted_encrypt_details = sorted(encrypt_details_dict.items(), key=operator.itemgetter(1), reverse=True)
for alg, count in sorted_encrypt_details:
	print("Encryption Algorithm: %s, Count: %s" % (alg, count) )


#print("Probe Request count: %s" % (probe_ssid_count))
#for s in probe_ssid_list:
#	print(s)


#print(gps_dict)

sorted_gps_dict = sorted(gps_dict.items(), key=operator.itemgetter(0) )

with open('gps.csv', 'wb') as csvfile:
	csvwriter = csv.writer(csvfile)
	for time, info in sorted_gps_dict:
		csvwriter.writerow([time, info[0], info[1], info[2], info[3], info[4] ])
