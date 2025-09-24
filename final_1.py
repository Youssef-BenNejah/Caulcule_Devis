import streamlit as st
import pandas as pd
import math
import json
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time

# ========= PAGE CONFIG ==========
st.set_page_config(
    page_title="🚚 Tictak Price Estimator",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========= CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --light-bg: #f8f9fa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem !important;
        opacity: 0.9;
        margin-bottom: 0 !important;
    }
    
    /* Card styling */
    .stExpander {
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border-radius: 15px !important;
        margin-bottom: 1rem !important;
    }
    
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-radius: 15px !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px !important;
        border: 2px solid #e1e5e9 !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: rgba(40, 167, 69, 0.1) !important;
        border: 1px solid #28a745 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background: rgba(220, 53, 69, 0.1) !important;
        border: 1px solid #dc3545 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid #ffc107 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    /* Metrics styling */
    .stMetric {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e1e5e9 !important;
    }
    
    .stMetric > div {
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%) !important;
    }
    
    /* Price display styling */
    .price-display {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
    }
    
    .price-amount {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .price-label {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Item selection styling */
    .item-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .item-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    }
    
    /* API Key input styling */
    .api-key-container {
        background: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Distance info styling */
    .distance-info {
        background: #e8f4f8;
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========= CONFIG ==========
ITEMS_JSON = "tictak.items.json"   # Must be in the same folder

# Initialize API key in session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = "AIzaSyCOxZCCAhsTSZPJwX7qumKmWaRKlTKpJew"

# ========= LOAD ITEMS =========
@st.cache_data
def load_items():
    try:
        with open(ITEMS_JSON, "r", encoding="utf-8") as f:
            items_data = json.load(f)
        return pd.DataFrame(items_data)
    except FileNotFoundError:
        # Sample data if JSON file not found
        sample_data = [
            {"key": "Small Box", "volume": 0.1, "min_truck_size": 12, "stairTime": 30},
            {"key": "Large Box", "volume": 0.3, "min_truck_size": 12, "stairTime": 60},
            {"key": "Sofa 2-seater", "volume": 2.5, "min_truck_size": 12, "stairTime": 300},
            {"key": "Sofa 3-seater", "volume": 3.5, "min_truck_size": 12, "stairTime": 420},
            {"key": "Dining Table", "volume": 1.8, "min_truck_size": 12, "stairTime": 240},
            {"key": "Wardrobe", "volume": 4.0, "min_truck_size": 20, "stairTime": 600},
            {"key": "Washing Machine", "volume": 0.8, "min_truck_size": 12, "stairTime": 480},
            {"key": "Refrigerator", "volume": 1.2, "min_truck_size": 12, "stairTime": 600},
            {"key": "Mattress Single", "volume": 0.5, "min_truck_size": 12, "stairTime": 120},
            {"key": "Mattress Double", "volume": 0.8, "min_truck_size": 12, "stairTime": 180}
        ]
        st.warning("⚠️ Items JSON file not found. Using sample data.")
        return pd.DataFrame(sample_data)

items_df = load_items()

# Validate required columns
required_cols = ["key", "volume", "min_truck_size", "stairTime"]
if not all(c in items_df.columns for c in required_cols):
    st.error(f"❌ JSON must include columns: {required_cols}")
    st.stop()

# ========= FUNCTIONS =========
def rate_per_minute(total_items: int) -> float:
    """Rate €/minute based on total number of items."""
    if total_items <= 5: return 2
    if total_items <= 10: return 3
    if total_items <= 15: return 4
    if total_items <= 20: return 5.5
    if total_items <= 25: return 6.5
    return 7.35 + math.ceil((total_items - 25) / 5)

def truck_fee(total_volume: float, min_required: float) -> float:
    """Base truck fee depending on total volume and min truck size."""
    if total_volume <= 12 and min_required <= 12:
        return 107.91
    elif total_volume <= 20:
        return 129.31
    else:
        return 129.31 * math.ceil(total_volume / 20)

def distance_fee(distance_km: float) -> float:
    """Distance surcharge for km > 15."""
    return 0 if distance_km <= 15 else 2.6 * (distance_km - 15)

def geocode(address: str, api_key: str):
    """Geocode address using Google Maps API."""
    if not api_key or not address:
        return None, "API key or address missing"
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address.strip(),
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            formatted_address = result["formatted_address"]
            location = result["geometry"]["location"]
            return {
                "formatted_address": formatted_address,
                "lat": location["lat"],
                "lng": location["lng"]
            }, None
        elif data.get("status") == "ZERO_RESULTS":
            return None, f"No results found for address: {address}"
        elif data.get("status") == "REQUEST_DENIED":
            return None, "API request denied. Check your API key and billing settings."
        elif data.get("status") == "INVALID_REQUEST":
            return None, "Invalid request. Check the address format."
        elif data.get("status") == "OVER_QUERY_LIMIT":
            return None, "API quota exceeded. Please try again later."
        else:
            return None, f"Geocoding error: {data.get('status', 'Unknown error')}"
            
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def get_distance_km(origin_coords: dict, destination_coords: dict, api_key: str):
    """Get driving distance using Google Maps Distance Matrix API."""
    if not api_key or not origin_coords or not destination_coords:
        return None, "Missing required data"
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_coords['lat']},{origin_coords['lng']}",
        "destinations": f"{destination_coords['lat']},{destination_coords['lng']}",
        "mode": "driving",
        "units": "metric",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK":
            element = data["rows"][0]["elements"][0]
            
            if element.get("status") == "OK":
                distance_m = element["distance"]["value"]
                duration_s = element["duration"]["value"]
                distance_km = distance_m / 1000
                duration_min = duration_s / 60
                
                return {
                    "distance_km": distance_km,
                    "duration_min": duration_min,
                    "distance_text": element["distance"]["text"],
                    "duration_text": element["duration"]["text"]
                }, None
            elif element.get("status") == "NOT_FOUND":
                return None, "Route not found between the specified locations."
            elif element.get("status") == "ZERO_RESULTS":
                return None, "No route found between the locations."
            else:
                return None, f"Route calculation error: {element.get('status')}"
        else:
            return None, f"Distance Matrix API error: {data.get('status')}"
            
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def calculate_trucks(total_volume: float):
    """Determine optimal truck combination for total volume."""
    trucks = []
    remaining_volume = total_volume

    # Large trucks (20m³ each)
    while remaining_volume > 20:
        trucks.append(20)
        remaining_volume -= 20

    # Medium truck (20m³)
    if remaining_volume > 12:
        trucks.append(20)
        remaining_volume -= 20

    # Small truck (12m³)
    if remaining_volume > 0:
        trucks.append(12)
        remaining_volume -= 12

    return trucks

def truck_fee(total_volume: float):
    """Calculate total truck fee based on multiple trucks."""
    trucks = calculate_trucks(total_volume)
    fee = 0
    for vol in trucks:
        if vol <= 12:
            fee += 107.91
        else:
            fee += 129.31
    return fee, trucks
def create_breakdown_chart(breakdown_data):
    """Create a pie chart for price breakdown."""
    # Filter out zero values
    filtered_data = {k: v for k, v in breakdown_data.items() if v > 0}
    
    if not filtered_data:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=list(filtered_data.keys()),
        values=list(filtered_data.values()),
        hole=0.4,
        marker_colors=['#667eea', '#764ba2', '#28a745', '#ffc107']
    )])
    
    fig.update_layout(
        title="💰 Price Breakdown",
        font=dict(size=14),
        showlegend=True,
        height=400,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return fig

# ========= MAIN UI =========
# Header
st.markdown("""
<div class="main-header">
    <h1>🚚 Tictak Price Estimator</h1>
    <p>Get instant quotes for your moving and delivery needs</p>
</div>
""", unsafe_allow_html=True)

# API Key Configuration
st.markdown("### 🔑 Google Maps API Configuration")
with st.expander("**Configure Google Maps API Key**", expanded=not st.session_state.api_key):
    st.markdown("""
    <div class="api-key-container">
        <h4>⚠️ Google Maps API Key Required</h4>
        <p>To get accurate distance calculations and address validation, you need a Google Maps API key with the following APIs enabled:</p>
        <ul>
            <li><strong>Geocoding API</strong> - for address validation</li>
            <li><strong>Distance Matrix API</strong> - for distance calculation</li>
        </ul>
        <p><a href="https://console.cloud.google.com/apis/credentials" target="_blank">Get your API key here →</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key_input = st.text_input(
        "Enter your Google Maps API Key:",
        type="password",
        value=st.session_state.api_key,
        help="Your API key is stored securely in this session only"
    )
    
    if st.button("💾 Save API Key"):
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.success("✅ API key saved successfully!")
            st.rerun()
        else:
            st.error("❌ Please enter a valid API key")
    
    if not st.session_state.api_key:
        st.error("❌ Please configure your Google Maps API key to continue")
        st.stop()

# Initialize session state
if 'addresses_confirmed' not in st.session_state:
    st.session_state.addresses_confirmed = False
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = {}
if 'geocoded_addresses' not in st.session_state:
    st.session_state.geocoded_addresses = {}
if 'distance_data' not in st.session_state:
    st.session_state.distance_data = {}

# Sidebar for quick info
with st.sidebar:
    st.markdown("### 📊 Quick Info")
    st.info("💡 **Tip**: Confirm your addresses first, then select items for accurate pricing.")
    
    st.markdown("### 🚛 Truck Sizes")
    st.markdown("""
    - **Small (12m³)**: €107.91
    - **Medium (20m³)**: €129.31  
    - **Large (20m³+)**: €129.31 per 20m³
    """)
    
    st.markdown("### ⏰ Pricing Tiers")
    rates = {
        "1-5 items": "€2.00/min",
        "6-10 items": "€3.00/min", 
        "11-15 items": "€4.00/min",
        "16-20 items": "€5.50/min",
        "21-25 items": "€6.50/min",
        "25+ items": "€7.35+ /min"
    }
    for items, rate in rates.items():
        st.markdown(f"**{items}**: {rate}")
    
    if st.session_state.geocoded_addresses:
        st.markdown("### 📍 Current Addresses")
        if 'pickup' in st.session_state.geocoded_addresses:
            st.success(f"🏠 **Pickup**: ✅ Confirmed")
        if 'delivery' in st.session_state.geocoded_addresses:
            st.success(f"📦 **Delivery**: ✅ Confirmed")
        
        if st.session_state.distance_data:
            st.markdown("### 🛣️ Route Information")
            dist_data = st.session_state.distance_data
            st.info(f"**Distance**: {dist_data['distance_text']}\n\n**Duration**: {dist_data['duration_text']}")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    with st.expander("📍 **Delivery Addresses**", expanded=True):
        pickup = st.text_input("🏠 Pickup Address", placeholder="e.g., Paris, France or 123 Main St, City")
        delivery = st.text_input("📦 Delivery Address", placeholder="e.g., Nice, France or 456 Oak Ave, City")
        
        if st.button("✅ Confirm Addresses", type="primary"):
            if not pickup or not delivery:
                st.error("❌ Please enter both pickup and delivery addresses.")
            else:
                with st.spinner("🔍 Validating addresses and calculating distance..."):
                    # Geocode pickup address
                    pickup_result, pickup_error = geocode(pickup, st.session_state.api_key)
                    
                    if pickup_error:
                        st.error(f"❌ Pickup address error: {pickup_error}")
                    else:
                        # Geocode delivery address
                        delivery_result, delivery_error = geocode(delivery, st.session_state.api_key)
                        
                        if delivery_error:
                            st.error(f"❌ Delivery address error: {delivery_error}")
                        else:
                            # Calculate distance
                            distance_result, distance_error = get_distance_km(
                                pickup_result, delivery_result, st.session_state.api_key
                            )
                            
                            if distance_error:
                                st.error(f"❌ Distance calculation error: {distance_error}")
                            else:
                                # Store results in session state
                                st.session_state.geocoded_addresses = {
                                    'pickup': pickup_result,
                                    'delivery': delivery_result
                                }
                                st.session_state.distance_data = distance_result
                                st.session_state.addresses_confirmed = True
                                
                                # Display success message
                                st.success(f"✅ **Addresses Confirmed!**")
                                
                                # Display distance info
                                st.markdown(f"""
                                <div class="distance-info">
                                    <h4>📍 Validated Addresses:</h4>
                                    <p><strong>Pickup:</strong> {pickup_result['formatted_address']}</p>
                                    <p><strong>Delivery:</strong> {delivery_result['formatted_address']}</p>
                                    <h4>🛣️ Route Information:</h4>
                                    <p><strong>Distance:</strong> {distance_result['distance_text']} ({distance_result['distance_km']:.1f} km)</p>
                                    <p><strong>Estimated Duration:</strong> {distance_result['duration_text']}</p>
                                </div>
                                """, unsafe_allow_html=True)

with col2:
    with st.expander("⚙️ **Delivery Options**", expanded=True):
        col2a, col2b = st.columns(2)
        
        with col2a:
            floors_source = st.number_input("⬇️ Source Floors (Down)", min_value=0, value=0, help="Number of floors to carry items DOWN")
        
        with col2b:
            floors_dest = st.number_input("⬆️ Destination Floors (Up)", min_value=0, value=0, help="Number of floors to carry items UP")
        
        urgency = st.selectbox("🚀 Service Type", 
                              options=["PLANNED", "URGENT/Express"],
                              help="Express service costs 50% more")
        
        if urgency == "URGENT/Express":
            st.warning("⚡ **Express Service**: +50% surcharge applied")

# Items Selection
st.markdown("---")
with st.expander("📦 **Select Your Items**", expanded=True):
    st.markdown("### Choose items and quantities")
    
    # Create columns for item selection
    cols = st.columns(3)
    
    for i, (_, item) in enumerate(items_df.iterrows()):
        col_idx = i % 3
        
        with cols[col_idx]:
            # Create a card-like container
            with st.container():
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; border: 2px solid #e1e5e9; margin-bottom: 1rem;">
                    <h4 style="margin-bottom: 0.5rem; color: #333;">{item['key']}</h4>
                    <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                        📦 Volume: {item['volume']}m³<br>
                        ⏱️ Stair time: {item['stairTime']}s<br>
                        🚛 Min truck: {item['min_truck_size']}m³
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                quantity = st.number_input(
                    f"Quantity",
                    min_value=0, 
                    value=st.session_state.selected_items.get(item['key'], 0),
                    key=f"qty_{item['key']}",
                    help=f"Number of {item['key']} items"
                )
                
                if quantity > 0:
                    st.session_state.selected_items[item['key']] = quantity
                elif item['key'] in st.session_state.selected_items:
                    del st.session_state.selected_items[item['key']]

# Calculate Price Button
st.markdown("---")
if st.button("💰 **Calculate Price**", type="primary", use_container_width=True):
    if not st.session_state.addresses_confirmed:
        st.error("❌ Please confirm your addresses first.")
    elif not st.session_state.selected_items:
        st.error("❌ Please select at least one item.")
    elif not st.session_state.distance_data:
        st.error("❌ Distance data not available. Please confirm addresses again.")
    else:
        with st.spinner("🧮 Calculating your quote..."):
            # Get distance from stored data
            distance_km = st.session_state.distance_data['distance_km']
            
            # Calculate totals
            total_volume = sum(
                items_df.loc[items_df["key"] == k, "volume"].iloc[0] * q
                for k, q in st.session_state.selected_items.items()
            )
            total_items = sum(st.session_state.selected_items.values())
            stair_minutes = sum(
                items_df.loc[items_df["key"] == k, "stairTime"].iloc[0] * q
                for k, q in st.session_state.selected_items.items()
            ) / 60.0
            

            # NEW SMART LOGIC:
            base_truck_fee, truck_list = truck_fee(total_volume)
            truck_size_label = " + ".join([f"{t}m³" for t in truck_list])

            # Display truck info
            st.markdown(f"### 🚛 Truck & Volume Info")
            st.info(f"**Total Volume:** {total_volume:.1f} m³\n**Trucks Used:** {truck_size_label}")
            
           # Calculate fees

            # 1️⃣ Rate per minute
            r = rate_per_minute(total_items)

            # 2️⃣ Smart truck fee
            base_truck_fee, truck_list = truck_fee(total_volume)
            truck_size_label = " + ".join([f"{t}m³" for t in truck_list])

            # 3️⃣ Distance fee
            dist_fee = distance_fee(distance_km)

            # 4️⃣ Handling fee (stairs + floors)
            handling_fee = r * stair_minutes * (1 + floors_source + 1.2 * floors_dest)

            # 5️⃣ Urgency multiplier
            urgency_mult = 1.5 if urgency == "URGENT/Express" else 1.0

            # 6️⃣ Total price
            total_price = urgency_mult * (base_truck_fee + dist_fee + handling_fee)
            
            st.info(f"======================>{r * stair_minutes}")

           

            
            # Display results
            st.markdown("---")
            st.markdown("## 📊 **Your Quote Results**")
            
            # Main price display
            st.markdown(f"""
            <div class="price-display">
                <div class="price-label">Estimated Total Price</div>
                <div class="price-amount">€{total_price:.2f}</div>
                <div style="font-size: 1rem; opacity: 0.8;">
                    {urgency} • {total_items} items • {distance_km:.1f}km
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🚛 Truck Fee", f"€{base_truck_fee:.2f}", 
                         help=f"Based on {total_volume:.1f}m³ volume")
            
            with col2:
                st.metric("🛣️ Distance Fee", f"€{dist_fee:.2f}", 
                         help=f"For {distance_km:.1f}km distance (>15km surcharge)")
            
            with col3:
                st.metric("👥 Handling Fee", f"€{handling_fee:.2f}", 
                         help=f"Based on stairs and {stair_minutes:.1f} min")
            
            with col4:
                urgency_fee = total_price - (base_truck_fee + dist_fee + handling_fee)
                st.metric("⚡ Urgency Fee", f"€{urgency_fee:.2f}", 
                         help=f"{urgency_mult}x multiplier")
            
            # Detailed breakdown
            st.markdown("### 📋 **Detailed Breakdown**")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                breakdown_data = {
                    "Truck Fee": base_truck_fee,
                    "Distance Fee": dist_fee,
                    "Handling Fee": handling_fee,
                    "Urgency Surcharge": urgency_fee
                }
                
                fig = create_breakdown_chart(breakdown_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**📦 Selected Items:**")
                for item_key, qty in st.session_state.selected_items.items():
                    item_data = items_df.loc[items_df["key"] == item_key].iloc[0]
                    st.markdown(f"• **{qty}x** {item_key}")
                    st.caption(f"   Volume: {item_data['volume'] * qty:.1f}m³")
                
                st.markdown("**📍 Route Details:**")
                dist_data = st.session_state.distance_data
                st.markdown(f"• **Distance**: {distance_km:.1f} km")
                st.markdown(f"• **Source floors**: {floors_source}")
                st.markdown(f"• **Destination floors**: {floors_dest}")
                st.markdown(f"• **Rate**: €{r:.2f}/min")
                st.markdown(f"• **Stair time**: {stair_minutes:.1f} min")
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666; font-size: 0.9rem;">
    <p>🚚 <strong>Tictak Price Estimator</strong> | Built with Streamlit</p>
    <p>💡 Prices are estimates and may vary based on actual conditions</p>
</div>
""", unsafe_allow_html=True)