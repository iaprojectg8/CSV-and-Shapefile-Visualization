from utils.imports import *
from function import *


cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def build_api_params(lat, lon):
    """
    Constructs the API parameters for the request based on latitude, longitude, and variables.
    
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
    
    Returns:
        dict: Parameters for the API request.
    """
    return {
        "latitude": lat,
        "longitude": lon,
        "start_date": "1950-01-01",
        "end_date": "1950-01-01",
        "models": "MRI_AGCM3_2_S",
        "daily": "temperature_2m_mean",
        "timezone": "auto",
        "wind_speed_unit": "ms"
    }

def get_open_meteo_resolution(coordinates_csv, dataset_folder):
    """
    Orchestrates the process of requesting and saving daily weather data for multiple coordinates.
    
    Args:
        coordinates_csv (str): Path to the CSV file containing coordinates.
        dataset_folder (str): Path to the folder where the results will be saved.
    """
    try:
        with open(coordinates_csv, 'r') as file:
            # Process the file as needed
            pass
    except FileNotFoundError:
        print("The coordinates file has not been found.")

    if os.path.isdir(dataset_folder):
        print("Dataset folder already exist")
    else:
        os.makedirs(dataset_folder)
        print("Dataset folder created")
    url ="https://climate-api.open-meteo.com/v1/climate"
    df = pd.read_csv(coordinates_csv)
    final_df = pd.DataFrame()
    
    for index, row in tqdm(df.iterrows(),total=len(df), desc="Processing rows"):

        lat, lon = get_lat_lon(row)
        params = build_api_params(lat, lon)


   
        
        response = get_data_from_open_meteo(url, params)
        if response:
            
            daily = response.Daily()

            daily_data = fill_daily_dict(daily, lat, lon)
            daily_df = pd.DataFrame(daily_data)
            final_df = pd.concat([final_df, daily_df])
            

        else:
            print(f"No data for point: Latitude {lat}, Longitude {lon}")
            
    
    final_df.to_csv("data_extracted.csv")


def get_unique_coordinates(csv_name):
    df = pd.read_csv(csv_name)
    unique_df = df[['lon', 'lat']].drop_duplicates()
    unique_df.to_csv("unique_coordinates_gambia.csv", index=False)

csv_path = "generated_points(7).csv"
dataset_folder = "data"

get_open_meteo_resolution(csv_path, dataset_folder)
# get_unique_coordinates("data_extracted.csv")