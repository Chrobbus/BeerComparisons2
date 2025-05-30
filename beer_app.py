import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Beer Price Comparison", page_icon="🍺", layout="centered")

st.title("🍺 Gull & Viking Lite Price Comparison ")
st.caption("Real-time comparison from Icelandic Online Liquor Stores")

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
    {"name": "Víking Lite 500ml", "store": "Costco", "url": "https://www.costco.is/Alcohol-Click-Collect/Viking-Lite-12-x-500ml/p/453945"},
    {"name": "Gull Lite 500ml", "store": "Costco", "url": "https://www.costco.is/Alcohol-Click-Collect/Gull-Lite-12-x-500ml/p/453613"},
    {"name": "Víking Lite 500ml", "store": "Hagkaup", "url": "https://www.veigar.eu/vara/viking-lite-500-ml-12pk-157969"},
    {"name": "Gull Lite 500ml", "store": "Hagkaup", "url": "https://www.veigar.eu/vara/gull-lite-500-ml-12pk-158102"},
    {"name": "Víking Lite 330ml", "store": "Hagkaup", "url": "https://www.veigar.eu/vara/viking-lite-330-ml-12pk-157965"},
    {"name": "Gull Lite 330ml", "store": "Hagkaup", "url": "https://www.veigar.eu/vara/gull-lite-330ml-12pk-158111"},
    {"name": "Víking Lite 330ml", "store": "Santé", "url": "https://sante.is/products/viking-lite-33-cl-dos?_pos=1&_psq=Viking+lite&_ss=e&_v=1.0"},
    {"name": "Víking Lite 500ml", "store": "Santé", "url": "https://sante.is/products/viking-lite-50-cl-dos?_pos=8&_psq=lite&_ss=e&_v=1.0"},
    {"name": "Gull Lite 330ml", "store": "Santé", "url": "https://sante.is/products/gull-lite-12-i-rutu?_pos=3&_psq=lite&_ss=e&_v=1.0"},
    {"name": "Gull Lite 500ml", "store": "Santé", "url": "https://sante.is/products/gull-lite-12-ofurdosir-i-rutu?_pos=4&_psq=lite&_ss=e&_v=1.0"},
    {"name": "Víking Lite 500ml", "store": "Desma", "url": "https://desma.is/products/viking-lite-500ml-4-4"},
    {"name": "Gull Lite 500ml", "store": "Desma", "url": "https://desma.is/products/gull-lite-500ml?_pos=2&_psq=gull+lite&_ss=e&_v=1.0"},
    {"name": "Gull Lite 330ml", "store": "Desma", "url": "https://desma.is/products/gull-lite-330ml?_pos=1&_psq=gull+lite+330&_ss=e&_v=1.0"},
    {"name": "Víking Lite 330ml", "store": "Desma", "url": "https://desma.is/products/viking-lite-330ml-4-4?_pos=1&_psq=viking+lite+330&_ss=e&_v=1.0"},
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

# Scraper for Smáríkið using name matching
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
            full_pack_text = price_tag.text.strip().replace("kr.", "").replace(".", "").replace(",", ".")
            full_pack_price = float(full_pack_text)
            unit_price = round(full_pack_price / 12, 2)
            return full_pack_price, unit_price
        return None, None
    except Exception as e:
        print(f"⚠️ Heimkaup ERROR: {e}")
        return None, None

# Scraper for Costco
def scrape_costco(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        price_span = soup.find("span", string=lambda text: text and "kr." in text)
        if price_span:
            full_pack_text = price_span.text.strip().replace("kr.", "").replace(".", "").replace(",", ".")
            full_pack_price = float(full_pack_text)
            unit_price = round(full_pack_price / 12, 2)
            return full_pack_price, unit_price
        return None, None
    except Exception as e:
        print(f"⚠️ Costco ERROR: {e}")
        return None, None

# Scraper for Hagkaup (veigar.eu)
def scrape_veigar(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        price_paragraphs = soup.find_all("p")
        for p in price_paragraphs:
            if p.text.strip().startswith("Verð:"):
                price_span = p.find("span")
                if price_span:
                    price_text = price_span.text.strip().replace("kr.", "").replace(".", "").replace(",", ".")
                    full_pack_price = float(price_text)
                    unit_price = round(full_pack_price / 12, 2)
                    return full_pack_price, unit_price

        return None, None
    except Exception as e:
        print(f"⚠️ Veigar ERROR: {e}")
        return None, None

# Scraper for Santé
def scrape_sante(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        price_span = soup.find("span", class_="price-item--regular")
        if price_span:
            price_text = price_span.text.strip().replace("ISK", "").replace("kr.", "").replace(".", "").replace(",", ".")
            full_pack_price = float(price_text)
            unit_price = round(full_pack_price / 12, 2)
            return full_pack_price, unit_price
        return None, None
    except Exception as e:
        print(f"⚠️ Santé ERROR: {e}")
        return None, None

# Scraper for Desma
def scrape_desma(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # First try sale price
        sale = soup.select_one("span.price-item--sale")
        if sale and sale.text.strip():
            price_text = sale.text.strip()
        else:
            # Fallback to regular price
            regular = soup.select_one("span.price-item--regular")
            if not regular or not regular.text.strip():
                print("⚠️ No price found on Desma page")
                return None, None
            price_text = regular.text.strip()

        price_text = price_text.replace("kr.", "").replace("kr", "").replace("ISK", "").replace(".", "").replace(",", ".").strip()
        full_pack_price = float(price_text)
        unit_price = round(full_pack_price / 12, 2)

        print(f"🧪 Desma scraped: {full_pack_price} ISK total / {unit_price} ISK per can")
        return full_pack_price, unit_price

    except Exception as e:
        print(f"⚠️ Desma ERROR: {e}")
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
        product_name = entry["query"]
        full_price, unit_price = get_smarikid_price(product_name)
        if full_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Heimkaup":
        url = entry["url"]
        full_pack_price, unit_price = scrape_heimkaup(url)
        if full_pack_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Costco":
        url = entry["url"]
        full_pack_price, unit_price = scrape_costco(url)
        if full_pack_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Hagkaup":
        url = entry["url"]
        full_pack_price, unit_price = scrape_veigar(url)
        if full_pack_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Santé":
        url = entry["url"]
        full_pack_price, unit_price = scrape_sante(url)
        if full_pack_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})
    elif store == "Desma":
        url = entry["url"]
        print(f"🔍 Scraping Desma URL: {url}")
        full_pack_price, unit_price = scrape_desma(url)
        print(f"🧪 Desma result: full={full_pack_price}, unit={unit_price}")
        if full_pack_price is not None and unit_price is not None:
            data.append({"Store": store, "12-pack Price": f"{int(full_pack_price)} kr", "Unit Price": f"{int(unit_price)} kr"})

# Only proceed if we have any price data
if data:
    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Extract numeric value from "12-pack Price" column for sorting/comparison
    df["12-pack Numeric"] = df["12-pack Price"].str.replace(" kr", "").str.replace(".", "").astype(int)

    # Sort by numeric price
    df = df.sort_values(by="12-pack Numeric")

    # Find the cheapest price
    cheapest = df["12-pack Numeric"].min()

    # Compare each price to the cheapest and format
    df["Compared to Cheapest"] = df["12-pack Numeric"].apply(
        lambda x: "Cheapest 🥇" if x == cheapest else f"+{int(round((x - cheapest) / cheapest * 100))}%"
    )

    # Drop the helper column
    df.drop(columns=["12-pack Numeric"], inplace=True)

    # Final display DataFrame
    df_display = df.reset_index(drop=True)

    # Show the updated table
    st.markdown(f"### 🍺 Prices for **{selected_beer}**")
    st.table(df_display)
else:
    st.write("No price data available.")
