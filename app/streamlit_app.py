# app/streamlit_app.py

import sys
import os
import time
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
import altair as alt
from src.agents.price_agent import CarPriceAgent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Drivio – Intelligent Car Valuation",
    page_icon="🚗",
    layout="wide"
)

# ---------------- LOGO PATH ----------------
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "drivio_logo.png")

# ---------------- CLEAN CSS ----------------
st.markdown("""
<style>

/* ---------------- HEADER PREMIUM STYLE ---------------- */

.header-wrapper {
    display: flex;
    align-items: center;
    gap: 18px;
}

/* Gradient + Glow Brand Name */
.brand-title {
    font-size: 60px;
    font-weight: 900;
    margin: 0;
    background: linear-gradient(90deg, #2E86C1, #00D4FF, #4CAF50);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% auto;
    animation: gradientMove 4s linear infinite;
    text-shadow: 0 0 18px rgba(46, 134, 193, 0.4);
    position: relative;
}

/* Animated Gradient */
@keyframes gradientMove {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

/* Animated Underline */
.brand-title::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -8px;
    height: 4px;
    width: 100%;
    background: linear-gradient(90deg, #2E86C1, #00D4FF, #4CAF50);
    border-radius: 6px;
    transform: scaleX(0);
    transform-origin: left;
    animation: underlineGrow 1.2s ease forwards;
}

@keyframes underlineGrow {
    from { transform: scaleX(0); }
    to { transform: scaleX(1); }
}

/* Tagline Beside Title */
.tagline-inline {
    font-size: 18px;
    color: #9aa0a6;
    margin-top: 16px;
    font-weight: 500;
}

/* ---------------- CARDS ---------------- */

.metric-card {
    background: #1e1e1e;
    padding: 28px;
    border-radius: 16px;
    text-align: center;
}

.price {
    font-size: 46px;
    font-weight: 700;
    color: #2E86C1;
}

.range-text {
    font-size: 16px;
    color: #bbbbbb;
    margin-top: 8px;
}

.breakdown-card {
    background: #111;
    padding: 20px;
    border-radius: 12px;
}

.summary-card {
    background: #151515;
    padding: 22px;
    border-radius: 14px;
    line-height: 1.7;
}

.vehicle-card {
    background:#111;
    padding:20px;
    border-radius:18px;
    text-align:center;
}

img {
    border-radius: 16px;
    transition: transform 0.3s ease;
}

img:hover {
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)


# ---------------- HELPER FUNCTIONS ----------------

def prettify_explanation(text: str) -> str:
    replacements = {
        "bodytype_": "Body Type: ",
        "fuel_type_": "Fuel Type: ",
        "transmission_type_": "Transmission: ",
        "brand_": "Brand: ",
        "model_": "Model: ",
        "km_driven_log": "Mileage",
        "car_age": "Car Age",
        "number_of_owners": "Number Of Owners",
        "ownership_classification_": "Ownership: ",
        "_": " "
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.title()


def extract_feature_impacts(explanations):
    rows = []
    for exp in explanations:
        match = re.search(r"₹([\d,]+)", exp)
        if not match:
            continue

        value = int(match.group(1).replace(",", ""))
        direction = 1 if "increased" in exp.lower() else -1
        feature = exp.split(" increased")[0].split(" decreased")[0]

        rows.append({
            "Feature": prettify_explanation(feature),
            "Impact": value * direction
        })
    return rows


def animated_feature_chart(explanations):
    rows = extract_feature_impacts(explanations)
    if not rows:
        return

    df = pd.DataFrame(rows)
    df = df.sort_values("Impact", ascending=False)

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Impact", title="Impact on Price (₹)"),
        y=alt.Y("Feature", sort="-x"),
        color=alt.condition(
            alt.datum.Impact > 0,
            alt.value("#2ecc71"),
            alt.value("#e74c3c")
        ),
        tooltip=["Feature", "Impact"]
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)


def valuation_breakdown(result):
    base_price = result.get("base_model_price", result["predicted_price"])
    adjustment = result.get("ownership_adjustment", 0)
    final_price = result["predicted_price"]

    st.subheader("💰 Valuation Breakdown")

    st.markdown('<div class="breakdown-card">', unsafe_allow_html=True)
    st.write(f"**Base ML Prediction:** ₹ {base_price:,.0f}")

    if adjustment >= 0:
        st.write(f"**Ownership Adjustment:** 🟢 +₹ {adjustment:,.0f}")
    else:
        st.write(f"**Ownership Adjustment:** 🔴 -₹ {abs(adjustment):,.0f}")

    st.write("---")
    st.write(f"### Final Estimated Price: ₹ {final_price:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)


def generate_llm_summary(result):
    final_price = f"₹ {result['predicted_price']:,.0f}"
    lower, upper = result.get("price_range", (0, 0))
    range_text = f"₹ {lower:,.0f} – ₹ {upper:,.0f}"

    paragraph = f"""
Based on the provided vehicle details, Drivio estimates the fair market value at approximately {final_price}.

The expected market range lies between {range_text}, reflecting predictive uncertainty and real-world pricing variability.

The final valuation integrates machine learning prediction, ownership calibration, structured explainability insights, and business-aware pricing logic.
"""
    return paragraph.strip()


# ---------------- BRAND DATA ----------------

brand_models = {
    "Hyundai": ["Creta", "i20", "Verna", "Venue"],
    "Maruti": ["Swift", "Baleno", "Dzire", "Brezza"],
    "Honda": ["City", "Amaze", "WR-V"],
    "Toyota": ["Innova", "Fortuner", "Glanza"],
    "Tata": ["Nexon", "Harrier", "Altroz"]
}

brand_logos = {
    "Hyundai": "https://upload.wikimedia.org/wikipedia/commons/4/44/Hyundai_Motor_Company_logo.svg",
    "Maruti": "https://1000logos.net/wp-content/uploads/2022/08/Maruti-Suzuki-Logo-2000.png",
    "Honda": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Honda_Logo.svg",
    "Toyota": "https://upload.wikimedia.org/wikipedia/commons/9/9d/Toyota_carlogo.svg",
    "Tata": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Tata_logo.svg"
}

car_images = {

    "Hyundai": {
        "Creta": "https://images.91wheels.com/assets/b_images/main/models/profile/profile1767946488.jpg?w=840&q=50",
        "i20": "https://cdn-s3.autocarindia.com/hyundai/i20/_AAB7144.JPG?w=640&q=75",
        "Verna": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Hyundai/Verna/7729/1616055133475/front-left-side-47.jpg",
        "Venue": "https://i.cdn.newsbytesapp.com/images/l207_2251625308944.jpg"
    },

    "Maruti": {
        "Swift": "https://www.autovista.in/assets/img/new_cars_colour_variants/swift-colour-solid-fire-red.jpg",
        "Baleno": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTI0T9AM9QSwgNrGEkH-me5Nnb1aCOpT1pd3w&s",
        "Dzire": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Maruti/Dzire/11387/1758802554630/front-left-side-47.jpg?imwidth=420&impolicy=resize",
        "Brezza": "https://media.spinny.com/sp-file-system/public/2025-01-03/cf67cf32846d41e185e0787fe5fe5ce4/file.JPG"
    },

    "Honda": {
        "City": "https://blogs.gomechanic.com/wp-content/uploads/2019/10/Webp.net-compress-image-1.jpg",
        "Amaze": "https://upload.wikimedia.org/wikipedia/commons/2/25/Honda_Amaze_front_view_%28cropped%29.jpg",
        "WR-V": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Honda/WRV/7665/1593678251480/front-view-118.jpg"
    },

    "Toyota": {
        "Innova": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Toyota/Innova-Crysta/8199/1606212255498/front-left-side-47.jpg?imwidth=420&impolicy=resize",
        "Fortuner": "https://spn-sta.spinny.com/blog/20221202123514/Toyota-Fortuner-1160x653.webp?compress=true&quality=80&w=1200&dpr=2.6",
        "Glanza": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQp_uhicNjUTVRnjQ7f68wxSxswuI-hHolD0A&s"
    },

    "Tata": {
        "Nexon": "https://media.zigcdn.com/media/model/2025/Mar/front-1-4-left-246997292_600x400.jpg",
        "Harrier": "https://spn-sta.spinny.com/blog/20231018141844/Harrier-1-1160x653.webp?compress=true&quality=80&w=1200&dpr=2.6",
        "Altroz": "https://images.timesdrive.in/photo/msid-152769352,thumbsize-148809/152769352.jpg"
    }
}


# ---------------- HEADER ----------------

col_logo, col_header = st.columns([1, 6])

with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=110)

with col_header:
    st.markdown("""
    <div class="header-wrapper">
        <h1 class="brand-title">Drivio</h1>
        <span class="tagline-inline">Intelligent Car Valuation Engine</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()


agent = CarPriceAgent()

# ---------------- SIDEBAR ----------------

st.sidebar.header("🚘 Vehicle Details")

brand = st.sidebar.selectbox("Brand", list(brand_models.keys()))
st.sidebar.image(brand_logos[brand], width=100)

model = st.sidebar.selectbox("Model", brand_models[brand])
fuel = st.sidebar.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG", "Electric"])
trans = st.sidebar.selectbox("Transmission", ["Manual", "Automatic"])
body = st.sidebar.selectbox("Body Type", ["SUV", "Sedan", "Hatchback"])
city = st.sidebar.selectbox("City", ["Delhi", "Mumbai", "Bangalore", "Chennai"])
owners = st.sidebar.selectbox("Number of Owners", [1, 2, 3])
age = st.sidebar.slider("Car Age (years)", 0, 20, 5)
km_log = st.sidebar.slider("Log(KM Driven)", 8.0, 13.0, 10.5)

predict = st.sidebar.button("🔮 Run Valuation")

# ---------------- MAIN ----------------

if predict:

    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)
    progress.empty()

    input_data = {
        "brand": brand,
        "model": model,
        "fuel_type": fuel,
        "transmission_type": trans,
        "bodytype": body,
        "city": city,
        "number_of_owners": owners,
        "car_age": age,
        "km_driven_log": km_log
    }

    result = agent.analyze(input_data)

    st.success("✅ Valuation Complete")

    # -------- Vehicle Preview --------
    st.subheader("🚘 Vehicle Preview")

    with st.container():
        st.markdown('<div class="vehicle-card">', unsafe_allow_html=True)
        time.sleep(0.3)
        
        image_url = car_images.get(brand, {}).get(model)
        if image_url:
            st.image(image_url, width=450)
        else:
            st.info("🚘 Model image not available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # -------- Price Card --------
    lower, upper = result.get("price_range", (0, 0))

    st.markdown(f"""
    <div class="metric-card">
        <div class="price">₹ {result['predicted_price']:,.0f}</div>
        <div class="range-text">
            Estimated Range: ₹ {lower:,.0f} – ₹ {upper:,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # -------- Summary --------
    st.subheader("🧾 AI Generated Market Summary")
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.write(generate_llm_summary(result))
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # -------- Feature + Graph Side by Side --------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Feature Contribution")
        rows = extract_feature_impacts(result["explanation"])
        for row in rows:
            impact = row["Impact"]
            sign = "+" if impact > 0 else "-"
            color = "🟢" if impact > 0 else "🔴"
            st.write(f"{color} {row['Feature']} → {sign}₹ {abs(impact):,}")

    with col2:
        st.subheader("📈 Visual Impact")
        animated_feature_chart(result["explanation"])

    st.divider()

    valuation_breakdown(result)

    st.divider()

    # -------- Negotiation --------
    st.subheader("🤝 Negotiation Strategy")
    col_buy, col_sell = st.columns(2)
    col_buy.success(result["negotiation"]["buyer_advice"])
    col_sell.warning(result["negotiation"]["seller_advice"])

else:
    st.info("👈 Enter vehicle details and click 'Run Valuation'.")
