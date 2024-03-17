import requests
from bs4 import BeautifulSoup
import re
from geopy.geocoders import Nominatim
import pandas as pd


# DECLARING FUNCTIONS
def access_beaches_website(base_url: str):
    """
    This function sends a GET request to the website where we extract
    USA Beaches
    """
    # Send an HTTP GET request to the URL and retrieve the content
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(base_url, headers=headers)
    return response

def extract_html_from_scraped_page(response):
    """
    This function examines the response code of the GET function and if it's
    200, it scraps the content of the page using Beautiful Soup, otherwise,
    it returns an error message. The return of this function is a tuple
    (status_code, str)
    """
    if response.status_code == 200:
        html = response.text
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')
        # Find the <ul> element with the class "beach-list"
        beach_list = soup.find('ul', class_='beach-list')
        return response.status_code, beach_list
    elif response.status_code == 404:
        message = "Invalid URL. Error " + str(response.status_code)
    elif response.status_code == 408:
        message = "Time Out. Error " + str(response.status_code)
    else:
        message = "Cannot connect to server. Error " + str(response.status_code)
    return response.status_code, message
    
def clean_h2_text(h2_text):
    """
    This function cleans H2 elements scrapped in the web page.
    """
    h2_text = h2_text.strip()
    # Split the text by the dot
    parts = h2_text.split('.')
    # Replace the first part and dot with nothing
    h2_text = h2_text.replace(parts[0] + ".", "")
    return h2_text

def find_alt_long(address: str):
    """
    This function uses the library geopy to return the latitude and longitude
    values of any given address, in our case, the name of the beaches
    """
    try:
        # Create a Nominatim geocoder object
        geolocator = Nominatim(user_agent="geopy_example")

        # Use the geocoder to obtain location information
        location = geolocator.geocode(address)

        if location is not None:
            latitude = location.latitude
            longitude = location.longitude
        else:
            latitude = ''
            longitude = ''
    except Exception as e:
        latitude = ''
        longitude = ''
    
    return latitude, longitude

def parse_li_element(li:str):
    """
    This function extracts the name of the beach and the state from LI elements
    scrapped in the web page. We use regex to extract the values we need.
    After that, we get the latitude and longitude values of the beach and 
    then return a dict with the extacted elements.
    """
    print(li)
    h2_element = li.find('h2')
    try:
        h2_element = h2_element.text
    except Exception as e:
        pass
    if h2_element:
        h2_text = clean_h2_text(str(h2_element))
        beach_name = re.sub(r'[\n\t]', '', h2_text.split("//")[0]).strip()
        state = re.sub(r'[\n\t]', '', h2_text.split("//")[1]).strip()
        latitude, longitude = find_alt_long(beach_name)
        # Create a dictionary with the extracted information
        beach_data = {
            "beach_name": beach_name,
            "state": state,
            "latitude": latitude,
            "longitude": longitude
        }
        return beach_data
    return None


def get_us_beaches():
    beaches = []
    for i in range(29):
        url = "https://www.worldbeachguide.com/usa/" + str(i+1)
        response = access_beaches_website(url)
        extraction = extract_html_from_scraped_page(response)
        if extraction[0] == 200:
            if extraction[1]:
                # Iterate through each <li> element within the <ul>
                for li in extraction[1].find_all('li'):
                    # Extract the text within the <h2> element
                    beach_data = parse_li_element(li)
                    if beach_data:
                        # Append the dictionary to the list
                        beaches.append(beach_data)
        else:
            return extraction[1] + str(str(i+1))

    return pd.DataFrame(beaches)

if __name__ == "__main__":
    get_us_beaches()