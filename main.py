import streamlit as st
import requests
import json
import os

# --- GATEWAY KONFIGURASI WEBHOOK & FILE CORE ---
WEBHOOK_URL = "YOUR_DEPLOYMENT_URL_HERE"
CONFIG_PATH = "data/inventory_config.json"

def load_ui_configuration():
    """Membaca data opsi dropdown dari file konfigurasi eksternal (The Fuel)."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as file_stream:
            return json.load(file_stream)
    return {
        "categories": ["Inventaris Umum"],
        "transaction_types": ["INFLOW", "OUTFLOW"],
        "operators": ["Default Operator"],
        "items_registry": {}
    }

st.set_page_config(page_title="Terminal Kontrol Inventaris", page_icon="📦", layout="wide")

# Warna korporat
st.markdown("""
    <style>
    .stApp { background-color: #F4F4F6; }
    .stButton > button {
        background-color: #1F4E79;
        color: white;
        border-radius: 6px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

config = load_ui_configuration()
items_db = config.get("items_registry", {})

st.title("📦 Terminal Transaksi Stok Barang")
st.caption("Auto-Lookup Registry Engine Operational | Remote Device Sync Enabled")

# --- FORMULIR INPUT ---
serial_number = st.text_input("Nomor Seri / Serial Number (Scan Barcode)", placeholder="Scan kode komponen...")

# Auto-lookup logic
if serial_number:
    search_key = serial_number.strip()
    if search_key in items_db:
        nama_barang = items_db[search_key]["name"]
        kategori_barang = items_db[search_key]["category"]
        st.success(f"🎯 Serial {search_key} teridentifikasi otomatis!")
        nama_disabled = True
        kategori_disabled = True
    else:
        nama_barang = ""
        kategori_barang = None
        nama_disabled = False
        kategori_disabled = False
else:
    nama_barang = ""
    kategori_barang = None
    nama_disabled = False
    kategori_disabled = False

col1, col2 = st.columns(2)

with col1:
    nama_input = st.text_input("Nama Barang / Nomenclature Item", value=nama_barang, disabled=nama_disabled)
    kategori_input = st.selectbox(
        "Klasifikasi Kategori Barang",
        config["categories"],
        index=config["categories"].index(kategori_barang) if kategori_barang in config["categories"] else 0,
        disabled=kategori_disabled
    )
    jumlah_input = st.number_input("Jumlah Unit / Quantity", min_value=1, value=1)

with col2:
    tipe_transaksi = st.selectbox("Jenis Protokol Transaksi", config["transaction_types"])
    operator_input = st.selectbox("Operator Penanggung Jawab", config["operators"])

# --- TOMBOL KIRIM ---
if st.button("Kirim Data Transaksi ke Google Sheets", use_container_width=True):
    if not serial_number or not nama_input or not kategori_input or not tipe_transaksi or not operator_input:
        st.error("⚠️ Gagal: Seluruh kolom data wajib dilengkapi!")
    else:
        transaction_packet = {
            "serial_number": str(serial_number).strip().upper(),
            "item_name": str(nama_input).strip(),
            "category": str(kategori_input),
            "transaction_type": str(tipe_transaksi),
            "quantity": int(jumlah_input),
            "operator": str(operator_input)
        }

        try:
            resp = requests.post(WEBHOOK_URL, json=transaction_packet, timeout=6.0)
            if resp.status_code == 200 and resp.json().get("status") == "SUCCESS":
                st.success("⚡ Sinkronisasi Sukses! Cloud Ledger Diperbarui.")
                st.balloons()
            else:
                st.error(f"❌ Data Gagal Terkirim: {resp.json().get('message')}")
        except Exception as err:
            st.error(f"🛑 Gangguan Jaringan: {str(err)}")

# --- FOOTER ---
st.divider()
st.caption("Flet Inventory Engine v1.0 · Powered by Streamlit · Webhook ke Google Sheets")