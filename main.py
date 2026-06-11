import flet as ft
import paho.mqtt.client as mqtt

BROKER = "10.0.14.196"
PUERTO = 1883

# main debe ser async para poder usar page.run_task()
async def main(page: ft.Page):
    page.title   = "SCADA — Estación Meteorológica"
    page.bgcolor = "#0f1117"
    page.padding = 30

    lbl_temp   = ft.Text("-- °C", size=48, weight=ft.FontWeight.BOLD, color="#4f8ef7")
    lbl_hum    = ft.Text("-- %",  size=48, weight=ft.FontWeight.BOLD, color="#34d399")
    lbl_estado = ft.Text("Conectando...", color="#94a3b8", size=13)

    # Función async que page.run_task() puede ejecutar de forma segura desde el hilo de MQTT
    async def do_update():
        page.update()

    def on_connect(c, userdata, flags, reason_code, properties):
        if reason_code == 0:
            lbl_estado.value = "✅ Conectado al broker MQTT"
            c.subscribe("estacion2/#")
        else:
            lbl_estado.value = f"❌ Error de conexión (código {reason_code})"
        page.run_task(do_update)

    def on_message(c, userdata, msg):
        topic   = msg.topic
        payload = msg.payload.decode("utf-8")

        if   topic == "estacion2/temperatura": lbl_temp.value = f"{payload} °C"
        elif topic == "estacion2/humedad":     lbl_hum.value  = f"{payload} %"

        page.run_task(do_update)  # ← seguro desde hilos externos

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PUERTO)
    client.loop_start()

    # set_led debe estar dentro de main() para acceder a client
    def set_led(color):
        client.publish("estacion2/led", color)

    page.add(
        ft.Text("Estación Meteorológica", size=28, weight=ft.FontWeight.BOLD, color="#e2e8f0"),
        lbl_estado,
        ft.Container(
            content=ft.Column([
                ft.Text("MXChip AZ3166", size=16, weight=ft.FontWeight.W_600, color="#94a3b8"),
                ft.Divider(color="#2d3348"),
                ft.Row([ft.Text("🌡️ Temperatura:", color="#94a3b8"), lbl_temp]),
                ft.Row([ft.Text("💧 Humedad:    ", color="#94a3b8"), lbl_hum]),
            ]),
            bgcolor="#1a1d27",
            border_radius=12,
            padding=24,
            border=ft.Border.all(1, "#2d3348"),  # ft.Border con B mayúscula en Flet 0.85+
        ),
        ft.Row([
            ft.ElevatedButton("🔴 Rojo",   on_click=lambda _: set_led("red"),   bgcolor="#f87171", color="white"),
            ft.ElevatedButton("🟢 Verde",  on_click=lambda _: set_led("green"), bgcolor="#34d399", color="white"),
            ft.ElevatedButton("🔵 Azul",   on_click=lambda _: set_led("blue"),  bgcolor="#4f8ef7", color="white"),
            ft.ElevatedButton("⬛ Apagar", on_click=lambda _: set_led("off"),   bgcolor="#374151", color="white"),
        ]),
    )

ft.run(main)  # ft.run() reemplaza a ft.app() en Flet 0.80+