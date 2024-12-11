from utils.imports import * 

# Function to create a grid of points within a shapefile
def generate_csv_from_shape(gdf, resolution):
    # Calculate the bounding box of the shapefile
    bounds = gdf.total_bounds
    min_x, min_y, max_x, max_y = bounds

    # Generate grid points
    x_coords = np.arange(min_x, max_x, resolution)
    y_coords = np.arange(min_y, max_y, resolution)
    points = [Point(x, y) for x in x_coords for y in y_coords]

    # Create GeoDataFrame for grid points
    points_gdf = gpd.GeoDataFrame(geometry=points, crs=gdf.crs)
    points_within = points_gdf[points_gdf.within(gdf.unary_union)]

    # Convert to DataFrame
    points_df = pd.DataFrame({
        'lon': points_within.geometry.x,
        'lat': points_within.geometry.y
    })

    return points_df

# Streamlit App
st.title("Shapefile Uploader and Viewer")

# Sidebar for uploading files
st.header("Upload Shapefile")
st.write("Please upload all components of the shapefile (.shp, .shx, .dbf, .prj) as individual files.")

# File uploader for shapefile
uploaded_files = st.file_uploader(
    "Upload Shapefile Components", type=["shp", "shx", "dbf", "prj"], accept_multiple_files=True
)

if uploaded_files:
    try:
        # Create a temporary directory to store uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            file_mapping = {}

            # Save each uploaded file temporarily
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                file_mapping[os.path.splitext(uploaded_file.name)[1]] = file_path

            # Load the shapefile using GeoPandas
            shapefile_path = file_mapping[".shp"]
            gdf = gpd.read_file(shapefile_path)

            # Display GeoDataFrame info
            st.subheader("Shapefile Information")
            st.write(gdf)

            # Create a Folium map
       
            center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
            print(center)
            print(type(gdf))
            m = folium.Map(location=center, zoom_start=8)
            folium.GeoJson(gdf).add_to(m)

            # Display the map
            st.subheader("Map")
            st_folium(m, width=700, height=500)

            # Option to generate CSV
            st.header("Generate CSV from Shapefile")
            resolution = st.number_input("Enter resolution (e.g., 0.01 degrees):", min_value=0.001, value=0.01, step=0.01)
            if st.button("Generate CSV"):
                csv_data = generate_csv_from_shape(gdf, resolution)
                st.write("Generated CSV Preview:")
                st.write(csv_data.head())

                # Download link for the CSV
                csv_file = csv_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv_file,
                    file_name="generated_points.csv",
                    mime="text/csv"
                )

    except Exception as e:
        print(e)

# CSV Upload Section
st.header("Upload CSV with Coordinates")
uploaded_csv = st.file_uploader("Upload CSV file", type="csv")

if uploaded_csv:
    try:
        # Load CSV into a DataFrame
        csv_df = pd.read_csv(uploaded_csv)

        # Check if necessary columns exist
        if 'lon' in csv_df.columns and 'lat' in csv_df.columns:
            # Create Folium map with points
            st.subheader("Uploaded Coordinates Map")
            m = folium.Map(location=[csv_df['lat'].mean(), csv_df['lon'].mean()], zoom_start=8,control_scale=True)
            m.add_child(MeasureControl(primary_length_unit='meters'))
            for _, row in csv_df.iterrows():
                folium.Marker(location=[row['lat'], row['lon']]).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.error("CSV must contain 'lon' and 'lat' columns.")

    except Exception as e:
        st.error(f"An error occurred while processing the CSV: {e}")
