import flet as ft

def main(page: ft.Page):
    page.title = "Azicio Inventory Engine Prototype"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(
        ft.Text("🏗️ Flet Engine Initialized", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Lead Operator: Azicio | Environment: Codespaces", size=14),
    )

ft.run(target=main, view=ft.AppView.WEB_BROWSER)