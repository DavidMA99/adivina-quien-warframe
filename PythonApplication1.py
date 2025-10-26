import json
import random
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ====== Cargar o crear base de datos JSON ======
try:
    with open("warframes.json", "r", encoding="utf-8") as f:
        warframes = json.load(f)
except FileNotFoundError:
    warframes = {}

# ====== Preguntas y opciones ======
preguntas = [
    ("rol", ["daño", "supervivencia", "soporte", "control de masas", "sigilo"]),
    ("genero", ["masculino", "femenino"]),
    ("elemento", ["agua", "toxina", "fuego", "electricidad", "aire", "magia", "magnietico", "tierra", "hielo"]),
    ("tema", ["militar", "ninja", "animal", "mitologico", "magico", "necromante", "cibernetico"]),
    ("dificultad", ["alta", "media", "baja"]),
]

RECURSOS_DIR = "recursos"

# ====== Interfaz gráfica HUD estilo consola ======
class AdivinaWarframe:
    def __init__(self, master):
        self.master = master
        master.title("🎮 ADIVINA QUIÉN: WARFRAME HUD EDITION 🎮")
        master.geometry("1400x800")
        master.configure(bg="black")

        # ASCII header
        self.ascii_art = """
╔══════════════════════════════════════════════════════════════════════╗
║                        ░░░ ADIVINA EL WARFRAME ░░░                  ║
║──────────────────────────────────────────────────────────────────────║
║     Responde las 5 preguntas y el sistema intentará adivinar         ║
║                         tu Warframe pensado.                         ║
╚══════════════════════════════════════════════════════════════════════╝
        """

        self.header_label = tk.Label(master, text=self.ascii_art, font=("Courier New", 14), fg="lime", bg="black", justify="left")
        self.header_label.pack(pady=10)

        # Frame principal dividido
        self.main_frame = tk.Frame(master, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        # Lado izquierdo: preguntas y opciones
        self.left_frame = tk.Frame(self.main_frame, bg="black")
        self.left_frame.pack(side="left", fill="y", padx=20, pady=10)

        self.pregunta_label = tk.Label(self.left_frame, text="", font=("Courier New", 14), fg="cyan", bg="black", justify="left", wraplength=400)
        self.pregunta_label.pack(pady=10)

        self.opciones_frame = tk.Frame(self.left_frame, bg="black")
        self.opciones_frame.pack(pady=10)

        # Lado derecho: resultado + imagen
        self.right_frame = tk.Frame(self.main_frame, bg="black")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=10)

        self.result_frame = tk.Frame(self.right_frame, bg="black")
        self.result_frame.pack(pady=10)

        self.image_label = tk.Label(self.right_frame, bg="black")
        self.image_label.pack(pady=10)

        # Variables de estado
        self.respuestas = {}
        self.indice_pregunta = 0
        self.prediccion = None
        self.img_cache = None

        self.mostrar_pregunta()

    # ====== Funciones de Preguntas ======
    def mostrar_pregunta(self):
        self.clear_frame(self.opciones_frame)
        self.clear_frame(self.result_frame)
        self.image_label.config(image="")

        if self.indice_pregunta < len(preguntas):
            pregunta, opciones = preguntas[self.indice_pregunta]
            self.pregunta_label.config(text=f"{pregunta.capitalize()}:")

            for opcion in opciones:
                btn = tk.Button(
                    self.opciones_frame,
                    text=opcion.upper(),
                    font=("Courier New", 12, "bold"),
                    width=25,
                    fg="yellow",
                    bg="gray20",
                    command=lambda op=opcion: self.guardar_respuesta(op)
                )
                btn.pack(pady=5)
        else:
            self.hacer_prediccion()

    def guardar_respuesta(self, opcion):
        pregunta, _ = preguntas[self.indice_pregunta]
        self.respuestas[pregunta] = opcion
        self.indice_pregunta += 1
        self.mostrar_pregunta()

    # ====== Predicción ======
    def hacer_prediccion(self):
        self.clear_frame(self.opciones_frame)
        self.clear_frame(self.result_frame)

        coincidencias = []
        for nombre, datos in warframes.items():
            match = all(self.respuestas.get(p[0]) == datos.get(p[0]) for p in preguntas if p[0] in self.respuestas)
            if match:
                coincidencias.append(nombre)

        if coincidencias:
            self.prediccion = random.choice(coincidencias)
        else:
            self.prediccion = random.choice(list(warframes.keys()) or ["excalibur"])

        self.mostrar_respuesta_prediccion()

    def mostrar_respuesta_prediccion(self):
        # ASCII dinámico con nombre del Warframe
        ascii_title = f"""
╔════════════════════════════════════════╗
║        {self.prediccion.upper():^36}        ║
╚════════════════════════════════════════╝
        """
        self.clear_frame(self.result_frame)
        label_ascii = tk.Label(self.result_frame, text=ascii_title, font=("Courier New", 14), fg="magenta", bg="black", justify="center")
        label_ascii.pack(pady=5)

        # Mostrar imagen centrada
        img_path = os.path.join(RECURSOS_DIR, f"{self.prediccion.lower()}.png")
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img.thumbnail((500, 500))  # tamaño máximo
            # Agregar borde ASCII sobre la imagen (HUD efecto)
            img_with_border = Image.new("RGBA", (img.width+20, img.height+20), (0,0,0,255))
            img_with_border.paste(img, (10,10))
            draw = ImageDraw.Draw(img_with_border)
            draw.rectangle([(0,0), (img_with_border.width-1, img_with_border.height-1)], outline="lime", width=4)
            self.img_cache = ImageTk.PhotoImage(img_with_border)
            self.image_label.config(image=self.img_cache)
        else:
            self.image_label.config(image="")

        # Botones Sí / No
        btn_si = tk.Button(self.result_frame, text="SÍ ✅", font=("Courier New", 12, "bold"), width=15,
                           fg="green", bg="gray20", command=self.prediccion_acertada)
        btn_si.pack(pady=5)
        btn_no = tk.Button(self.result_frame, text="NO ❌", font=("Courier New", 12, "bold"), width=15,
                           fg="red", bg="gray20", command=self.prediccion_fallida)
        btn_no.pack(pady=5)

    # ====== Predicción acertada ======
    def prediccion_acertada(self):
        self.clear_frame(self.opciones_frame)
        self.clear_frame(self.result_frame)
        label = tk.Label(self.result_frame, text="🎯 ¡Genial! Adiviné correctamente.", font=("Courier New", 14, "bold"),
                         fg="lime", bg="black", justify="center")
        label.pack(pady=10)
        self.mostrar_boton_reiniciar()

    # ====== Predicción fallida y aprendizaje ======
    def prediccion_fallida(self):
        self.clear_frame(self.opciones_frame)
        self.clear_frame(self.result_frame)
        self.image_label.config(image="")

        label = tk.Label(self.result_frame, text="😅 No acerté. ¿En qué Warframe estabas pensando?", font=("Courier New", 14, "bold"),
                         fg="orange", bg="black", justify="center")
        label.pack(pady=10)

        entry_nombre = tk.Entry(self.result_frame, font=("Courier New", 12), width=30, bg="gray20", fg="white")
        entry_nombre.pack(pady=5)
        entry_nombre.focus_set()

        btn_guardar = tk.Button(self.result_frame, text="GUARDAR Y CONTINUAR", font=("Courier New", 12, "bold"),
                                width=25, fg="yellow", bg="gray20",
                                command=lambda: self.guardar_nuevo(entry_nombre.get()))
        btn_guardar.pack(pady=5)

    def guardar_nuevo(self, nombre):
        if not nombre.strip():
            return
        warframes[nombre.lower()] = {p[0]: self.respuestas[p[0]] for p in preguntas}
        with open("warframes.json", "w", encoding="utf-8") as f:
            json.dump(warframes, f, indent=4, ensure_ascii=False)

        self.clear_frame(self.opciones_frame)
        self.clear_frame(self.result_frame)
        self.image_label.config(image="")

        label = tk.Label(self.result_frame, text=f"✅ He aprendido sobre {nombre.title()}!", font=("Courier New", 14, "bold"),
                         fg="lime", bg="black", justify="center")
        label.pack(pady=10)
        self.mostrar_boton_reiniciar()

    def mostrar_boton_reiniciar(self):
        btn_jugar = tk.Button(self.result_frame, text="JUGAR DE NUEVO", font=("Courier New", 12, "bold"),
                              width=20, fg="yellow", bg="gray20", command=self.reiniciar)
        btn_jugar.pack(pady=5)

        btn_salir = tk.Button(self.result_frame, text="SALIR", font=("Courier New", 12, "bold"),
                              width=20, fg="red", bg="gray20", command=self.master.quit)
        btn_salir.pack(pady=5)

    def reiniciar(self):
        self.respuestas = {}
        self.indice_pregunta = 0
        self.prediccion = None
        self.img_cache = None
        self.clear_frame(self.opciones_frame)
        self.clear_frame(self.result_frame)
        self.image_label.config(image="")
        self.mostrar_pregunta()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()


# ====== Ejecutar la ventana ======
if __name__ == "__main__":
    root = tk.Tk()
    juego = AdivinaWarframe(root)
    root.mainloop()
