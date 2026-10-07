# ☀️ Solar ROI Calculator — ติดโซลาร์เซลล์ที่บ้าน คุ้มไหม?

เว็บแอปคำนวณขนาดระบบโซลาร์เซลล์ งบลงทุน และระยะคืนทุน สำหรับบ้านในประเทศไทย
ใช้ข้อมูลแสงแดดจริงจาก [NASA POWER](https://power.larc.nasa.gov/) รองรับมือถือ iPad และ Desktop

## รันบนเครื่อง
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## โครงสร้างไฟล์
| ไฟล์ | หน้าที่ |
|---|---|
| `app.py` | ตัวแอปทั้งหมด |
| `data/thai_districts.csv` | พิกัดกลางอำเภอ 928 อำเภอ / 77 จังหวัด (ที่มา: OpenGISData-Thailand) |
| `.streamlit/config.toml` | ธีมและการตั้งค่า |
| `requirements.txt` | ไลบรารีที่ใช้ |

## Deploy ฟรีบน Streamlit Community Cloud
1. Push โฟลเดอร์นี้ขึ้น GitHub (public หรือ private ก็ได้)
2. ไปที่ https://share.streamlit.io แล้วล็อกอินด้วย GitHub
3. กด **Create app** → เลือก repo, branch `main`, ไฟล์ `app.py`
4. กด **Deploy** รอ 1–3 นาที จะได้ลิงก์ `https://<ชื่อ>.streamlit.app`
