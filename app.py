import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. การตั้งค่าหน้าจอแอปพลิเคชัน (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="Solar ROI Calculator | ติดโซลาร์เซลล์ที่บ้านคุ้มไหม?",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 1.1 สไตล์ Responsive (มือถือ / iPad / Desktop)
# ==========================================
# - ไม่ใช้ Sidebar เพราะบนมือถือ Sidebar จะถูกซ่อน ผู้ใช้ทั่วไปอาจหาช่องกรอกไม่เจอ
# - st.columns จะเรียงเป็นแนวตั้งอัตโนมัติเมื่อจอแคบกว่า ~640px
# - การ์ดผลลัพธ์ใช้ CSS Grid: Desktop 4 คอลัมน์ / iPad 2 คอลัมน์ / มือถือ 2 หรือ 1 คอลัมน์
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap');

html, body, .stApp, .stMarkdown, p, label, input, textarea, button, h1, h2, h3, h4 {
    font-family: 'Noto Sans Thai', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp {
    background:
        radial-gradient(1100px 600px at 0% -10%, rgba(245,158,11,.16), transparent 60%),
        radial-gradient(900px 500px at 110% 0%, rgba(34,197,94,.10), transparent 60%),
        #0b1120;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem; }

/* ป้องกัน iPhone ซูมหน้าจอเองเมื่อแตะช่องกรอก (ต้องใช้ตัวอักษร >= 16px) */
input, textarea, select { font-size: 16px !important; }

/* ---------- Hero ---------- */
.hero { margin-bottom: 1.4rem; animation: fadeUp .6s ease both; }
.hero-badge {
    display: inline-block; padding: .3rem .8rem; border-radius: 999px;
    background: rgba(245,158,11,.12); border: 1px solid rgba(245,158,11,.35);
    color: #fbbf24; font-size: .85rem; font-weight: 600;
}
.hero h1 {
    font-size: clamp(1.7rem, 3.5vw + .6rem, 2.9rem); line-height: 1.3;
    margin: .6rem 0 .4rem; padding: 0; font-weight: 700;
    background: linear-gradient(90deg, #fef3c7, #f59e0b 60%, #fb923c);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: #cbd5e1; font-size: clamp(.95rem, .6vw + .8rem, 1.1rem); max-width: 760px; margin: 0; }
.hero [data-testid="stHeaderActionElements"] { display: none; }

/* ---------- KPI cards ---------- */
.kpi-grid {
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem; margin: .4rem 0 1.6rem;
}
.kpi {
    position: relative; overflow: hidden;
    background: linear-gradient(160deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(148,163,184,.16); border-radius: 18px;
    padding: 1.15rem 1.2rem; animation: fadeUp .5s ease both;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.kpi:hover { transform: translateY(-3px); border-color: rgba(245,158,11,.55); box-shadow: 0 10px 30px -12px rgba(245,158,11,.35); }
.kpi.good { border-color: rgba(34,197,94,.45); }
.kpi-icon { font-size: 1.35rem; }
.kpi-label { color: #94a3b8; font-size: .88rem; margin-top: .25rem; }
.kpi-value { color: #f8fafc; font-size: 1.85rem; font-weight: 700; line-height: 1.25; margin: .15rem 0; word-break: break-word; }
.kpi-value span { font-size: .95rem; font-weight: 500; color: #cbd5e1; margin-left: .2rem; }
.kpi.good .kpi-value { color: #4ade80; }
.kpi-sub { color: #94a3b8; font-size: .8rem; line-height: 1.4; }
.kpi:nth-child(2) { animation-delay: .05s; } .kpi:nth-child(3) { animation-delay: .1s; } .kpi:nth-child(4) { animation-delay: .15s; }

/* ---------- Location pill ---------- */
.psh-pill {
    display: flex; align-items: center; gap: .7rem; margin-top: .6rem;
    padding: .75rem 1rem; border-radius: 14px;
    background: linear-gradient(90deg, rgba(245,158,11,.14), rgba(245,158,11,.04));
    border: 1px solid rgba(245,158,11,.3); color: #fde68a; font-size: .92rem;
}
.psh-pill b { color: #fff; font-size: 1.15rem; }

/* ---------- Buttons ---------- */
.stDownloadButton button { min-height: 48px; border-radius: 12px; font-weight: 600; }

/* ---------- Tablet (iPad) ---------- */
@media (max-width: 1024px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .block-container { padding-left: 1.5rem; padding-right: 1.5rem; }
}
/* ---------- Mobile ---------- */
@media (max-width: 640px) {
    .block-container { padding: 1rem .85rem 3rem; }
    .kpi-grid { gap: .6rem; }
    .kpi { padding: .85rem .9rem; border-radius: 14px; }
    .kpi-value { font-size: 1.35rem; }
    .kpi-value span { font-size: .8rem; }
    .kpi-sub { font-size: .74rem; }
}
@media (max-width: 360px) {
    .kpi-grid { grid-template-columns: 1fr; }
}
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
</style>
""")

# ==========================================
# 2. ฟังก์ชันดึงข้อมูลจาก API (NASA POWER API)
# ==========================================
# ใช้ @st.cache_data เพื่อเก็บข้อมูลไว้ในหน่วยความจำแคช 
# ช่วยลดภาระการร้องขอข้อมูลซ้ำซ้อนเมื่อผู้ใช้เลื่อน Slider และลดปัญหา Rate Limit จาก API
@st.cache_data(ttl=3600)
def fetch_nasa_psh(lat, lon):
    """
    ฟังก์ชันสำหรับดึงค่าความเข้มแสงอาทิตย์ (Solar Irradiance / PSH) จากระบบ NASA POWER
    โดยใช้พารามิเตอร์ ALLSKY_SFC_SW_DWN ในรูปแบบ Climatology (ค่าเฉลี่ยระยะยาว)
    เพื่อประเมินศักยภาพการผลิตไฟฟ้าเฉลี่ยรายปีที่แม่นยำ
    """
    try:
        # กำหนด Endpoint URL สำหรับดึงข้อมูลจากดาวเทียม
        url = (
            f"https://power.larc.nasa.gov/api/temporal/climatology/point"
            f"?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}&format=JSON"
        )
        
        # กำหนด Timeout 10 วินาที เพื่อสร้างกลไกป้องกันแอปพลิเคชันค้าง (Graceful Degradation)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # สกัดค่าเฉลี่ยรายปี (ANN = Annual) ออกจากโครงสร้าง JSON แบบลำดับชั้น
            annual_psh = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']['ANN']
            return annual_psh
        else:
            # ใช้ค่า Default หากเซิร์ฟเวอร์ตอบกลับรหัสข้อผิดพลาด
            return 4.5
    except Exception as e:
        # ใช้ค่า Default หากการเชื่อมต่อล้มเหลว (เช่น ขาดการเชื่อมต่ออินเทอร์เน็ต)
        return 4.5

# ==========================================
# 2.1 ข้อมูลจังหวัด/อำเภอ และตัวช่วยประเมินการใช้ไฟกลางวัน
# ==========================================
# ไฟล์ CSV เก็บพิกัดจุดศูนย์กลางของทั้ง 928 อำเภอ/เขต ใน 77 จังหวัด
# (คำนวณล่วงหน้าจากขอบเขตอำเภอของ OpenGISData-Thailand จึงไม่ต้องเรียกบริการแปลงที่อยู่เป็นพิกัดตอนใช้งาน)
DISTRICTS_CSV = Path(__file__).parent / "data" / "thai_districts.csv"

@st.cache_data
def load_districts():
    return pd.read_csv(DISTRICTS_CSV)

# ตัวเลือกการเปิดแอร์ตอนกลางวัน -> สัดส่วนที่บวกเพิ่ม (แอร์คือเครื่องใช้ไฟฟ้าที่กินไฟมากที่สุดในบ้าน)
AC_OPTIONS = {
    "ไม่เปิด / ไม่มีแอร์": 0.00,
    "เปิดบางห้อง หรือบางช่วง": 0.05,
    "เปิดเกือบทั้งวัน": 0.12,
}

def estimate_daytime_share(members, home_weekday, ac_bonus):
    """
    แปลงคำตอบแบบง่าย ๆ ให้เป็นสัดส่วนการใช้ไฟช่วงกลางวัน (f_day)
    - ฐาน 20%  : ตู้เย็น ปั๊มน้ำ เครื่องใช้ที่เสียบทิ้งไว้ ทำงานตลอดแม้ไม่มีคนอยู่
    - สูงสุด +35% : ตามสัดส่วนคนที่อยู่บ้านช่วงกลางวัน
    - แอร์      : บวกเพิ่มตามตัวเลือก (คิดเฉพาะเมื่อมีคนอยู่)
    - วันเสาร์-อาทิตย์ถือว่าส่วนใหญ่อยู่บ้าน (อย่างน้อย 75%) แล้วเฉลี่ย 5 วันธรรมดา + 2 วันหยุด
    """
    ratio = home_weekday / members
    weekday = 0.20 + 0.35 * ratio + (ac_bonus if home_weekday > 0 else 0)
    weekend = 0.20 + 0.35 * max(ratio, 0.75) + ac_bonus
    share = (5 * weekday + 2 * weekend) / 7
    return min(max(share, 0.15), 0.85)

# ==========================================
# 3. ส่วนหัว (Hero) และแบบฟอร์มรับ Input บนหน้าหลัก
# ==========================================
st.markdown(
    '<div class="hero">'
    '<span class="hero-badge">☀️ Solar ROI Calculator</span>'
    '<h1>ติดโซลาร์เซลล์ที่บ้าน คุ้มไหม?</h1>'
    '<p>ตอบคำถามสั้น ๆ ไม่กี่ข้อ ระบบจะคำนวณขนาดแผง งบลงทุน และระยะคืนทุนให้ทันที '
    'โดยใช้ข้อมูลแสงแดดจริงจากดาวเทียม NASA</p>'
    '</div>',
    unsafe_allow_html=True,
)

# 2 คอลัมน์บน Desktop/iPad แนวนอน -> เรียงซ้อนเป็นแนวตั้งอัตโนมัติบนมือถือ
col_home, col_loc = st.columns([1.1, 1], gap="large")

with col_home:
    with st.container(border=True):
        st.markdown("##### 🏠 ข้อมูลบ้านของคุณ")
        
        # 3.1 ตัวแปร B = ภาระค่าไฟฟ้ารายเดือน (บาท/เดือน)
        bill_monthly = st.number_input(
            "💡 ค่าไฟรายเดือนเฉลี่ย (บาท)", 
            min_value=500, max_value=100000, value=3000, step=500,
            help="ดูได้จากบิลค่าไฟ หรือแอป PEA Smart Plus / MEA Smart Life"
        )
        
        # 3.2 คำถามแบบง่ายแทนการให้ผู้ใช้กะเปอร์เซ็นต์เอง -> แปลงเป็น f_day
        members = st.number_input(
            "👨‍👩‍👧 สมาชิกในบ้านมีกี่คน", min_value=1, max_value=20, value=4, step=1
        )
        home_weekday = st.slider(
            "🕘 วันธรรมดา ช่วงกลางวัน (9 โมงเช้า – 4 โมงเย็น) มีคนอยู่บ้านกี่คน",
            min_value=0, max_value=int(members), value=min(2, int(members)),
            help="นับคนที่อยู่บ้านเป็นประจำ เช่น ผู้สูงอายุ เด็กเล็ก หรือคนที่ทำงานที่บ้าน"
        )
        ac_choice = st.radio(
            "❄️ ตอนกลางวันเปิดแอร์ไหม", list(AC_OPTIONS.keys()), index=1
        )
        
        f_day = estimate_daytime_share(members, home_weekday, AC_OPTIONS[ac_choice])
        
        # ทางเลือกสำหรับผู้ที่รู้ค่าจริง (เช่น ดูจากมิเตอร์ TOU) ให้กำหนดเองได้
        with st.expander("🔧 รู้ตัวเลขจริง? ปรับเองแบบละเอียด"):
            if st.checkbox("กำหนดสัดส่วนการใช้ไฟกลางวันเอง"):
                f_day = st.slider(
                    "สัดส่วนการใช้ไฟกลางวัน (%)", 0, 100, int(round(f_day * 100)), 5
                ) / 100.0
        
        st.caption(f"👉 ประเมินว่าบ้านคุณใช้ไฟช่วงกลางวันประมาณ **{f_day * 100:.0f}%** ของทั้งหมด")

with col_loc:
    with st.container(border=True):
        st.markdown("##### 📍 บ้านอยู่ที่ไหน")
        # 3.3 เลือกจังหวัด -> อำเภอ แล้วนำพิกัดกลางอำเภอไปใช้แทนการพิมพ์ Latitude/Longitude
        df_districts = load_districts()
        provinces = sorted(df_districts["province"].unique())
        province = st.selectbox(
            "จังหวัด", provinces,
            index=provinces.index("กรุงเทพมหานคร"),
            help="แตะแล้วพิมพ์ชื่อเพื่อค้นหาได้"
        )
        # เรียงให้ "อำเภอเมือง" ขึ้นก่อน ที่เหลือเรียงตามตัวอักษร
        district_names = sorted(
            df_districts.loc[df_districts["province"] == province, "district"],
            key=lambda d: (not d.startswith("เมือง"), d)
        )
        district = st.selectbox(
            "เขต" if province == "กรุงเทพมหานคร" else "อำเภอ", district_names
        )
        
        loc = df_districts[
            (df_districts["province"] == province) & (df_districts["district"] == district)
        ].iloc[0]
        lat, lon = float(loc["lat"]), float(loc["lon"])
        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=8, height=200)
        
        # ประมวลผลการร้องขอ API อัตโนมัติเมื่อพิกัดถูกปรับเปลี่ยน
        with st.spinner("กำลังดึงข้อมูลแสงแดดจากดาวเทียม NASA..."):
            psh_value = fetch_nasa_psh(lat, lon)
        
        st.markdown(
            f'<div class="psh-pill">☀️<div>แดดเฉลี่ยที่ {district}<br>'
            f'<b>{psh_value:.2f}</b> ชั่วโมงแดดเต็มต่อวัน</div></div>',
            unsafe_allow_html=True,
        )

# ==========================================
# 4. กลไกการคำนวณหลัก (Mathematical & Logic Engine)
# ==========================================
# กำหนดตัวแปรคงที่ (Constants) อ้างอิงตามสภาวะเศรษฐศาสตร์มหภาคและฟิสิกส์
R = 4.5             # อัตราค่าไฟฟ้าฐาน (บาท/หน่วย)
efficiency = 0.8    # อัตราส่วนประสิทธิภาพระบบ (หักลบสัมประสิทธิ์อุณหภูมิและความต้านทาน 20%)
cost_per_kw = 35000 # โครงสร้างต้นทุนเฉลี่ยต่อกิโลวัตต์สำหรับภาคครัวเรือน (บาท/kW)
PANEL_WATT = 550    # กำลังไฟต่อแผงที่นิยมในปัจจุบัน (W) ใช้แปลง kW เป็นจำนวนแผงให้เข้าใจง่าย
PANEL_AREA_M2 = 2.6 # พื้นที่หลังคาโดยประมาณต่อแผง (ตร.ม.)

# สมการวิเคราะห์ที่ 1: การประเมินพลังงานบริโภครวมรายเดือน (kWh)
energy_monthly = bill_monthly / R

# สมการวิเคราะห์ที่ 2: การสกัดความต้องการพลังงานสุทธิในช่วงกลางวัน (kWh/วัน)
energy_daytime_daily = (energy_monthly / 30) * f_day

# สมการวิเคราะห์ที่ 3: การประเมินกำลังการผลิตติดตั้งเป้าหมาย (kW)
# โดยปัดเศษทศนิยมขึ้นหนึ่งตำแหน่งเพื่อความปลอดภัยทางวิศวกรรม (Margin of Safety)
raw_panel_size = energy_daytime_daily / (psh_value * efficiency)
panel_size_kw = math.ceil(raw_panel_size * 10) / 10.0
num_panels = math.ceil(panel_size_kw * 1000 / PANEL_WATT)

# สมการวิเคราะห์ที่ 4: การประเมินงบประมาณการลงทุน (CAPEX)
total_cost = panel_size_kw * cost_per_kw

# สมการวิเคราะห์ที่ 5: การประเมินกระแสเงินสดสุทธิที่ประหยัดได้ (บาท/เดือน)
monthly_savings = panel_size_kw * psh_value * efficiency * 30 * R

# สมการวิเคราะห์ที่ 6: การประเมินระยะเวลาคืนทุน (Payback Period)
if monthly_savings > 0:
    payback_years = total_cost / (monthly_savings * 12)
else:
    payback_years = 0

# สมการวิเคราะห์ทางสิ่งแวดล้อม: การประเมินคาร์บอนฟุตพริ้นต์ที่ลดลง
# อ้างอิงสัมประสิทธิ์การปล่อยก๊าซเรือนกระจก (Scope 2) ของ TGO ปี 2025 ที่ 0.475 kgCO2e/kWh
co2_reduction_kg_per_year = (panel_size_kw * psh_value * efficiency * 365) * 0.475

# ==========================================
# 5. การ์ดผลลัพธ์ (Responsive KPI Cards)
# ==========================================
st.subheader("📊 ผลการคำนวณสำหรับบ้านคุณ")

def kpi_card(icon, label, value, unit, sub, extra_class=""):
    # สร้าง HTML ต่อกันเป็นบรรทัดเดียว (ห้ามย่อหน้า ไม่งั้น Markdown จะตีความเป็น code block)
    return (
        f'<div class="kpi {extra_class}"><div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}<span>{unit}</span></div>'
        f'<div class="kpi-sub">{sub}</div></div>'
    )

st.markdown(
    '<div class="kpi-grid">'
    + kpi_card("⚡", "ขนาดระบบที่แนะนำ", f"{panel_size_kw:,.1f}", "kW",
               f"ประมาณ {num_panels} แผง · ใช้หลังคา ~{num_panels * PANEL_AREA_M2:,.0f} ตร.ม.")
    + kpi_card("💰", "งบลงทุนโดยประมาณ", f"{total_cost:,.0f}", "บาท",
               f"คิดที่ {cost_per_kw:,.0f} บาท ต่อ kW")
    + kpi_card("📉", "ประหยัดค่าไฟ", f"{monthly_savings:,.0f}", "บาท/เดือน",
               f"≈ {monthly_savings * 12:,.0f} บาท ต่อปี", "good")
    + kpi_card("⏱️", "คืนทุนภายใน", f"{payback_years:.1f}", "ปี",
               f"🌱 ลด CO₂ ได้ {co2_reduction_kg_per_year:,.0f} kg ต่อปี")
    + '</div>',
    unsafe_allow_html=True,
)

# ==========================================
# 6. การสร้างแผนภูมิวิเคราะห์จุดคุ้มทุนเชิงพลวัต (Break-even Dynamics)
# ==========================================
st.subheader("📈 เปรียบเทียบเงินที่จ่ายสะสมใน 15 ปี")
st.caption("จุดที่เส้นสีเขียวตัดกับเส้นสีแดงคือจุดคุ้มทุน หลังจากนั้นการติดโซลาร์จะถูกกว่า")

# สร้างพาร์ทิชันอาร์เรย์ (NumPy) จำลองแกนเวลา 15 ปี
years = np.arange(0, 16) 

# สถานการณ์ฐาน (Base Case): ไม่มีการลงทุน ภาระค่าไฟฟ้าสะสมเชิงเส้น
cost_no_solar = (bill_monthly * 12) * years

# สถานการณ์ลงทุน (Investment Case): เริ่มต้นด้วยงบลงทุน (CAPEX) และสะสมค่าไฟฟ้าส่วนที่ยังคงเหลือ
remaining_bill = max(0, bill_monthly - monthly_savings)
cost_with_solar = total_cost + ((remaining_bill * 12) * years)

# ใช้ชื่อสั้น ๆ เพื่อให้คำอธิบายกราฟ (Legend) ไม่ล้นจอมือถือ
LABEL_GRID = "ไม่ติดโซลาร์"
LABEL_SOLAR = "ติดโซลาร์"

# จัดรูปแบบข้อมูลลง Pandas DataFrame
df_plot = pd.DataFrame({
    "ปีที่": years,
    LABEL_GRID: cost_no_solar,
    LABEL_SOLAR: cost_with_solar
})

# แปลงสัณฐานข้อมูลด้วยฟังก์ชัน Melt เพื่อรองรับการพล็อตเส้นหลายทิศทางใน Plotly
df_melt = df_plot.melt(
    id_vars=["ปีที่"], 
    var_name="แบบ", 
    value_name="เงินที่จ่ายสะสม (บาท)"
)

# ประมวลผลแผนภูมิเส้นแบบอินเทอร์แอกทีฟ
fig = px.line(
    df_melt, 
    x="ปีที่", 
    y="เงินที่จ่ายสะสม (บาท)", 
    color="แบบ",
    markers=True,
    color_discrete_map={
        LABEL_GRID: "#ef4444",  # กำหนดสีแดงแทนสภาวะสูญเสีย
        LABEL_SOLAR: "#22c55e"  # กำหนดสีเขียวแทนสภาวะคุ้มทุน
    }
)
fig.update_traces(hovertemplate="%{y:,.0f} บาท")

# ขีดเส้นบอกจุดคุ้มทุน (ถ้าอยู่ในกรอบ 15 ปี)
if 0 < payback_years <= 15:
    fig.add_vline(
        x=payback_years, line_dash="dot", line_color="#fbbf24",
        annotation_text=f"คุ้มทุน ~{payback_years:.1f} ปี",
        annotation_position="top left", annotation_font_color="#fbbf24",
    )

# ขัดเกลาเอกลักษณ์ทางภาพ (Visual Polish) + ปรับให้ใช้งานบนจอสัมผัสได้ดี
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans Thai, sans-serif", size=13),
    height=400,
    margin=dict(l=8, r=8, t=30, b=8),
    hovermode="x unified",
    dragmode=False,  # ปิดการลากซูม เพื่อให้ปัดเลื่อนหน้าจอบนมือถือ/iPad ได้ตามปกติ
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None),
    xaxis=dict(title="ปี", fixedrange=True, gridcolor="rgba(148,163,184,.12)"),
    yaxis=dict(title=None, tickformat=",.0f", fixedrange=True, gridcolor="rgba(148,163,184,.12)"),
)

st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": False})

# ==========================================
# 7. สรุปผลเชิงกลยุทธ์และการส่งออกข้อมูล (Strategic Summary & Export)
# ==========================================
st.success(
    f"💡 **สรุป:** บ้านที่จ่ายค่าไฟ {bill_monthly:,.0f} บาท/เดือน ที่{district} {province} "
    f"เหมาะกับระบบขนาด **{panel_size_kw} kW** (ประมาณ {num_panels} แผง) "
    f"ลงทุนราว **{total_cost:,.0f} บาท** และจะคืนทุนในประมาณ **{payback_years:.1f} ปี** "
    f"หลังจากนั้นจะประหยัดค่าไฟได้ราว **{monthly_savings * 12:,.0f} บาทต่อปี**"
)



st.caption(
    "ℹ️ ผลลัพธ์เป็นการประมาณเบื้องต้น คิดค่าไฟ 4.5 บาท/หน่วย ประสิทธิภาพระบบ 80% "
    "และระบบแบบไม่มีแบตเตอรี่ ยังไม่รวมการเสื่อมของแผงและค่าบำรุงรักษา "
    "ควรขอใบเสนอราคาจากผู้ติดตั้งก่อนตัดสินใจ · ข้อมูลแสงแดด: NASA POWER"
)
