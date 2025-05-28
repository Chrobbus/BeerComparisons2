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
    {"name": "Víking Lite 500ml", "store": "Smáríkið", "id": "65577db2c98d14ede00b576d"},
    {"name": "Gull Lite 500ml", "store": "Smáríkið", "id": "65679ca2988512fb68f35bb5"},
    {"name": "Víking Lite 330ml", "store": "Smáríkið", "id": "67f009370e72d7e1be83155b"},
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
        print(f"⚠️ Nýja Vínbúðin ERROR: {e}")
        return None

# Scraper for Smáríkið using API (with debug logging)
def scrape_smarikid_api(product_id):
    try:
        response = requests.get("https://smarikid.is/api/products", timeout=10)
        response.raise_for_status()
        products = response.json()

        # Debug output
        for product in products:
            print(f"Product ID: {product.get('_id')} | Title: {product.get('title')}")

        for product in products:
            if product.get("_id") == product_id:
                print(f"✅ MATCHED: {product.get('title')}")
                price = float(product.get("price", 0))
                unit_price = price / 12.0
                return price, unit_price

        print(f"❌ Product ID {product_id} not found in API results.")
        return None, None
    except Exception as e:
        print(f"⚠️ API ERROR: {e}")
        return None, None

# Filter entries for selected beer
filtered_entries = [entry for entry in beer_entries if entry["name"] == selected_beer]

# Collect price data
data = []
for entry in filtered_entries:
    store = entry["store"]

    if store == "Nýja Vínbúðin":
        url = entry["url"]
        unit_price = scrape_nyjavinbudin(url)
        if unit_price is not None:
            full_pack_price = unit_price * 12
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Smáríkið":
        product_id = entry["id"]
        full_price, unit_price = scrape_smarikid_api(product_id)
        if full_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_price)} kr", "Unit Price": f"{int(unit_price)} kr"})

# Display results
df = pd.DataFrame(data)
st.write(f"### Prices for **{selected_beer}**")
st.table(df)
