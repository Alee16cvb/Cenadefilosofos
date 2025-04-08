import threading
import time
import random
import tkinter as tk
from tkinter import ttk

class Tenedor:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()

    def tomar(self):
        self.lock.acquire()

    def soltar(self):
        self.lock.release()

class Portero:
    def __init__(self, capacidad):
        self.semaforo = threading.Semaphore(capacidad)

    def entrar(self):
        self.semaforo.acquire()

    def salir(self):
        self.semaforo.release()

class Filosofo(threading.Thread):
    def __init__(self, id, tenedor_izq, tenedor_der, portero, interfaz):
        super().__init__()
        self.id = id
        self.tenedor_izq = tenedor_izq
        self.tenedor_der = tenedor_der
        self.portero = portero
        self.interfaz = interfaz
        self.contador = 0
        self.running = True
        self.paused = threading.Event()
        self.paused.set()

    def run(self):
        while self.running:
            self.paused.wait()
            self.interfaz.actualizar_estado(self.id, "Pensando")
            time.sleep(random.uniform(0.5, 1.5))

            self.portero.entrar()
            self.interfaz.actualizar_estado(self.id, "Quiere comer")

            self.tenedor_izq.tomar()
            self.interfaz.ocupar_tenedor((self.id + 4) % 5)

            if not self.tenedor_der.lock.acquire(timeout=random.uniform(0.5, 1.0)):
                self.tenedor_izq.soltar()
                self.interfaz.liberar_tenedor((self.id + 4) % 5)
                self.portero.salir()
                self.interfaz.actualizar_estado(self.id, "Pensando")
                continue

            self.interfaz.ocupar_tenedor(self.id)
            self.interfaz.actualizar_estado(self.id, "Comiendo")
            self.contador += 1
            self.interfaz.actualizar_contador(self.id, self.contador)
            time.sleep(random.uniform(0.5, 1.0))

            self.tenedor_der.soltar()
            self.interfaz.liberar_tenedor(self.id)
            self.tenedor_izq.soltar()
            self.interfaz.liberar_tenedor((self.id + 4) % 5)
            self.portero.salir()

    def pausar(self):
        self.paused.clear()

    def continuar(self):
        self.paused.set()

    def detener(self):
        self.running = False
        self.continuar()

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("La Cena de los Filósofos")
        self.filosofos = []
        self.labels = []
        self.tenedores = []
        self.contadores = []

        self.canvas = tk.Canvas(root, width=600, height=400)
        self.canvas.pack()

        posiciones = [(250, 50), (400, 150), (330, 300), (170, 300), (100, 150)]
        for i, pos in enumerate(posiciones):
            label = tk.Label(root, text=f"Filósofo {i+1}", bg="white", relief="solid", width=15)
            label.place(x=pos[0], y=pos[1])
            self.labels.append(label)
            contador = tk.Entry(root, width=5)
            contador.place(x=pos[0]+60, y=pos[1])
            self.contadores.append(contador)

        tenedor_pos = [(325, 100), (370, 230), (250, 330), (150, 230), (200, 100)]
        for pos in tenedor_pos:
            label = tk.Label(root, text="T", bg="lightgray", relief="raised", width=2)
            label.place(x=pos[0], y=pos[1])
            self.tenedores.append(label)

        self.log = tk.Text(root, height=8, width=70)
        self.log.place(x=50, y=350)

        self.iniciar_btn = tk.Button(root, text="Iniciar", command=self.iniciar)
        self.iniciar_btn.place(x=500, y=50)
        self.pausar_btn = tk.Button(root, text="Pausar", command=self.pausar)
        self.pausar_btn.place(x=500, y=90)
        self.continuar_btn = tk.Button(root, text="Continuar", command=self.continuar)
        self.continuar_btn.place(x=500, y=130)

    def actualizar_estado(self, id, estado):
        colores = {
            "Pensando": "white",
            "Quiere comer": "pink",
            "Comiendo": "orange"
        }
        self.labels[id].config(bg=colores[estado])
        self.log.insert(tk.END, f"Filósofo {id+1} está {estado}\n")
        self.log.see(tk.END)

    def actualizar_contador(self, id, valor):
        self.contadores[id].delete(0, tk.END)
        self.contadores[id].insert(0, str(valor))

    def ocupar_tenedor(self, id):
        self.tenedores[id].config(bg="blue")

    def liberar_tenedor(self, id):
        self.tenedores[id].config(bg="lightgray")

    def iniciar(self):
        tenedores = [Tenedor(i) for i in range(5)]
        portero = Portero(4)
        for i in range(5):
            f = Filosofo(i, tenedores[i], tenedores[(i+1)%5], portero, self)
            self.filosofos.append(f)
            f.start()

    def pausar(self):
        for f in self.filosofos:
            f.pausar()

    def continuar(self):
        for f in self.filosofos:
            f.continuar()

if __name__ == "__main__":
    root = tk.Tk()
    interfaz = Interfaz(root)
    root.mainloop()
