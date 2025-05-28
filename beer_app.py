import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# List of beers across stores
beer_entries = [
    {"name": "Víking Lite 500ml", "store": "Nýja Vínbúðin", "url": "https://nyjavinbudin.is/vara/viking-lite/"},
    {"name": "Víking Lite 330ml", "store": "Nýja Vínbúðin", "url": "https://nyjavinbudin.is/vara/viking-lite-330ml/"},
    {"name": "Gull Lite 500ml", "store": "Nýja Vínbúðin", "url": "https://nyjavinbudin.is/vara/gull-lite-500-ml-dos/"},
    {"name": "Gull Lite 330ml", "store": "Nýja Vínbúðin", "url": "https://nyjavinbudin.is/vara/gull-lite-330-ml-dos/"},
]

# Dropdown to select beer
unique_beers = sorted(list(set(entry["name"] for entry in beer_entries)))
selected_beer = st.selectbox("Select a beer:", unique_beers)

# Function to scrape price (discount-aware)
def scrape_nyjavinbudin(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try discount price first
        ins_tag = soup.find("ins")
        if ins_tag:
            price_span = ins_tag.find("span", class_="woocommerce-Price-amount")
            if price_span:
                return price_span.text.strip()

        # Fallback to regular price
        price_span = soup.find("span", class_="woocommerce-Price-amount")
        if price_span:
            return price_span.text.strip()

        return "Price not found"
    except Exception as e:
        return f"Error: {e}"

# Filter beer entries that match selected beer
filtered_entries = [entry for entry in beer_entries if entry["name"] == selected_beer]

# Collect prices for all stores
data = []
for entry in filtered_entries:
    price = scrape_nyjavinbudin(entry["url"])
    data.append({
        "Store": entry["store"],
        "Price": price
    })

# Display results in a table
df = pd.DataFrame(data)
st.write(f"### Prices for **{selected_beer}**")
st.table(df)
