# import urllib.request, urllib.parse - urllib does not seem to work with data.gov api
import json, ssl
import datetime
import requests
import pprint #to print test APIs
import sqlite3
import codecs #to write to where.js

#NEA API for windspeed URL
neaUrl1 = 'https://api-open.data.gov.sg/v2/real-time/api/wind-speed?'


#extracts current time as local time for NEA query. Assumes local time is same as Singapore time
currentTime = datetime.datetime.now()
#test print current time and NEA url
print('Current time:', currentTime)
print('Current url:', neaUrl1)

#converts current time (a datetime object) as local time to a string for URL query
queryTime = currentTime.strftime('%Y-%m-%dT%H:%M:%S')
print('Query time:', queryTime)

#constructs the URL for the query
url = neaUrl1 + 'date=' + queryTime
print('Retrieving', url)

#opens the URL and reads the data. API data is stored as a dictionary
response = requests.get(url)
data = response.json()

#test print data from API
pprint.pp(data)

#somehow urlopen does not work with data.gov api, not sure why, is it to avoid being blocked while scraping?
#encodes the parameters for the URL query
#parms = dict()
#parms['date'] = queryTime
#url = neaUrl + urllib.parse.urlencode(parms)
#urlHandler = urllib.request.urlopen(url)
#data = urlHandler.read().decode()

conn = sqlite3.connect('nea-wind-speed.sqlite')
cur = conn.cursor()

script1 = '''
DROP TABLE IF EXISTS Station;
DROP TABLE IF EXISTS Reading;
DROP TABLE IF EXISTS Timestamp;

CREATE TABLE Station (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    nea_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    name TEXT NOT NULL UNIQUE,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

CREATE TABLE Timestamp (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    timestamp TEXT NOT NULL UNIQUE
);

CREATE TABLE Reading (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    station_id INTEGER NOT NULL,
    timestamp_id INTEGER NOT NULL,
    wind_speed FLOAT NOT NULL
);
'''

cur.executescript(script1)

#extract timestamp from data
for element in data['data']['readings']:
    timeStamp = element['timestamp']
    print('Timestamp:', timeStamp)
    #save timestamp into SQL database
    cur.execute('INSERT OR IGNORE INTO Timestamp (timestamp) VALUES (?)', (timeStamp,))
    conn.commit()

#test to check that timestamp is saved correctly
#cur.execute('SELECT * FROM Timestamp')
#print(cur.fetchall())

#extract stations from data
for element in data['data']['stations']:
    stationId = element['id']
    deviceId = element['deviceId']
    name = element['name']
    latitude = element['location']['latitude']
    longitude = element['location']['longitude']
    #save station into SQL database
    cur.execute('''INSERT OR IGNORE INTO Station (nea_id, device_id, name, latitude, longitude)
    VALUES (?, ?, ?, ?, ?)''', (stationId, deviceId, name, latitude, longitude))
    conn.commit()
    #test that stations are processed
    print('Station:', stationId, deviceId, name, latitude, longitude)

#checks if stations are saved correctly into database
#cur.execute('SELECT * FROM Station')
#for row in cur.fetchall():
    #print(row)

  
#extract readings from data
#extract timestamp ID from database, this assumes that the python script runs for only one timestamp
cur.execute('SELECT id FROM Timestamp WHERE timestamp = ?', (timeStamp,))
timeStampId = cur.fetchone()[0]

#Test for timeStampID
print('Timestamp ID:', timeStampId)

#for some reason data['data']['readings'][0]['data'] is needed to 
#access the readings even though we could access the timestamp directly previously
#pprint.pp(data['data']['readings'][0]['data'])

for element in data['data']['readings'][0]['data']:
    #extract wind speed and station ID from data
    windSpeed = element['value']
    stationId = cur.execute('SELECT id FROM Station WHERE nea_id = ?', (element['stationId'],)).fetchone()[0]
    #test print for stationId and windSpeed are extracted correctly
    #print(stationId, windSpeed)
    #save reading into SQL database
    cur.execute('''INSERT OR IGNORE INTO Reading (station_id, timestamp_id, wind_speed)
    VALUES (?, ?, ?)''', (stationId,timeStampId, windSpeed))
    conn.commit()

#test that readings are saved correctly into database
#cur.execute('SELECT * FROM Reading')
#for row in cur.fetchall():
    #print(row)

#prepare to write to where.js and writes opening line
fhand = codecs.open('where.js', 'w', "utf-8")
fhand.write("myData = [\n")

#excute SQL query to extract data for where.js
#there is no need to join timestamp for now as this script only runs for one timestamp.
#Timestamp is kept as a potential future feature
cur.execute('''SELECT name, latitude, longitude, wind_speed
FROM Reading JOIN Station
ON Reading.station_id=station.id 
''')

count = 0

#start to get individual row data
for row in cur:
    name = row[0]
    latitude = row[1]
    longitude = row[2]
    windSpeed = row[3]
    #test print for individual row data
    print(name, latitude, longitude, windSpeed)

    #write to where.js
    count = count + 1
    if count > 1 :
        fhand.write(",\n")
    output = "["+str(latitude) + "," + str(longitude) + ", " + "'Station: " + name + " Wind Speed: " + str(windSpeed) + " knots']"
    fhand.write(output)
    #test print for output
    print(output)

#write closing line for where.js
fhand.write("\n];\n")
cur.close()
conn.close()
fhand.close()

print(count, "records written to where.js")
print("Open where.html to view the data in a browser")














