import streamlit as st
import requests
from bs4 import BeautifulSoup

# Step 1: Define beers with correct URLs
beers = [
    {"name": "Víking Lite 500ml", "url": "https://nyjavinbudin.is/vara/viking-lite/"},
    {"name": "Egils Gull 500ml", "url": "https://nyjavinbudin.is/vara/egils-gull-500-ml/"},
]

# Step 2: UI Dropdown
beer_names = [beer["name"] for beer in beers]
selected_beer_name = st.selectbox("Select a beer to check price:", beer_names)
selected_beer = next(beer for beer in beers if beer["name"] == selected_beer_name)

# Step 3: Scraper
def scrape_nyjavinbudin(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        price_span = soup.find("span", class_="woocommerce-Price-amount")
        if price_span:
            return price_span.text.strip()
        return "Price not found"
    except Exception as e:
        return f"Error: {e}"

# Step 4: Show result
price = scrape_nyjavinbudin(selected_beer["url"])
st.write(f"**{selected_beer_name}** at Nýja Vínbúðin: {price}")
