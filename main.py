import flet as ft
import requests
import json
import os

# --- GATEWAY KONFIGURASI WEBHOOK & FILE CORE ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwk1jWYyo7Lz2fXkh2QQcfLQB__X2BbRoB4wUzIQTgO6KTLeGd-xsHPp9n0rc-Zt-RG/exec"
CONFIG_PATH = "data/inventory_config.json"

def load_ui_configuration():
    """Membaca data opsi dropdown dari file konfigurasi eksternal (The Fuel)."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as file_stream:
            return json.load(file_stream)
    return {
        "categories": ["Inventaris Umum"],
        "transaction_types": ["INFLOW", "OUTFLOW"],
        "operators": ["Default Operator"]
    }

def main(page: ft.Page):
    page.title = "Terminal Kontrol Inventaris Lokalisasi"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    # Warna dasar mengikuti identitas Corporate Blue
    page.theme = ft.Theme(color_scheme_seed="#1F4E79")

    # Ambil data opsi dari fuel line
    config_fuel = load_ui_configuration()

    # --- INISIALISASI ELEMEN TEKS ANTARMUKA (80% ID / 20% EN) ---
    st_title = ft.Text("📦 Terminal Transaksi Stok Barang", size=24, weight=ft.FontWeight.BOLD, color="#1F4E79")
    st_caption = ft.Text("Inventory Engine Pipeline · Remote Device Sync Operational", size=12, italic=True)
    
    serial_field = ft.TextField(
        label="Nomor Seri / Serial Number", 
        prefix_icon=ft.icons.BARCODE,
        hint_text="Scan QR / Barcode atau ketik kode unik barang..."
    )
    name_field = ft.TextField(
        label="Nama Barang / Nomenclature Item", 
        prefix_icon=ft.icons.PRECISION_MANUFACTURING,
        hint_text="Contoh: Seal Kit Hidrolik PC210"
    )
    qty_field = ft.TextField(
        label="Jumlah Unit / Quantity", 
        value="1", 
        prefix_icon=ft.icons.UNFOLD_MORE
    )

    # --- PEMBUATAN DROPDOWN DINAMIS (BAHASA INDONESIA) ---
    category_dropdown = ft.Dropdown(
        label="Klasifikasi Kategori Barang",
        options=[ft.dropdown.Option(cat) for cat in config_fuel["categories"]],
        prefix_icon=ft.icons.CATEGORY
    )
    type_dropdown = ft.Dropdown(
        label="Jenis Protokol Transaksi",
        options=[ft.dropdown.Option(t_type) for t_type in config_fuel["transaction_types"]],
        prefix_icon=ft.icons.SWAP_HORIZ
    )
    operator_dropdown = ft.Dropdown(
        label="Operator Penanggung Jawab",
        options=[ft.dropdown.Option(op) for op in config_fuel["operators"]],
        prefix_icon=ft.icons.PERSON
    )

    # --- TRIGGER EKSEKUSI DATA PIPELINE ---
    def transmit_form_payload(e):
        # Validasi Input Lapangan
        if not serial_field.value or not name_field.value or not category_dropdown.value or not type_dropdown.value or not operator_dropdown.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ Transaksi Ditolak: Seluruh kolom form wajib diisi!"),
                background_color="#D11A5B" # Crimson Red
            )
            page.snack_bar.open = True
            page.update()
            return

        # Pemetaan data untuk dikirim ke Google Apps Script Gateway
        transaction_packet = {
            "serial_number": str(serial_field.value).strip().upper(),
            "item_name": str(name_field.value).strip(),
            "category": str(category_dropdown.value),
            "transaction_type": str(type_dropdown.value),
            "quantity": int(qty_field.value),
            "operator": str(operator_dropdown.value)
        }

        # Reset visual form segera setelah tombol ditekan untuk menghindari double-tap
        serial_field.value = ""
        name_field.value = ""
        qty_field.value = "1"
        page.update()

        try:
            # Kirim data transaksi secara real-time ke Cloud Spreadsheet
            sync_response = requests.post(
                WEBHOOK_URL, 
                data=json.dumps(transaction_packet),
                headers={"Content-Type": "application/json"},
                timeout=6.0
            )
            
            # Evaluasi respons server data gateway
            if sync_response.status_code == 200 and sync_response.json().get("status") == "SUCCESS":
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚡ Sinkronisasi Berhasil! Baris data telah ditambahkan ke Cloud Ledger."),
                    background_color="#008080" # Teal Stable
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Gagal Terkirim: {sync_response.json().get('message')}"),
                    background_color="#D11A5B"
                )
        except Exception as error_fault:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"🛑 Masalah Jaringan Intercepted: {str(error_fault)}"),
                background_color="#D11A5B"
            )
        
        page.snack_bar.open = True
        page.update()

    # Tombol Aksi Utama Kontrol Internal
    submit_action_btn = ft.ElevatedButton(
        text="Kirim Data Transaksi ke Google Sheets",
        icon=ft.icons.CLOUD_UPLOAD,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor="#1F4E79",
            shape=ft.RoundedRectangleBorder(radius=6)
        ),
        on_click=transmit_form_payload
    )

    # --- STRUKTUR TATA LETAK CONTAINER WIDGET ---
    page.add(
        ft.Container(
            content=ft.Column([
                st_title,
                st_caption,
                ft.Divider(color="#1F4E79", thickness=1.5),
                serial_field,
                name_field,
                ft.Row([category_dropdown, type_dropdown], alignment=ft.MainAxisAlignment.START),
                ft.Row([qty_field, operator_dropdown], alignment=ft.MainAxisAlignment.START),
                ft.VerticalDivider(height=10),
                submit_action_btn
            ], spacing=15),
            padding=20,
            bgcolor="#F4F4F6", # Soft Slate Background
            border_radius=10,
            border=ft.border.all(1, "#1F4E79")
        )
    )

if __name__ == "__main__":
    # Menjalankan Flet dengan mode Web Browser agar kompatibel di Codespaces dan HP
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
