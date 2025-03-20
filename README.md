This project is based on the OPENGEO example in the py4e course at www.py4e.com
used under Copyright Creative Commons Attribution 3.0 - Charles R. Severance.

The query.py script extracts Singapore National Environmental Agency data for 
the current average wind speed from the last ten minutes in knots from the Data.Gov API
at the following address:
https://api-open.data.gov.sg/v2/real-time/api/wind-speed

The script then reads the data and saves the weather station and wind speed readings data
to a database, nea-wind-speed.sqlite.

The script then outputs the data to a json file, where.js.
The where.js format is largely unchanged from Dr Chuck's exmaple version.

The script stops running when the data is written to the where.js file.
The user can load the where.html file to view the visualisation of the NEA stations and windspeed.
You would have navigate the map in the html file and zoom into Singapore to see the weather stations.
The where.html file is unchanged from Dr Chuck's version until I sharpen my HTML skills.
