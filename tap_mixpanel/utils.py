import json
import os
import urllib
from datetime import datetime
from base64 import b64encode

datetime_format = "%Y-%m-%dT%H:%M:%SZ"
mixpanel_date_format = "%Y-%m-%d"


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schema(entity):
    with open(get_abs_path('schemas/{}.json'.format(entity))) as file:
        return json.load(file)

def authenticate(api_key, session):
    encoded_key = b64encode(bytes("{0}".format(api_key), 'utf-8')).decode("ascii")
    session.headers.update({ 'Authorization': 'Basic {0}'.format(encoded_key)})

def convert_events_to_events_schema(events):
    formatted_events = []
    for event in events['data']['values']:
        formatted_event = {}
        formatted_event['event'] = event
        formatted_event['values'] = {}
        for date in events['data']['values'][event]:
            formatted_event['values'][date] = events['data']['values'][event][date]
        formatted_events.append(formatted_event)

    return formatted_events

def fill_in_missing_values(line):
    schema = load_schema('raw_data')
    for prop in schema['properties']['event_properties']['properties']:
        if prop not in line:
            line[prop] = ""

    return line

def convert_export_response_to_raw_data_schema(response):
    raw_data = []
    for line in response.text.splitlines():
        line = line.replace('properties', 'event_properties')
        json_line = json.loads(line)
        complete_line = fill_in_missing_values(json_line)
        raw_data.append(json.loads(line))
        
    return raw_data

#per the Mixpanel API the events query param should be in this format: 
#"["play song", "log in", "add playlist"]"
def build_event_query_param(events_to_get):
    event_query = '['
    for event in events_to_get:
        event_query += '"{0}",'.format(event)
    event_query = event_query[:-1] #strip off last comma
    event_query += "]"
    encoded_event_query = urllib.parse.quote(event_query)
    event_query_param = "&event=" + encoded_event_query

    return event_query_param

#Mixpanel API Date format:
#yyyy-mm-dd
def convert_date_string_to_mixpanel_format(date_string):
    date = datetime.strptime(date_string, datetime_format)
    date = date.strftime(mixpanel_date_format)

    return date

def build_date_query_param(start_date, end_date):
    from_date = convert_date_string_to_mixpanel_format(start_date)
    to_date = convert_date_string_to_mixpanel_format(end_date)
    query_string = 'from_date={0}&to_date={1}'.format(from_date, to_date)

    return query_string

def build_events_query_string(events_to_get, start_date, end_date):
    query_string = "?type=general&unit=day&" + build_date_query_param(start_date, end_date)

    event_query_param = build_event_query_param(events_to_get)

    return query_string + event_query_param