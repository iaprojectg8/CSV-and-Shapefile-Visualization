from utils.imports import *

def get_lat_lon(row):
    """
    Extracts latitude and longitude from a DataFrame row.
    
    Args:
        row (pd.Series): A row from the DataFrame containing 'lat' and 'lon' fields.
    
    Returns:
        tuple: A tuple containing the latitude and longitude.
    """
    lat = row["lat"]
    lon = row["lon"]

    return lat, lon


def get_data_from_open_meteo(url, params):
    """
    Fetches weather data from the Open Meteo API using specified URL and parameters.
    
    Args:
        url (str): The API endpoint URL for fetching weather data.
        params (dict): Parameters for the API request.
    
    Returns:
        dict: The API response containing weather data.
    """
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    responses = openmeteo.weather_api(url, params=params)   
    response = responses[0]
    return response


def fill_daily_dict(daily, lat, lon):
    """
    Fills a dictionary with daily weather data including date, latitude, and longitude.
    
    Args:
        daily (object): Object containing daily weather data from the API response.
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        
    Returns:
        dict: A dictionary with the date, latitude, longitude, and weather variables.
    """
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "lat": lat,
        "lon": lon,
        "temperature": daily.Variables(0).ValuesAsNumpy()

    }
    return daily_data
