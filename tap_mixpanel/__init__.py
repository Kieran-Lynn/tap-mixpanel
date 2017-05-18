import argparse
import json
from datetime import datetime
import requests
import singer

from tap_mixpanel import utils

base_url = 'https://mixpanel.com/api/2.0/'
raw_data_export_url = 'https://data.mixpanel.com/api/2.0/export?'
datetime_format = "%Y-%m-%dT%H:%M:%SZ"

endpoints = {
    "events" : "events"
}
session = requests.Session()
logger = singer.get_logger()

def http_get(url):
    resp = session.request(method='get', url=url)
    return resp

def get_start_date(state, config):
    start_date = config['start-date']
    if state:
        start_date = state['start-date']

    return start_date

def get_end_date(config):
    end_date = datetime.today().strftime(datetime_format)
    if 'end-date' in config:
        end_date = config['end-date']

    return end_date

def get_all_events(state, config):
    events_to_get = config['event-names']
    start_date = get_start_date(state, config)
    end_date = get_end_date(config)

    query_string = utils.build_events_query_string(events_to_get, start_date, end_date)
    response = http_get(base_url + endpoints['events'] + query_string)
    events = response.json()

    formatted_events = utils.convert_events_to_events_schema(events)
    singer.write_records('events', formatted_events)
    state['start-date'] = end_date

    return state

def sync_events(state, config):
    event_schema = utils.load_schema('events')
    singer.write_schema('events', event_schema, 'legend_size')
    state = get_all_events(state, config)
    return state

def get_raw_data(state, config):
    start_date = get_start_date(state, config)
    end_date = get_end_date(config)

    query_string = utils.build_date_query_param(start_date, end_date)
    response = http_get(raw_data_export_url + query_string)
    raw_data = utils.convert_export_response_to_raw_data_schema(response)
    singer.write_records('raw_data', raw_data)

    state['start-date'] = end_date
    return state

def sync_raw_data(state, config):
    raw_data_schema = utils.load_schema('raw_data')
    singer.write_schema('raw_data', raw_data_schema, 'distinct_id')
    state = get_raw_data(state, config)
    return state

def do_sync(config, state):
    logger.info("Starting Mixpanel sync")
    api_key = config['api-secret']
    should_export_events = config['events']
    should_export_raw_data = config['raw-data'].lower()
    utils.authenticate(api_key, session)

    if should_export_events == 'true':
        logger.info('Exporting events data')
        state = sync_events(state, config)
        logger.info('Done exporting events data')

    if should_export_raw_data == 'true':
        logger.info('Exporting raw data')
        state = sync_raw_data(state, config)
        logger.info('Done exporting raw data')

    singer.write_state(state)
    logger.info("Done Mixpanel sync")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', help='Config file', required=True)
    parser.add_argument(
        '-s', '--state', help='State file')

    args = parser.parse_args()
    with open(args.config) as config_file:
        config = json.load(config_file)

    missing_keys = []
    for key in ['api-secret', 'start-date']:
        if key not in config:
            missing_keys += [key]

    if len(missing_keys) > 0:
        logger.fatal("Missing required configuration keys: {}".format(missing_keys))
        exit(1)

    state = {}
    if args.state:
        with open(args.state, 'r') as data_file:
            state = json.load(data_file)

    do_sync(config, state)
    
if __name__ == '__main__':
    main()
