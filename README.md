# tap-mixpanel

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:
- Pulls raw data from Mixpanel's [REST API](https://mixpanel.com/api/2.0/)
- Extracts the following resources from Mixpanel:
  - [Events](https://mixpanel.com/help/reference/data-export-api#events)
  - [Raw Data](https://mixpanel.com/help/reference/exporting-raw-data)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state and configtwin 


## Quick start

1. Install

    ```bash
    > pip install tap-mixpanel
    ```

2. Get your Mixpanel API Secret

    Login to your Mixpanel account, click your name in the top right.
    Click project settings. You'll see your API secret there. 

3. Create the config file

    Create a JSON file called `config.json` containing the api secret and the name events you want to pull in the following format.

    ```json
    {
        "api-secret": "your-api-secret",
        "raw-data": "true", 
        "events": "true",
        "event-names": ["event1", "event2"],
        "start-date": "2017-05-10T00:00:00Z",
        "end-date":"2017-05-11T00:00:00Z" #optional
    }
    ```

    **raw-data(required):** Determines whether or not to sync Mixpanel raw data. This is a bool <br />
    **events(required):** Determines whether or not to sync Mixpanel raw data. This is a bool. <br />
    **event-names(required if events is true):** Array must be populated with valid event names. This is how the Mixpanel API works, it expects an array of event names.<br />
    **start-date(required):** Determines pulls data from after that day<br />
    **end-date(optional):** Determines limits the data to the days between start-date and end-date. If no end-date is provided then the default is the current day.

4. [Optional] Create the initial state file

    You can provide JSON file that contains a start date to pull data from. This will override the required `start-date` in the config file. The state is output after the program is run to stdout with a new state file where the old `end-date` becomes the new state's `start-date`. See the Singer documentation for more information on states.

    **Keep in mind that if you use this feature you'll need to update the end-date in the config or else you'll end up pulling data from only one day.**

    ```json
    {"start-date": "2017-01-17T20:00:00Z"}
    ```

5. Run the application

    `tap-mixpanel` can be run with:

    ```bash
    tap-mixpanel --config config.json [--state state.json]
    ```

6. [Optional] Save state

    ```bash
    › tap-mixpanel --config config.json --state state.json >> state.json
    › tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

### Limitations

1. Events

Events currently does not sort the returned dates so the output can be a little wonky.

2. Raw Data

The mixpanel API is super slow at returning the raw data export. Be prepared to wait if 
you're trying to pull a large amount of data. Also, events can have any number of custom properties so you cannot depend on each event object returned to have the same number of properties. <br/>
**This can cause some weirdness if you use target-csv**

---
