import flet as ft
import requests
import json
import os

WEBHOOK_URL = "YOUR_DEPLOYMENT_URL_HERE"
CONFIG_PATH = "data/inventory_config.json"

def load_ui_configuration():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as file_stream:
            return json.load(file_stream)
    return {
        "categories": ["Inventaris Umum"],
        "transaction_types": ["INFLOW"],
        "operators": ["Default Operator"],
        "items_registry": {}
    }

def main(page: ft.Page):
    page.title = "Terminal Kontrol Inventaris Otomatis"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme = ft.Theme(color_scheme_seed="#1F4E79")

    config_fuel = load_ui_configuration()
    items_db = config_fuel.get("items_registry", {})

    # --- ELEMEN INPUT ANTARMUKA ---
    st_title = ft.Text("📦 Terminal Transaksi Stok Barang", size=24, weight=ft.FontWeight.BOLD, color="#1F4E79")
    st_caption = ft.Text("Auto-Lookup Registry Engine Operational", size=12, italic=True)
    
    name_field = ft.TextField(label="Nama Barang / Nomenclature Item", prefix_icon=ft.icons.PRECISION_MANUFACTURING)
    qty_field = ft.TextField(label="Jumlah Unit / Quantity", value="1", prefix_icon=ft.icons.UNFOLD_MORE)

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

    # --- INTELLIGENT AUTO-LOOKUP LOGIC GATES ---
    def check_barcode_registry(e):
        search_key = str(serial_field.value).strip()
        
        # If the serial matches a record inside our JSON fuel registry, auto-populate the form
        if search_key in items_db:
            name_field.value = items_db[search_key]["name"]
            category_dropdown.value = items_db[search_key]["category"]
            name_field.disabled = True  # Protect known items from accidental renaming typos
            category_dropdown.disabled = True
            page.snack_bar = ft.SnackBar(ft.Text(f"🎯 Serial {search_key} Teridentifikasi Otomatis!"), background_color="#008080")
            page.snack_bar.open = True
        else:
            # If item is unknown, keep fields open to allow manual field logging updates
            name_field.value = ""
            category_dropdown.value = None
            name_field.disabled = False
            category_dropdown.disabled = False
        page.update()

    # Define the serial control widget with the automated lookup event listener attached
    serial_field = ft.TextField(
        label="Nomor Seri / Serial Number (Scan Barcode)", 
        prefix_icon=ft.icons.BARCODE,
        hint_text="Scan kode komponen...",
        on_change=check_barcode_registry # Fires automatically on input stream changes
    )

    # --- TRANSMIT ACTION MATRIX ---
    def transmit_form_payload(e):
        if not serial_field.value or not name_field.value or not category_dropdown.value or not type_dropdown.value or not operator_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Gagal: Seluruh kolom data wajib dilengkapi!"), background_color="#D11A5B")
            page.snack_bar.open = True
            page.update()
            return

        transaction_packet = {
            "serial_number": str(serial_field.value).strip().upper(),
            "item_name": str(name_field.value).strip(),
            "category": str(category_dropdown.value),
            "transaction_type": str(type_dropdown.value),
            "quantity": int(qty_field.value),
            "operator": str(operator_dropdown.value)
        }

        # Reset Form and clear disable locks for the next transaction scan block
        serial_field.value = ""
        name_field.value = ""
        qty_field.value = "1"
        name_field.disabled = False
        category_dropdown.disabled = False
        page.update()

        try:
            sync_response = requests.post(WEBHOOK_URL, json=transaction_packet, timeout=6.0)
            if sync_response.status_code == 200 and sync_response.json().get("status") == "SUCCESS":
                page.snack_bar = ft.SnackBar(ft.Text("⚡ Sinkronisasi Sukses! Cloud Ledger Diperbarui."), background_color="#008080")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Data Gagal Terkirim ke Cloud Server."), background_color="#D11A5B")
        except Exception as error_fault:
            page.snack_bar = ft.SnackBar(ft.Text(f"🛑 Gangguan Jaringan: {str(error_fault)}"), background_color="#D11A5B")
        
        page.snack_bar.open = True
        page.update()

    submit_action_btn = ft.ElevatedButton(
        text="Kirim Data Transaksi ke Google Sheets",
        icon=ft.icons.CLOUD_UPLOAD,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor="#1F4E79", shape=ft.RoundedRectangleBorder(radius=6)),
        on_click=transmit_form_payload
    )

    page.add(
        ft.Container(
            content=ft.Column([
                st_title, st_caption,
                ft.Divider(color="#1F4E79", thickness=1.5),
                serial_field, name_field,
                ft.Row([category_dropdown, type_dropdown], alignment=ft.MainAxisAlignment.START),
                ft.Row([qty_field, operator_dropdown], alignment=ft.MainAxisAlignment.START),
                ft.VerticalDivider(height=10),
                submit_action_btn
            ], spacing=15),
            padding=20, bgcolor="#F4F4F6", border_radius=10, border=ft.border.all(1, "#1F4E79")
        )
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
