import threading
import tkinter as tk
import random
import time


class Tenedor:
    def __init__(self, id):
        self.id = id
        self.ocupado=False
        self.lock = threading.Lock()

    def coger(self):

        return self.lock.acquire(timeout=1)
    def is_ocupado(self):
        self.ocupado = True

    def no_is_ocupado(self):
        self.ocupado = False
    def soltar(self):
        self.lock.release()
    def debug(self):
        while (comando := input(f"cena_filosofos>Tenedor{self.id}>"))!="exit":
            try:
                exec(comando)
            except Exception as e:
                print(e)

class Portero:
    def __init__(self, max_comensales):
        self.semaforo = threading.Semaphore(max_comensales)

    def entrar(self):
        self.semaforo.acquire()

    def salir(self):
        self.semaforo.release()
    def debug(self):
        while (comando := input("cena_filosofos>Portero>"))!="exit":
            try:
                exec(comando)
            except Exception as e:
                print(e)

class Filosofo(threading.Thread):
    def __init__(self, id, tenedor_izq, tenedor_der, portero, interfaz, control_event):
        threading.Thread.__init__(self)
        self.id = id
        self.tenedor_izq = tenedor_izq
        self.tenedor_der = tenedor_der
        self.portero = portero
        self.interfaz = interfaz
        self.comidas = 0
        self.vivo = True
        self.control_event = control_event

    def run(self):
        while self.vivo:
            self.control_event.wait()
            self.pensar()

            self.control_event.wait()
            self.portero.entrar()
            self.interfaz.actualizar_estado(self.id, "Intentando comer", "pink")

            if self.tenedor_izq.coger():
                self.interfaz.actualizar_estado(self.id, f"Cogió tenedor {self.tenedor_izq.id}", "cyan")
                self.tenedor_izq.is_ocupado()
                if self.tenedor_der.coger():
                    self.tenedor_izq.is_ocupado()
                    self.comer()
                    self.tenedor_der.soltar()
                    self.tenedor_der.no_is_ocupado()

                self.tenedor_izq.soltar()
                self.tenedor_izq.no_is_ocupado()
            self.portero.salir()

    def pensar(self):
        self.interfaz.actualizar_estado(self.id, "Pensando", "white")
        time.sleep(random.uniform(0.5, 1.5))

    def comer(self):
        self.interfaz.actualizar_estado(self.id, "Comiendo", "yellow")
        self.tenedor_izq.is_ocupado()
        self.tenedor_der.is_ocupado()
        time.sleep(random.uniform(0.5, 1.0))
        self.comidas += 1
        self.interfaz.actualizar_contador(self.id, self.comidas)

    def detener(self):
        self.vivo = False
    def debug(self):
        while (comando := input(f"cena_filosofos>Filosofo{self.id}>"))!="exit":
            try:
                exec(comando)
            except Exception as e:
                print(e)

class Interfaz:
    def __init__(self, root, num_filosofos, iniciar_callback, pausar_callback, continuar_callback):
        self.root = root
        self.root.title("La Cena de los Filósofos")
        self.root.geometry("1000x600")

        self.texto_log = tk.Text(root, height=10, width=60)
        self.texto_log.place(x=500, y=20)

        self.canvas = tk.Canvas(root, width=480, height=400, bg='lightgray')
        self.canvas.place(x=10, y=10)

        self.etiquetas_filosofos = []
        self.tenedores_gui = []

        self.contador_text = tk.Text(root, height=10, width=50)
        self.contador_text.place(x=500, y=250)

        self.btn_iniciar = tk.Button(root, text="Iniciar", command=iniciar_callback, bg="lightgreen")
        self.btn_iniciar.place(x=500, y=500)

        self.btn_pausar = tk.Button(root, text="Pausar", command=pausar_callback, bg="orange")
        self.btn_pausar.place(x=580, y=500)

        self.btn_continuar = tk.Button(root, text="Continuar", command=continuar_callback, bg="lightblue")
        self.btn_continuar.place(x=660, y=500)

        self.posiciones = [
            (240, 60), (380, 140), (320, 280), (160, 280), (100, 140)
        ]

        self.pos_tenedores = [
            (310, 100), (350, 220), (240, 300), (130, 220), (170, 100)
        ]

        for i in range(num_filosofos):
            x, y = self.posiciones[i]
            etiqueta = self.canvas.create_rectangle(x - 60, y - 25, x + 60, y + 25, fill="white")
            texto = self.canvas.create_text(x, y, text=f"Filósofo {i+1}: Pensando", font=("Arial", 10))
            self.etiquetas_filosofos.append((etiqueta, texto))

            tx, ty = self.pos_tenedores[i]
            tenedor = tk.Label(root, text=f" {i} ",bg="green")
            tenedor.place(x=tx, y=ty)
            self.tenedores_gui.append(tenedor)


    def actualizar_estado(self, id, estado, color):
        etiqueta, texto = self.etiquetas_filosofos[id]
        self.canvas.itemconfig(etiqueta, fill=color)
        self.canvas.itemconfig(texto, text=f"Filósofo {id+1}: {estado}")
        self.texto_log.insert(tk.END, f"Filósofo {id+1}: {estado}\n")
        self.texto_log.see(tk.END)

    def cambiar_color_tenedor(self, id, color):
        self.tenedores_gui[id].configure(bg=color)

    def actualizar_contador(self, id, cuenta):
        lineas = self.contador_text.get("1.0", tk.END).strip().split("\n")
        while len(lineas) < 5:
            lineas.append(f"Filósofo {len(lineas)+1} : 0 platos")
        lineas[id] = f"Filósofo {id+1} : {cuenta} platos"
        self.contador_text.delete("1.0", tk.END)
        self.contador_text.insert(tk.END, "\n".join(lineas))
    def debug(self):
        while comando := input("cena_filosofos>Interfaz>"):
            try:
                exec(comando)
            except Exception as e:
                print(e)

class Simulador:
    def __init__(self, root):
        self.estado = False
        self.num_filosofos = 5
        self.max_comensales = 4
        self.control_event = threading.Event()
        self.control_event.clear()

        self.filosofos = []
        self.tenedores = [Tenedor(i) for i in range(self.num_filosofos)]
        self.portero = Portero(self.max_comensales)

        self.interfaz = Interfaz(root, self.num_filosofos, self.iniciar, self.pausar, self.continuar)
        threading.Thread(target=self.debug).start()
        threading.Thread(target=self.actualizacion).start()

    def iniciar(self):
        self.estado = True
        if not self.filosofos:
            self.control_event.set()
            for i in range(self.num_filosofos):
                f = Filosofo(i, self.tenedores[i], self.tenedores[(i + 1) % self.num_filosofos], self.portero, self.interfaz, self.control_event)
                self.filosofos.append(f)
                f.start()
    def actualizacion(self):
        while True:
            if self.estado:
                for i in self.tenedores:
                    if i.ocupado:
                        self.interfaz.cambiar_color_tenedor(self.tenedores.index(i), "red")
                    else:
                        self.interfaz.cambiar_color_tenedor(self.tenedores.index(i), "green")
    def pausar(self):
        self.estado = False
        self.control_event.clear()
        for i in range(self.num_filosofos):
            self.interfaz.actualizar_estado(i, "Pausado", "gray")

    def continuar(self):
        self.estado = True
        self.control_event.set()

    def detener(self):
        for f in self.filosofos:
            f.detener()
        self.control_event.set()

    def debug(self):
        while (comando := input("cena_filosofos>Simulador>"))!="exit":
            try:
                exec(comando)
            except Exception as e:
                print(e)


def main():


    root = tk.Tk()
    app = Simulador(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.detener(), root.destroy()))
    root.mainloop()





if __name__ == "__main__":
    main()


