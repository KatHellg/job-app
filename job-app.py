import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
# Define the API endpoint and the headers
API_ENDPOINT = "https://arbeidsplassen.nav.no/public-feed/api/v1/ads"
HEADERS = {
   "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJwdWJsaWMudG9rZW4udjFAbmF2Lm5vIiwiYXVkIjoiZmVlZC1hcGktdjEiLCJpc3MiOiJuYXYubm8iLCJpYXQiOjE1NTc0NzM0MjJ9.jNGlLUF9HxoHo5JrQNMkweLj_91bgk97ZebLdfx3_UQ"
}
def get_data(date_range=None, orgnr=None):
   """Fetch data from the API."""
   params = {}
   if date_range:
       # Format the date range as per the API requirements
       params["published"] = f"[{date_range[0].isoformat()}, {date_range[1].isoformat()}]"
   if orgnr:
       params["orgnr"] = orgnr
   response = requests.get(API_ENDPOINT, headers=HEADERS, params=params)
   if response.status_code == 200:
       return response.json()["content"]
   else:
       st.error(f"Failed to fetch data from the API. Status Code: {response.status_code}")
       return []
def display_ad(ad):
   """Display a single ad in Streamlit."""
   st.title(ad["title"])
   # Display basic info
   st.write(f"Published: {ad['published']}")
   st.write(f"Expires: {ad['expires']}")
   st.write(f"Updated: {ad['updated']}")
   # Display work locations
   for location in ad["workLocations"]:
       st.write(location["country"], "-", location["city"], "-", location["address"])
   # Display the description, assuming it's HTML content
   st.markdown(ad["description"], unsafe_allow_html=True)
   # Display the source and application link
   st.write(f"Source: {ad['source']}")
   st.write(f"More Info: [Link]({ad['sourceurl']})")
   st.write(f"Apply Here: [Link]({ad['applicationUrl']})")

def plot_ads_over_time(ads_data):
   """Plot the number of ads over time."""
   # Extract publication dates
   dates = [ad["published"].split("T")[0] for ad in ads_data]
   df = pd.DataFrame(dates, columns=["Date"])
   # Count the number of ads for each date
   date_counts = df["Date"].value_counts().sort_index()
   # Plot
   plt.figure(figsize=(10,5))
   date_counts.plot(kind='line', marker='o')
   plt.title("Ads Published Over Time")
   plt.xlabel("Date")
   plt.ylabel("Number of Ads")
   plt.grid(True)
   st.pyplot()
def main():
   st.title("Streamlit App for NAV Job Ads API")
   # Date Slider
   today = datetime.now().date()
   selected_date_range = st.date_input("Filter by published date:", [today, today])
   # Orgnr Input
   orgnr = st.text_input("Organization Number (optional, prefix with '!' to exclude):")
   # Fetch data
   ads_data = get_data(selected_date_range, orgnr)
   # Search by Title
   keyword = st.text_input("Search by job title:")
   # Filter by Location
   all_locations = list(set([loc["city"] for ad in ads_data for loc in ad["workLocations"]]))
   selected_location = st.selectbox("Filter by location:", ["All"] + all_locations)
   # Filter ads based on user input
   if keyword:
       ads_data = [ad for ad in ads_data if keyword.lower() in ad["title"].lower()]
   if selected_location != "All":
       ads_data = [ad for ad in ads_data if any(loc["city"] == selected_location for loc in ad["workLocations"])]
   # Display data
   if ads_data:
       for ad in ads_data:
           display_ad(ad)
           st.write("---")  # Add a separator between ads
   else:
       st.write("No job ads match the criteria.")
   # Add a button to plot ads over time
   if st.button("Show Ads Published Over Time"):
       plot_ads_over_time(ads_data)
if __name__ == "__main__":
   main()