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
    {"name": "Víking Lite 500ml", "store": "Smáríkið", "query": "Víking Lite 500ml"},
    {"name": "Gull Lite 500ml", "store": "Smáríkið", "query": "Gull Lite"},
    {"name": "Víking Lite 330ml", "store": "Smáríkið", "query": "Víking Lite 330ml"},
    {"name": "Víking Lite 500ml", "store": "Heimkaup", "url": "https://www.heimkaup.is/viking-lite-0-5l-10pk-dos-afhendist-kaldur"},
    {"name": "Víking Lite 330ml", "store": "Heimkaup", "url": "https://www.heimkaup.is/viking-lite-4-4-12-x-330ml"},
    {"name": "Gull Lite 500ml", "store": "Heimkaup", "url": "https://www.heimkaup.is/gull-lite-4-4-12-x-500ml"},
    {"name": "Gull Lite 330ml", "store": "Heimkaup", "url": "https://www.heimkaup.is/gull-lite-4-4-12-x-330ml"},
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

# Scraper for Smáríkið using name matching (uses base_price if sale_price is missing or not lower)
@st.cache_data
def get_smarikid_price(product_name):
    try:
        url = "https://smarikid.is/api/products"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        data = response.json()

        product_list = data.get("products", [])

        for product in product_list:
            name = product.get("name", "").strip()
            if name == product_name:
                base_price = product.get("base_price")
                sale_price = product.get("sale_price")
                final_price = sale_price if sale_price and sale_price < base_price else base_price
                if final_price:
                    unit_price = round(final_price / 12, 2)
                    return final_price, unit_price

        print(f"❌ No match for '{product_name}' in API.")
        return None, None

    except Exception as e:
        print(f"⚠️ Smáríkið API ERROR: {e}")
        return None, None

# Scraper for Heimkaup
def scrape_heimkaup(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        price_tag = soup.find("span", class_="Price")
        if price_tag:
            price_text = price_tag.text.strip().replace("kr.", "").replace(".", "").replace(",", ".")
            return float(price_text)
        return None
    except Exception as e:
        print(f"⚠️ Heimkaup ERROR: {e}")
        return None

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
        product_name = entry["query"]
        full_price, unit_price = get_smarikid_price(product_name)
        if full_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Heimkaup":
        url = entry["url"]
        unit_price = scrape_heimkaup(url)
        if unit_price is not None:
            full_pack_price = unit_price * 12
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})

# Display results
df = pd.DataFrame(data)
st.write(f"### Prices for **{selected_beer}**")
st.table(df)
