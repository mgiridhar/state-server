#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''
This is a HTTPServer which has the border information of the states in 'The United States of America' given in latitudes and longitudes.
When queried for a location given by (latitude,longitude), the server replies with a json response which contains a key 'states'. The 
value part of this key is a list of states in which the given location is in. If the location is well contained within a state then it 
returns an array of size 1, whereas if the location is at the border of two or more states then it returns all of them.

class GeospatialStates performs two functions. One function to read the json file and stores the information in a dictionary, and other
is to find the states that contain the given location.

class CustomHTTPRequestHandler is a BaseHTTPRequestHandler for handling HTTP POST and GET requests.
'''

import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import urlparse
from shapely.geometry import Point, Polygon

class GeospatialStates:
    '''
    This class stores the states and border information read from the "states.json" file as a dictionary, where the key represents
    the state's name and value is a Polygon object constructed from the borders' latitude & longitude information.
    The find_states function of this class returns a list of states which is contains the given location.
    '''


    def __init__(self, states_filename = 'states.json'):
        '''
        states: dictionary that holds state-name as key and Polygon object as value
        states_filename: json file that contains the states information - name, borders
        '''
        self.states = {}
        self.initialize(states_filename=states_filename)


    def initialize(self, states_filename = None):
        '''
        Initializes the dictionary data structure from the json file which is "states.json" in this case.
        key - state name
        value - Polygon object constructed from the borders' latitude & longitude
        '''

        # base case check - if states_filename is None then do nothing
        if states_filename is None:
            print "states_filename is None"
            return

        print "initializing data structures"

        try:
            # opening the states file and iterating through it line by line
            with open(states_filename) as states_file:

                # every line in the file contains a state's name and border information that is represented as a json object
                for state in states_file.readlines():
                    
                    # converting a line (string) into json
                    state_json = json.loads(state)
                    
                    # key as state's name, value as Polygon object constructed using it's borders' (longitude, latitude)
                    self.states[str(state_json['state'])] = Polygon(state_json['border'])
        except IOError as ioErr:
            print "I/O error({0}): {1}".format(ioErr.errno, ioErr.strerror)
            print "IO error while opening/closing the given file:", sys.exc_info()[0]
            print "Unable to start the server"
            sys.exit()


    def find_states(self, longitude = None, latitude = None):
        '''
        This function iterates through the states (those which are in the json file) and checks if the given location represented
        by latitude and longitude is contained within that state. If the state contains the location then the state is added
        to the result list.
        '''

        # base case check - if given longitude and latitude is None then return empty list
        if longitude is None or latitude is None:
            return []

        # construct Point object for the given location given by (longitude, latitude)
        location = Point(longitude, latitude)
        
        # list that holds all the state/s that contain required location
        contained_states = []

        # iterating through every <key,value> pair in state dictionary object to see if the given point or location is
        # contained within a state
        for state_name, state_polygon in self.states.iteritems():

            # if the polygon contains the location or if the location touches the border of the polygon then add the state to the list
            if state_polygon.contains(location) or location.touches(state_polygon):
                contained_states.append(state_name)
        
        return contained_states



class CustomHTTPRequestHandler(BaseHTTPRequestHandler):

    # To hold GeospatialStates object
    geo_spatial_states = None


    def _set_headers(self, response_code=200, content_type='application/json'):
        '''
        This function sets the headers for the HTTP response
        '''
        self.send_response(response_code)
        self.send_header('Content-type', content_type)
        self.end_headers()


    def do_GET(self):
        '''
        Handles HTTP Get request of the form "/?longitude=-77.036133&latitude=40.513799"
        
        Response is a json object of the form {"state": ["Pennsylvania"]}
        '''

        try:
            # parse the url path and get the query string
            query_string = urlparse.urlparse(self.path).query

            # get the states that contain the given location and send it as a json response
            json_response = self.get_location_response(query_string=query_string)

            # initializes the headers for the response
            self._set_headers(200, 'application/json')

            self.wfile.write(json_response)

        except KeyError as keyErr:
            self._set_headers(500, 'text/html')
            self.wfile.write("Key Error Occurred at Server, Check if the query string is valid")
            print "Key error:", keyErr

        except ValueError as valueErr:
            self._set_headers(500, 'text/html')
            self.wfile.write("Value Error Occurred at Server, Check if the query string is valid")
            print "Value error:", valueErr

        except TypeError as typeErr:
            self._set_headers(500, 'text/html')
            self.wfile.write("Type Error Occurred at Server")
            print "Type error:", typeErr

        except:
            self._set_headers(500, 'text/html')
            self.wfile.write("Unexpected Error Occurred at Server")
            print "Unexpected error:", sys.exc_info()[0]
            raise

        
    
    def do_POST(self):
        '''
        Handles HTTP POST request with the content/data of the form "longitude=-77.036133&latitude=40.513799"

        Response is a json object of the form {"states": ["Pennsylvania"]}
        '''

        try:
            # get the content length of the POST request
            content_length = self.headers.getheaders('content-length')
            
            # type cast the content length to integer
            length = int(content_length[0]) if content_length else 0
            
            # read the content of the request
            query_string = self.rfile.read(length)

            # get the states that contain the given location and send it as a json response
            json_response = self.get_location_response(query_string=query_string)

            # initializes the headers for the response
            self._set_headers(200, 'application/json')

            self.wfile.write(json_response)
        
        except KeyError as keyErr:
            self._set_headers(500, 'text/html')
            self.wfile.write("Key Error Occurred at Server, Check if the query string is valid")
            print "Key error:", keyErr

        except ValueError as valueErr:
            self._set_headers(500, 'text/html')
            self.wfile.write("Value Error Occurred at Server, Check if the query string is valid")
            print "Value error:", valueErr

        except TypeError as typeErr:
            self._set_headers(500, 'text/html')
            self.wfile.write("Type Error Occurred at Server")
            print "Type error:", typeErr

        except:
            self._set_headers(500, 'text/html')
            self.wfile.write("Unexpected Error Occurred at Server")
            print "Unexpected error:", sys.exc_info()[0]
            raise
        

    def get_location_response(self, query_string = None):
        '''
        Takes query_string as an input which has longitude and latitude values of the required location. 
        
        Returns a json object having the list of all the states that contain the given location.
        '''

        if query_string is None:
            return json.dumps({})

        # parse the query string into a dictionary
        query_dict = urlparse.parse_qs(query_string)

        # if the key is not present or any error in the query string then KeyError is raised
        longitude = float(query_dict['longitude'][0])
        latitude = float(query_dict['latitude'][0])

        """ #IGNORE
        if 'longitude' in query_dict.keys() and len(query_dict['longitude']) > 0:
            longitude = float(query_dict['longitude'][0])
        else:
            longitude = None

        if 'latitude' in query_dict.keys() and len(query_dict['latitude']) > 0:
            latitude = float(query_dict['latitude'][0])
        else:
            latitude = None
        """

        # get those states that contain the given location
        contained_states = self.geo_spatial_states.find_states(longitude=longitude, latitude=latitude)

        return json.dumps({'states': contained_states})


def run(server_class=HTTPServer, handler_class=CustomHTTPRequestHandler, port=8080):
    '''
    Starts the HTTPServer with CustomHTTPRequestHandler at the given port (default: 8080)
    '''
    server_address = ('127.0.0.1', port)
    if handler_class.geo_spatial_states is None:
        handler_class.geo_spatial_states = GeospatialStates()
    
    http_server = server_class(server_address, handler_class)

    print 'Starting HTTP server...'
    http_server.serve_forever()

if __name__ == '__main__':
    '''
    Start of the program
    '''
    if len(sys.argv) > 1 and type(sys.argv[1]) == type(int):
        run(port=int(sys.argv[1]))
    else:
        run()
