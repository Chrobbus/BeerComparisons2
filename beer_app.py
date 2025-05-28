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
    {"name": "Víking Lite 500ml", "store": "Smáríkið", "url": "https://smarikid.is/product/65577db2c98d14ede00b576d"},
    {"name": "Gull Lite 500ml", "store": "Smáríkið", "url": "https://smarikid.is/product/65679ca2988512fb68f35bb5"},
    {"name": "Víking Lite 330ml", "store": "Smáríkið", "url": "https://smarikid.is/product/67f009370e72d7e1be83155b"},
]

# Dropdown to select beer
unique_beers = sorted(list(set(entry["name"] for entry in beer_entries)))
selected_beer = st.selectbox("Select a beer:", unique_beers)

# Scraper for Nýja Vínbúðin (discount-aware)
def scrape_nyjavinbudin(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        ins_tag = soup.find("ins")
        if ins_tag:
            price_span = ins_tag.find("span", class_="woocommerce-Price-amount")
            if price_span:
                price_text = price_span.text.strip().replace("kr.", "").replace(".", "").replace(",", ".")
                return float(price_text)

        price_span = soup.find("span", class_="woocommerce-Price-amount")
        if price_span:
            price_text = price_span.text.strip().replace("kr.", "").replace(".", "").replace(",", ".")
            return float(price_text)

        return None
    except Exception as e:
        return None

# Scraper for Smáríkið (price for 12-pack)
def scrape_smarikid(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        h2_tag = soup.find("h2", class_="text-xl  md:text-3xl font-medium")
        if h2_tag:
            price_text = h2_tag.text.strip().replace("Kr.", "").replace("kr.", "").replace("kr", "").replace("\xa0", "").replace(".", "").replace(",", ".")
            full_pack_price = float(price_text)
            unit_price = full_pack_price / 12.0
            return full_pack_price, unit_price

        return None, None
    except Exception as e:
        return None, None

# Filter entries for selected beer
filtered_entries = [entry for entry in beer_entries if entry["name"] == selected_beer]

# Collect price data
data = []
for entry in filtered_entries:
    store = entry["store"]
    url = entry["url"]
    
    if store == "Nýja Vínbúðin":
        unit_price = scrape_nyjavinbudin(url)
        if unit_price:
            full_pack_price = unit_price * 12
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Smáríkið":
        full_price, unit_price = scrape_smarikid(url)
        if full_price and unit_price:
            data.append({"Store": store, "12-pack Price": f"{int(full_price)} kr", "Unit Price": f"{int(unit_price)} kr"})

# Display results
df = pd.DataFrame(data)
st.write(f"### Prices for **{selected_beer}**")
st.table(df)
