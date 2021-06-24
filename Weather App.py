import requests
import csv
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

# List of all cities we are checking the weather for
cities = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow', 'Southampton',
          'Liverpool', 'Leicester', 'Nottingham', 'Sheffield', 'Bristol', 'Belfast']
# Container for initial XML with all the data
forecast = []
# Containers for categorising cities by weather
raining = []
snowing = []
icing = []
sunny = []
# Tomorrow date for saving the final XML file
tomorrow = 'no_date'


# This function will iterate over the list of cities watched, request a forecast in XML format and add it to
# the list of forecasts for every city, indexes will match ones in 'cities' list
def downloadWeatherData():
    for city in cities:
        response = requests.get("https://api.openweathermap.org/data/2.5/forecast?q=" + city +
                                "&appid=11fdafc9ed4c0d8d9d13bf9ce71eabf4"
                                "&mode=xml"
                                "&units=metric")
        if response.status_code == 200:
            xml_data = response.text
            root = ET.fromstring(xml_data)
            forecast.append(root)
        else:
            print('Something went wrong, error: ' + str(response.status_code))


# This function will create four containers to store weather properties for each day at a time, to later create
# a CSV file formatted as shown in the assignment briefing. All containers have matching indexes, which makes it
# easier to later create almost a whole CSV file in one for loop. Also, here is where tomorrow variable is set,
# it was the simplest way to extract tomorrows date without writing extra bits of code.
def extractToCSV():
    global tomorrow
    for city in forecast:
        date = []
        time = []
        temp = []
        status = []
        for tag in city.findall('forecast/time'):
            h_value = tag.get('from')
            date.append(h_value[0:10])
            time.append(h_value[11:19])
        for tag in city.findall('forecast/time/temperature'):
            h_value = tag.get('value')
            temp.append(h_value)
        for tag in city.findall('forecast/time/symbol'):
            h_value = tag.get('name')
            status.append(h_value)

        with open(cities[forecast.index(city)] + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date&Time', 'Main Weather Condition', 'Temperature'])
            for prediction in date:
                writer.writerow([prediction + ' ' + time[date.index(prediction)],
                                 status[date.index(prediction)], temp[date.index(prediction)]])
        tomorrow = date[9]


# This function will extract the sensible information from the XML files of all the cities one by one, categorizing
# them with four if statements. The 'i' variable is there to count number of times sub-zero temperatures
# will occur(2 times is equivalent to 6 hours), to then decide if it is icy outside. Cities are sorted
# by simply appending them to the right container
def categorizeCities():
    for city in forecast:

        weather = []
        temp = []
        badWeather = False

        for tag in city.findall('forecast/time/symbol'):
            h_value = tag.get('name')
            weather.append(h_value)
        for tag in city.findall('forecast/time/temperature'):
            h_value = tag.get('value')
            temp.append(h_value)

        i = 0
        for w in weather[8:16]:
            if w == "snow":
                snowing.append(cities[forecast.index(city)])
                badWeather = True
            if float(temp[weather.index(w)]) < 0:
                i += 1
        if i >= 2:
            icing.append(cities[forecast.index(city)])
            badWeather = True

        for w in weather[10:15]:
            if w == "rain":
                raining.append(cities[forecast.index(city)])
                badWeather = True

        if not badWeather:
            sunny.append(cities[forecast.index(city)])


# Cities sorted by category can now be displayed for the user to see
def printWeatherForecast():
    if len(sunny) > 0:
        print('Enjoy the weather if you are living in these cities:')
        for i in sunny:
            print(i)
        print('\n')

    if len(raining) > 0:
        print('Bring your ambrella if you live in these cities:')
        for i in raining:
            print(i)
        print('\n')

    if len(icing) > 0:
        print('Mind your step if you are in these cities:')
        for i in icing:
            print(i)
        print('\n')

    if len(snowing) > 0:
        print('Plan your journey thoroughly if you are in these cities:')
        for i in snowing:
            print(i)


# This function will take the information 'printWeatherForecast()' used, this time to create an XML file formatted as
# specified in the assignment briefing
def parseToXML():
    root = Element('WeatherForecasting')
    head = SubElement(root, 'Date', Date=tomorrow)
    goodWthr = SubElement(head, 'GoodWeather')
    goodWthr.text = 'Enjoy the weather if you are living in these cities:'
    towns = SubElement(goodWthr, 'cities')
    for i in sunny:
        SubElement(towns, 'city', name=i)
    poorRain = SubElement(head, 'PoorWeather', Issue='Raining')
    poorRain.text = 'Bring your ambrella if you live in these cities:'
    towns = SubElement(poorRain, 'cities')
    for i in raining:
        SubElement(towns, 'city', name=i)
    poorIce = SubElement(head, 'PoorWeather', Issue='Icing')
    poorIce.text = 'Mind your step if you are in these cities:'
    towns = SubElement(poorIce, 'cities')
    for i in icing:
        SubElement(towns, 'city', name=i)
    poorSnow = SubElement(head, 'PoorWeather', Issue='Snowing')
    poorSnow.text = 'Plan your journey thoroughly if you are in these cities:'
    towns = SubElement(poorSnow, 'cities')
    for i in snowing:
        SubElement(towns, 'city', name=i)

    tree = ET.ElementTree(root)
    tree.write(tomorrow + '.xml')


# Here all the above functions are executed one by one
if __name__ == '__main__':
    input('Press Enter to start...')
    downloadWeatherData()
    extractToCSV()
    categorizeCities()
    printWeatherForecast()
    parseToXML()
