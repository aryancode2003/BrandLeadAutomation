import streamlit as st
import pandas as pd
import io
import os
import time
import json
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION (Must be first)
# ==========================================
st.set_page_config(page_title="Multi-Brand Lead Portal", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# ADVANCED UI/UX CSS INJECTION 
# ==========================================
st.markdown("""
    <style>
    /* Global App Background and Text Reset */
    .stApp { background-color: #F4F6F9; font-family: 'Inter', sans-serif; color: #1E1E2D; }
    
    /* Ensure all main area headings are visible and dark */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #1E1E2D !important; font-weight: 700; }
    
    /* Dark Modern Sidebar */
    [data-testid="stSidebar"] { background-color: #1A1A27; }
    [data-testid="stSidebar"] * { color: rgba(255, 255, 255, 0.85) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    
    /* Hide Default Headers */
    header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Brand Selection Cards */
    .brand-card {
        background: white; border-radius: 12px; padding: 2rem; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04); transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 2px solid transparent; cursor: pointer; margin-bottom: 1rem;
    }
    .brand-card:hover { transform: translateY(-4px); box-shadow: 0 12px 25px rgba(54,153,255,0.15); border-color: #3699FF; }
    .brand-title { font-size: 1.6rem; font-weight: 800; color: #1E1E2D !important; margin-bottom: 0.3rem; }
    
    /* Login Container */
    .login-container { max-width: 400px; margin: 3rem auto; padding: 2.5rem; background: white; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.05); }
    
    /* Primary Gradient Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3699FF 0%, #2084EB 100%);
        color: white !important; border-radius: 8px; font-weight: 600; border: none; padding: 0.6rem 2rem;
        box-shadow: 0 4px 10px rgba(54, 153, 255, 0.25); transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(54, 153, 255, 0.35); }
    
    /* Outline Buttons */
    .btn-outline>button { background: transparent !important; color: #1E1E2D !important; border: 1px solid #E4E6EF !important; box-shadow: none !important; }
    .btn-outline>button:hover { background: #F3F6F9 !important; border-color: #B5B5C3 !important; }
    
    /* Metric Cards Fix */
    .metric-card {
        background: #FFFFFF; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid #E4E6EF; border-left: 5px solid #3699FF; margin-bottom: 1.5rem;
    }
    .metric-card h3 { color: #7E8299 !important; font-size: 0.9rem; margin-bottom: 0.4rem; text-transform: uppercase; font-weight: 700;}
    .metric-card h2 { color: #1E1E2D !important; font-size: 2.4rem; font-weight: 800; margin: 0; line-height: 1;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. FILE SYSTEM & DATABASE SETUP
# ==========================================
CONFIG_FILE = "brands_config.json"
LOG_FILE = "usage_logs.csv"

# SET YOUR PASSWORDS HERE
USER_DATABASE = {
    "aryan@jungleworks.com": {"password": "admin", "role": "superadmin", "brand": "ALL"},
    "aryan.srivastava@jungleworks.com": {"password": "Fatafat123", "role": "user", "brand": "FATAFAT"},
    "anshul.mehra@jungleworks.com": {"password": "Jugnoo123", "role": "user", "brand": "JUGNOO"},
    "spark@brand.com": {"password": "123", "role": "user", "brand": "SPARK STUDIO"}
}

DEFAULT_BRANDS = {
    "FATAFAT": {
        "name": "FATAFAT", 
        "lost_cities": [
            "Adipur", "Agartala", "Ahmedabad", "Akola", "Aligarh", "Alipurduar", "Alwar", "Ambejogai", 
            "Amravati", "Amritsar", "Asansol", "Ashoka Nagar", "Ashta", "Azamgarh", "Baddi", "Bahraich", 
            "Balasore", "Ballari", "Banka", "Bardhaman", "Baripada", "Basti", "Bazpur", "Beawar", "Betul", 
            "Bhaderwah", "Bhagalpur", "Bhandara", "Bhiwani", "Bilaspur", "Bishanpura", "Brahmapur", "Burhar", 
            "Chamba", "Chanchal", "Chunar", "Coimbatore", "Contai", "Cuttack", "Daltonganj", "Darbhanga", 
            "Dewas", "Dharamshala", "Dharmanagar", "Dimapur", "Dinhata", "Doda", "Dumka", "Durgapur", "Erode", 
            "Faridabad", "Faridkot", "Farrukhabad", "Fatehgarh", "Firozabad", "Ganderbal", "Gandhidham", "Gondia", 
            "Gora Bazar", "Guntur", "Gurugram", "Guruvayur", "Gwalior", "Hailakandi", "Hamirpur", "Haridwar", 
            "Hazaribagh", "Hyderabad", "Imphal", "Islampur", "Jagadhri", "Jaisalmer", "Jalandhar", "Jammu", 
            "Jamshedpur", "Jangipur", "Jhunjhunu", "Jodhpur", "Jorhat", "Kadapa", "Kakinada", "Kalyan", "Kangra", 
            "Karimnagar", "Karnal", "Kathua", "Keonjhar", "KGF", "Khordha", "Kishanganj", "Kishangarh", "Kot Kapura", 
            "Kumarghat", "Kunda", "Kurukshetra", "Lakhimpur Kheri", "Latur", "Ludhiana", "Madurai", "Mahendragarh", 
            "Maheshwarpur", "Mahoba", "Malda", "Manali", "Manawar", "Manipal", "Mau", "Meerut", "Midnapore", 
            "Mohali", "Moradabad", "Motihari", "Nagpur", "Navi Mumbai", "Nimbahera", "Noida", "Nuh", "Orai", 
            "Outer Ahmedabad", "Outer Patna", "Pali", "Panipat", "Paonta Sahib", "Pathankot", "Patna", 
            "Perinthalmanna", "Phalodi", "Port Blair", "Prakasam", "Prayagraj", "Puducherry", "Pune", "Puri", 
            "Rampur", "Rampurhat", "Ranchi", "Rawatbhata", "Reasi", "Robertsganj", "Rohini", "Rohru", "Roorkee", 
            "Sangareddy", "Sangli", "Saraipali", "Sasaram", "Shahdol", "Shahjahanpur", "Shamli", "Shimla", 
            "Shivpuri", "Shujalpur", "Silchar", "Siliguri", "Singhana", "Singur", "Sirohi", "Sirsa", "Solan", 
            "Solapur", "Sonipat District", "Srinagar", "Sundernagar", "Suri", "Tarn Taran", "Tezpur", "Thane", 
            "Tinsukia", "Umarkhed", "Una", "Unnao", "Vadodara", "Waidhan", "Yamunanagar"
        ]
    },
    "JUGNOO": {
        "name": "JUGNOO", 
        "lost_cities": [
            "Vadodara", "Guwahati", "Jaipur", "Srinagar", "Nagercoil", "Bhopal", "Ludhiana", "Faridabad", "Chandigarh", "Mohali", 
            "Sagar", "Rewa", "Dewas", "Kanniyakumari", "Mau", "Raipur", "Daman", "Vapi", "Nagpur", "Rajkot", "Bijnor", "Meerut", 
            "Muzaffarnagar", "Coimbatore", "Deoghar", "Lucknow", "Kanpur", "Pune", "Gorakhpur", "Kalaburagi", "Barabanki", "Ratlam", 
            "Kozhikode", "Betul", "Chhindwara", "Dharmanagar", "Thucklay", "Padmanabhapuram", "Marthandam", "Derabassi", "Durgapur", 
            "Kharar", "Pinjore", "Koraput", "Navi Mumbai", "Kollam", "Sumerpur", "Nagaon", "Balaghat", "Rudrapur", "Una", "Baddi", 
            "Shimla", "Thrissur", "Cooch Bihar", "Imphal", "Dharamshala", "Manali", "Gondia", "Ernakulam", "Kodagu", "Dindigul", 
            "Patiala", "Barwani", "Dhar", "Dhanbad", "Chapra", "Waidan", "Bidar", "Kamareddy", "Nanded", "Pathankot", "Hajipur", 
            "Goalpara", "Balasore", "Puri", "Karimnagar", "Hassan", "Ahmedabad", "Baripada", "Kannur", "Shamli", "Mirzapur", "Jaunpur", 
            "Bhadohi", "Tuticorin", "Ramanathapuram", "Thoubal", "Karimganj", "Doddaballapura", "Nandi Hills", "Godda", "Delhi", 
            "New Delhi", "Gurgaon", "Gurugram", "Noida", "Greater Noida", "Baleswar", "Belgaum", "Calicut", "Midnapore", "Daltonganj", 
            "Barotiwala", "Nalagarh", "Hyderabad", "Bangalore", "Chennai", "Kolkata", "Bengaluru", "Mumbai", "Shahdol", "Kottayam", 
            "Dehri-on-Sone", "Ghaziabad", "Kamrup", "Madanapalle", "Aizawl", "Udaipur", "Narmadapuram", "Bathinda", "Jalgaon", 
            "Waidhan", "Biswanath", "Bandikui", "Ganjam", "Bareilly", "Dhemaji", "Bahraich", "Bhuj", "Gandhidham", "Kutch", "Dhubri", 
            "Kohima", "Nalanda", "Dinhata", "Beawar", "Sitamarhi", "Alipurduar", "Hazaribagh", "Barbil", "Ballia", "Joda", "Bhubaneswar", 
            "Bhadrak", "Palamu", "Mathura", "Vrindavan", "Basti", "Saharsa", "Tarn Taran", "Madurai", "Orai", "Rajouri", "Begusarai", 
            "Kushinagar", "Khatu Shyam", "Dombivli", "Gwalior", "Satara", "Sundar Nagar", "Singrauli", "Surat", "Vikasnagar", "Dimapur", 
            "Rapar", "Katihar", "Vijayapura", "Ajmer", "Gir Somnath", "Moga", "Jharsuguda", "Dwarka", "Madhubani", "Jaisalmer", 
            "Gulbarga", "Huancayo", "Bharuch", "Khanna", "Morbi", "Indore", "Ankleshwar", "Bankura", "Purulia", "Murshidabad", "Haridwar", 
            "Raiganj", "Dalkhola", "Asansol", "Sri Muktsar Sahib", "Bhavnagar", "Malerkotla", "Sangrur", "Barnala", "Raichur", "Palghar", 
            "Vasai", "Dungarpur", "Champawat", "Khatima", "Malviya Nagar", "Arambagh", "Harda", "Gandhinagar", "Hosur", "Naharlagun", 
            "Kishtwar", "Doda", "Ambikapur", "Dar es Salaam", "Ziro", "Malegaon", "Dhule", "Aurangabad", "Bikaner", "Roorkee", 
            "Kharagpur", "Prakasam", "Udgir", "Hojai", "Jalore", "Bhinmal", "Gangapur", "Sonipat", "Addanki", "Saket", "New Town", 
            "Jabalpur", "Kandukur", "Chimakurthi", "Tangutur", "Kothapatnam", "Ahore", "Sayla", "Lanka", "Itanagar", "Kolhapur", 
            "Belagavi", "Jamshedpur", "Dausa", "Karauli", "Rishikesh", "Tirupati", "Secunderabad", "Jaleswar", "Purnia", "Sangli", 
            "Junagadh", "Jhargram", "Godhra", "Bilaspur", "Medchal-Malkajgiri", "Kanyakumari", "Umaria", "Panipat", "Varanasi", 
            "Ayodhya", "Haldia", "Khordha", "Bagodar"
        ]
    },
    "SOLO BEAUTY": {"name": "SOLO BEAUTY", "lost_cities": [
        "Hozabad", "Deoria", "Rajkot", "Ajmer", "Udham Singh Nagar", "Rudrapur", "Nagpur", "Bhopal", "Navi Mumbai", "Panipat", "Bhubaneswar", "Gwalior", "Jammu", "Ghaziabad", "Agra", "Jabalpur", "Mathura", "Jalandhar", "Noida", "Secunderabad", "Muzaffarpur", "Asansol", "Silchar", "Mandi", "Ayodhya", "Balasore", "Zirakpur", "Patna", "Etawah", "Kolkata", "South Kolkata", "East Kolkata", "Pune", "Vadodara", "Vijayawada", "Allahabad", "Muzaffarnagar", "Lucknow", "Varanasi", "Jodhpur", "Indore", "Udaipur", "Guntur", "Gorakhpur", "Kashipur", "Gurgaon", "Amritsar", "Hyderabad", "Jaipur", "Kanpur", "Bhagalpur", "Sonipat", "Ahmedabad", "Orai", "Bharatpur", "Firozabad", "Vapi"
    ]}
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f: json.dump(DEFAULT_BRANDS, f, indent=4)

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Timestamp", "User_Email", "Brand", "Action", "Total_Leads", "File_Name"]).to_csv(LOG_FILE, index=False)

def load_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f: json.dump(data, f, indent=4)

def log_activity(email, brand, action, leads_count, file_name):
    new_log = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User_Email": email, "Brand": brand, "Action": action,
        "Total_Leads": leads_count, "File_Name": file_name
    }])
    new_log.to_csv(LOG_FILE, mode='a', header=False, index=False)

brand_configs = load_config()

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'step' not in st.session_state: st.session_state.step = "brand_selection"
if 'selected_brand' not in st.session_state: st.session_state.selected_brand = ""
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = ""

# ==========================================
# STEP 1: BRAND SELECTION SCREEN
# ==========================================
if st.session_state.step == "brand_selection":
    st.markdown("<h1 style='text-align:center; margin-top:3rem;'>⚡ Select Your Workspace</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7E8299; margin-bottom:3rem;'>Choose a brand portal to continue</p>", unsafe_allow_html=True)
    
    brands_list = list(brand_configs.keys())
    cols = st.columns(len(brands_list))
    
    for idx, brand in enumerate(brands_list):
        with cols[idx]:
            st.markdown(f"<div class='brand-card'><div class='brand-title'>{brand}</div><span style='color:#7E8299;'>Lead Engine</span></div>", unsafe_allow_html=True)
            if st.button(f"Enter {brand}", key=f"btn_{brand}", use_container_width=True):
                st.session_state.selected_brand = brand
                st.session_state.step = "login"
                st.rerun()
    st.stop()

# ==========================================
# STEP 2: LOGIN SCREEN
# ==========================================
elif st.session_state.step == "login":
    brand = st.session_state.selected_brand
    st.markdown(f"<h1 style='text-align:center; margin-top:2rem;'>{brand} Portal</h1>", unsafe_allow_html=True)
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("### 🔐 Secure Login")
        email_input = st.text_input("Email Address")
        password_input = st.text_input("Password", type="password")
        if st.form_submit_button("Authenticate", use_container_width=True):
            if email_input in USER_DATABASE and USER_DATABASE[email_input]["password"] == password_input:
                user_brand = USER_DATABASE[email_input]["brand"]
                if user_brand == brand or user_brand == "ALL":
                    st.session_state.logged_in, st.session_state.user_email, st.session_state.user_role = True, email_input, USER_DATABASE[email_input]["role"]
                    st.session_state.step = "main_portal"
                    log_activity(email_input, brand, "Logged In", 0, "N/A")
                    st.rerun()
                else: st.error(f"Access Denied: Not authorized for {brand}.")
            else: st.error("Invalid credentials.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='btn-outline' style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("← Back to Workspaces"):
        st.session_state.step, st.session_state.selected_brand = "brand_selection", ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# STEP 3: MAIN PORTAL & DYNAMIC LOGIC ENGINES
# ==========================================
elif st.session_state.step == "main_portal":
    active_brand = st.session_state.selected_brand
    brand_data = brand_configs.get(active_brand, DEFAULT_BRANDS["FATAFAT"])

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h1 style='text-align:center; color:#3699FF !important; font-size:2.2rem;'>{active_brand}</h1>", unsafe_allow_html=True)
        if st.session_state.user_role == "superadmin":
            st.divider()
            st.markdown("🛠️ **Super Admin Actions**")
            new_brand = st.selectbox("Quick Switch:", list(brand_configs.keys()), index=list(brand_configs.keys()).index(active_brand))
            if new_brand != active_brand:
                st.session_state.selected_brand = new_brand
                st.rerun()
                
        st.divider()
        st.markdown(f"👤 **{st.session_state.user_email}**\n\n🛡️ **{st.session_state.user_role.upper()}**")
        st.markdown("<div class='btn-outline'>", unsafe_allow_html=True)
        if st.button("🔄 Change Workspace", use_container_width=True):
            st.session_state.step, st.session_state.logged_in = "brand_selection", False
            st.rerun()
        st.markdown("</div><br>", unsafe_allow_html=True)
        if st.button("🚪 Secure Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- TABS ---
    st.markdown(f"<h1>{active_brand} Operations</h1>", unsafe_allow_html=True)
    if st.session_state.user_role == "superadmin":
        tab_proc, tab_brand_mgr, tab_logs = st.tabs(["📊 Lead Engine", "⚙️ Brand Settings", "📈 Global Logs"])
    else:
        tab_proc, = st.tabs(["📊 Lead Engine"])

    # --- TAB 1: PROCESSOR ---
    with tab_proc:
        
        with st.expander("📝 View / Edit Active Sold-Out Cities for this Upload"):
            joined_cities = ", ".join(brand_data["lost_cities"])
            st.info("💡 You can manually add or remove cities here before uploading your file. It will only apply to this session.")
            live_cities_input = st.text_area("Live Database Grid (Comma Separated):", value=joined_cities, height=150)
            
        active_lost_set = {c.strip().lower() for c in live_cities_input.split(",") if c.strip()}

        uploaded_file = st.file_uploader(f"Upload Raw Leads for {active_brand}", type=["csv", "txt"])

        if uploaded_file is not None:
            try:
                with st.spinner("Executing Brand-Specific Logic..."):
                    try:
                        df = pd.read_csv(uploaded_file, sep='\t', encoding='utf-16')
                    except UnicodeError:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, sep='\t', encoding='utf-8')
                    except Exception:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file)
                    
                    df.columns = df.columns.str.lower().str.strip()

                    df_transformed = pd.DataFrame()
                    df_transformed['City'] = df['city'] if 'city' in df.columns else ""
                    df_transformed['Country'] = 'India'
                    df_transformed['Contact Name'] = df['full_name'] if 'full_name' in df.columns else ""
                    df_transformed['Contact Email'] = df['email'] if 'email' in df.columns else ""
                    
                    if 'phone_number' in df.columns:
                        cleaned_phones = df['phone_number'].astype(str).str.replace(r'\D', '', regex=True)
                        df_transformed['Contact Phone Number'] = cleaned_phones.apply(lambda x: f"{x}" if pd.notnull(x) else "")
                    elif 'phone' in df.columns:
                        cleaned_phones = df['phone'].astype(str).str.replace(r'\D', '', regex=True)
                        df_transformed['Contact Phone Number'] = cleaned_phones.apply(lambda x: f"{x}" if pd.notnull(x) else "")
                    else:
                        df_transformed['Contact Phone Number'] = ""
                    
                    df_transformed['Deal Owner Email ID'] = 'anshul.mehra@jungleworks.com'
                    df_transformed['Pipeline'] = active_brand 
                    df_transformed['Tags'] = 'Brands-Franchise'
                    df_transformed['Deal Status'] = 'Open'

                    # =====================================
                    # DYNAMIC BRAND LOGIC BRANCHING
                    # =====================================
                    if active_brand == "FATAFAT":
                        def determine_utm_fatafat(row):
                            val = str(row.iloc[12]).lower() + " " + str(row.iloc[13]).lower() if len(row) > 13 else ""
                            return 'as_a_delivery_boy' if any(k in val for k in ['driver', 'merchant', 'driving', 'job', 'delivery']) else 'as_a_franchise_owner'
                        df_transformed['Utm Content'] = df.apply(determine_utm_fatafat, axis=1)
                        if 'full_name' in df.columns: df_transformed['Note'] = 'Join ' + df_transformed['Utm Content'] + ' in ' + df['full_name'].astype(str)
                        if 'platform' in df.columns: df_transformed['Source'] = df['platform'].map({'fb': 'Facebook', 'ig': 'Instagram'}).fillna('Other')
                        df_transformed['investment'] = ''

                    elif active_brand == "JUGNOO":
                        def determine_utm_jugnoo(row):
                            # Bulletproof: Scans BOTH Column M (12) and Column N (13) simultaneously
                            val_m = str(row.iloc[12]).lower() if len(row) > 12 else ""
                            val_n = str(row.iloc[13]).lower() if len(row) > 13 else ""
                            combined_vals = val_m + " " + val_n
                            
                            # If they mention driver, merchant, delivery, or job ANYWHERE in those columns
                            if any(k in combined_vals for k in ['driver', 'merchant', 'driving', 'job', 'delivery']):
                                return 'as_a_delivery_boy'
                            
                            # Otherwise, they are a franchise owner
                            return 'as_a_franchise_owner'
                            
                        df_transformed['Utm Content'] = df.apply(determine_utm_jugnoo, axis=1)
                        if 'full_name' in df.columns: df_transformed['Note'] = 'Want to join ' + df_transformed['Utm Content'] + ' in ' + df['full_name'].astype(str)
                        df_transformed['Source'] = 'Facebook' 
                        df_transformed['investment'] = df.iloc[:, 13].astype(str) if df.shape[1] > 13 else ""
                            
                        df_transformed['Utm Content'] = df.apply(determine_utm_jugnoo, axis=1)
                        if 'full_name' in df.columns: df_transformed['Note'] = 'Want to join ' + df_transformed['Utm Content'] + ' in ' + df['full_name'].astype(str)
                        df_transformed['Source'] = 'Facebook' 
                        df_transformed['investment'] = df.iloc[:, 13].astype(str) if df.shape[1] > 13 else ""

                    elif active_brand == "SPARK STUDIO":
                        df_transformed['Utm Content'] = 'as_a_franchise_owner'
                        df_transformed['Note'] = 'Spark Studio Lead'
                        df_transformed['Source'] = 'Other'
                        df_transformed['investment'] = ''
                    # =====================================

                    def determine_stage(row, lost_set):
                        raw_city = str(row['City']).strip().lower()
                        if row['Utm Content'] == 'as_a_delivery_boy': return 'Driver/Merchant'
                        if raw_city in lost_set or raw_city.split('(')[0].strip() in lost_set: return 'Lost'
                        return 'Fresh Lead'
                        
                    df_transformed['Stage'] = df_transformed.apply(lambda r: determine_stage(r, active_lost_set), axis=1)
                    
                    cols = ['Country', 'City', 'Contact Name', 'Contact Email', 'Contact Phone Number', 
                            'Deal Owner Email ID', 'Pipeline', 'Stage', 'Tags', 'Deal Status', 
                            'Note', 'Source', 'Utm Content', 'investment']
                    df_transformed = df_transformed[cols]

                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                with m_col1: st.markdown(f"<div class='metric-card'><h3>👥 Total Leads</h3><h2>{len(df_transformed)}</h2></div>", unsafe_allow_html=True)
                with m_col2: st.markdown(f"<div class='metric-card'><h3>🏢 Fresh Leads</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Fresh Lead'])}</h2></div>", unsafe_allow_html=True)
                with m_col3: st.markdown(f"<div class='metric-card'><h3>🛵 Delivery</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Driver/Merchant'])}</h2></div>", unsafe_allow_html=True)
                with m_col4: st.markdown(f"<div class='metric-card'><h3>🛑 Auto-Lost</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Lost'])}</h2></div>", unsafe_allow_html=True)

                st.dataframe(df_transformed, use_container_width=True, height=250)
                
                st.download_button(
                    label=f"📥 Download {active_brand} CSV",
                    data=df_transformed.to_csv(index=False, encoding='utf-8'),
                    file_name=f"{active_brand}_Leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    on_click=log_activity,
                    args=(st.session_state.user_email, active_brand, "Processed CSV", len(df_transformed), uploaded_file.name)
                )
            except Exception as e:
                st.error(f"Processing Error: Please verify this is a valid {active_brand} raw file. Details: {e}")

    # --- TAB 2: BRAND MANAGER (SUPERADMIN) ---
    if st.session_state.user_role == "superadmin":
        with tab_brand_mgr:
            st.markdown(f"### Manage Rules for **{active_brand}**")
            st.warning("Updates made here will permanently save to the database.")
            current_cities_str = ", ".join(brand_configs[active_brand]["lost_cities"])
            updated_cities = st.text_area("Master Sold-Out Cities Database", value=current_cities_str, height=200)
            if st.button(f"💾 Permanently Save {active_brand} Rules"):
                brand_configs[active_brand]["lost_cities"] = [c.strip() for c in updated_cities.split(",") if c.strip()]
                save_config(brand_configs)
                log_activity(st.session_state.user_email, active_brand, "Updated Brand Cities", 0, "N/A")
                st.success(f"{active_brand} successfully updated!")
                st.rerun()

    # --- TAB 3: GLOBAL LOGS (SUPERADMIN) ---
    if st.session_state.user_role == "superadmin":
        with tab_logs:
            st.markdown("### 🌍 Global Audit Master Log")
            try:
                logs_df = pd.read_csv(LOG_FILE).sort_values(by="Timestamp", ascending=False).reset_index(drop=True)
                st.dataframe(logs_df, use_container_width=True)
            except Exception as e:
                st.error("No logs generated yet.")
