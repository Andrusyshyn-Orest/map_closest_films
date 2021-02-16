"""
GitHub repository: https://github.com/Andrusyshyn-Orest/map_closest_films.git
This module generates a map of closest
places to user location where films from locations.list were shoot.
"""
from math import radians, cos, sin, asin, sqrt
import threading
import sys
import itertools
import time
import folium

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter



def input_info() -> tuple:
    """
    Input year, latitude, longitude. Return tuple:
    (year, (latitude, longitude))
    """

    year = input("Please, enter which year you are interested in: ")
    latitude = float(input("Please, enter your latitude: "))
    longitude = float(input("Please, enter your longitude: "))
    return year, (latitude, longitude)


def read_file(name: str, year: str, coord = []) -> list:
    """
    Reads a file name, returns list of lists as:
    [[film, place], ...], where film - is a title of film, place -
    is a place for this film. There are only films that were shoot in
    specified year and in specified country (coord is a list of coordinates
    which belong to a specified country). If coordinates do not belong
    to any country, return ['Exception'].

    >>> read_file("locations.list", '2006')[:2]
    [['"#1 Single" (2006)', 'Los Angeles, California, USA'],
 ['"#1 Single" (2006)', 'New York City, New York, USA']]
    """

    if coord:
        geolocator = Nominatim(user_agent="webmap")
        try:
            location =\
 geolocator.reverse(coord, language='en').raw['address']['country']
        except:
            return ['Exception']
        if location == 'United States':
            location = 'USA'

    films = []
    with open(name, mode='r', encoding='UTF-8', errors="ignore")\
                                                     as file_locations:
        line = file_locations.readline()
        while not line.startswith('='):
            line = file_locations.readline()
        for line in file_locations:
            line = line.strip()
            if not line.startswith('----'):
                line_lst = list( filter(None, line.split('\t')) )
                film = line_lst[0]
                place = line_lst[1]
                if coord:
                    if location not in place:
                        continue
                ind1 = film.index('(')
                ind2 = film.index(')')
                if film[ind1 + 1: ind2] == year:
                    films.append( [film, place] )
    if len(films) > 100:
        return films[:100]
    return films


def find_coordinates_by_name(name: str) -> tuple:
    """
    Return coordinates as a tuple from name of the place.

    >>> find_coordinates_by_name('Старі Кути')
    (48.287312, 25.1738)
    """


    geolocator = Nominatim(user_agent="webmap")
    location = geolocator.geocode(name)
    name = name.split(',')
    while not location:
        name = ','.join(name[1:])
        location = geolocator.geocode(name)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0)
    return location.latitude, location.longitude


def transform_list(films: list) -> list:
    """
    Return list as [[film, (latitude, longitude)], ...] from
    list (films):  [[film, place], ...], where film is a title of film,
    place is a name of place where film was shoot, (lat, lon) is coordinates
    of the place.

    >>> transform_list(read_file("locations.list", '2015'))[:2]
    [['"#15SecondScare" (2015) {It\\'s Me Jessica (#1.5)}',\
 (52.4081812, -1.510477)], ['"#15SecondScare" (2015) {Who Wants to\
 Play with the Rabbit? (#1.2)}', (34.2032325, -118.645476)]]
    """

    films_coord = []
    for film in films:
        #print(film)
        #print(film)

        try:
            films_coord.append([film[0], find_coordinates_by_name(film[1])])
        except:
            continue
    return films_coord


def distance_between_to_locations(lat1: float, lat2: float, lon1: float,
                                  lon2: float) -> float:
    """
    Returns distance between two locations by theit coordinates in km.

    Took formula from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

    >>> distance_between_to_locations(49.8, 50.4, 24, 30.6)
    475.2924415293368
    """

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    under_sqrt = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    koef = 2 * asin(sqrt(under_sqrt))
    radius = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return koef * radius
    # return haversine.haversine((lat1, lon1), (lat2, lon2))


def find_closest(lat: float, lon: float,
                 number: int, year_list: list) -> list:
    """
    Return list of number or less films that are the closest to (lat, lon)
    from year_list: [[film, (latitude, longitude)], ...], where film is a
    title of film, (lat, lon) is coordinates of place where film was shoot.
    >>> find_closest(49, 24, 10,\
 transform_list(read_file("locations.list", '2015')))
    [['"1945: 12 Stdte, 12 Schicksale" (2015) {Augsburg - Die\
 Entnazifizierung (#1.6)}', (50.03890605, 19.171298357759902)],\
 ['"12 Monkeys" (2015) {Year of the Monkey (#2.1)}',\
 (47.4983815, 19.0404707)], ['"12 Monkeys" (2015)\
 {Year of the Monkey (#2.1)}', (47.4983815, 19.0404707)],\
 ['"1945: 12 Stdte, 12 Schicksale" (2015) {Braunschweig - Die Ruinen\
 (#1.7)}', (52.2319581, 21.0067249)], ['"1945: 12 Stdte, 12 Schicksale"\
 (2015) {Amsterdam - DerVlkermord (#1.11)}',\
 (48.2083537, 16.3725042)], ['"12 Monkeys" (2015) {Thief (#3.9)}',\
 (50.0874654, 14.4212535)], ['"12 Monkeys" (2015) {Thief (#3.9)}',\
 (50.09086385, 14.40057198099588)], ['"10,000 BC" (2015)',\
 (42.6073975, 25.4856617)], ['"1945: 12 Stdte, 12 Schicksale" (2015)\
 {Berlin - Der Neubeginn (#1.12)}', (52.5318238, 14.380704)],\
 ['"12 Monkeys" (2015) {Tomorrow (#1.9)}', (42.079261, 22.1802182)]]
    """

    year_list.sort(key=lambda x:
                   distance_between_to_locations(lat, x[1][0], lon, x[1][1]))
    return year_list[:number]


def transform_to_dict(closest_list: list) -> dict:
    """
    Returns dict {(latitude, longitude): {film1, film2, ...}, ...} from
    closest_list [[film1, (latitude, longitude)], ...], where film1,
    film2 are titles of films, (latitude, longitude) is a coordinates of
    a place where those films were shoot.

    >>> transform_to_dict([["film1", (49, 24)]])
    {(49, 24): {'film1'}}
    """

    closest_dict = {}
    for film, coord in closest_list:
        if coord in closest_dict:
            closest_dict[coord].add(film)
        else:
            closest_dict[coord] = {film}
    return closest_dict



def generate_map(closest_dict: dict, lat, lon):
    """
    Generates map to file "Map_1.html" from closest_dict:
    {(latitude, longitude): {film1, film2, ...}, ...}, where film1,
    film2 are titles of films, (latitude, longitude) is a coordinates of
    a place where those films were shoot. lat, lon are coordinates of user
    location.
    """

    my_map = folium.Map(tiles="Stamen Terrain",
                     location=[lat, lon],
                     zoom_start=3)
    fg_markers = folium.FeatureGroup(name="markers")
    fg_lines = folium.FeatureGroup(name='lines')
    for coord, film in closest_dict.items():
        #print(film)
        lat1, lon1 = coord[0], coord[1]
        fg_markers.add_child(folium.Marker(location=[lat1, lon1],
                                   popup=str(film)[1:-1],
                                   icon=folium.Icon()))
        fg_lines.add_child(folium.vector_layers.PolyLine(
            [(lat, lon), (lat1, lon1)],
            popup = str(
                        round(
                    distance_between_to_locations(lat, lat1, lon, lon1), 2)
                        )
                        + 'km'))
    my_map.add_child(folium.Marker(location = [lat, lon],
                                popup = 'Me',
                                icon = folium.Icon(color='red')))
    my_map.add_child(fg_markers)
    my_map.add_child(fg_lines)
    my_map.add_child(folium.LayerControl())
    my_map.save("Map_1.html")


def main():
    """
    Runs a program.
    """

    info = input_info()
    year = info[0]
    lat = info[1][0]
    lon = info[1][1]

    films = read_file('locations.list', year, coord = [str(lat), str(lon)])
    while films == ['Exception']:
        print('Your coordinates do not belong to any country')
        print('Please, enter parameters one more time:')
        info = input_info()
        year = info[0]
        lat = info[1][0]
        lon = info[1][1]
        films = read_file('locations.list', year, coord=[str(lat), str(lon)])

    done = False
    def animate():
        for char in itertools.cycle(['.', '..', '...']):
            if done:
                break
            sys.stdout.write('\rGenerating map ' + char + '  ')
            sys.stdout.flush()
            time.sleep(0.3)

    thread = threading.Thread(target=animate)
    thread.start()
    films_coord = transform_list(films)
    closest_list = find_closest(lat, lon, 10, films_coord)
    closest_dict = transform_to_dict(closest_list)
    generate_map(closest_dict, lat, lon)

    sys.stdout.write('\r')
    print("Check out map in Map_1.html")
    done = True

if __name__ == "__main__":
    # import doctest
    # print(doctest.testmod())
    #start = time.time()
    main()
    #print(time.time() - start)
