import threading
import tkinter as tk
import random
import time


class Tenedor:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()

    def coger(self):
        return self.lock.acquire(timeout=1)

    def soltar(self):
        self.lock.release()


class Portero:
    def __init__(self, max_comensales):
        self.semaforo = threading.Semaphore(max_comensales)

    def entrar(self):
        self.semaforo.acquire()

    def salir(self):
        self.semaforo.release()


class Filosofo(threading.Thread):
    def __init__(self, id, tenedor_izq, tenedor_der, portero, interfaz):
        threading.Thread.__init__(self)
        self.id = id
        self.tenedor_izq = tenedor_izq
        self.tenedor_der = tenedor_der
        self.portero = portero
        self.interfaz = interfaz
        self.comidas = 0
        self.vivo = True

    def run(self):
        while self.vivo:
            self.pensar()

            self.portero.entrar()
            self.interfaz.actualizar_estado(self.id, "Intentando comer", "pink")

            if self.tenedor_izq.coger():
                self.interfaz.actualizar_estado(self.id, f"Cogió tenedor izquierdo {self.tenedor_izq.id}", "cyan")

                if self.tenedor_der.coger():
                    self.comer()
                    self.tenedor_der.soltar()

                self.tenedor_izq.soltar()

            self.portero.salir()

    def pensar(self):
        self.interfaz.actualizar_estado(self.id, "Pensando", "white")
        time.sleep(random.uniform(0.5, 1.5))

    def comer(self):
        self.interfaz.actualizar_estado(self.id, "Comiendo", "yellow")
        time.sleep(random.uniform(0.5, 1.0))
        self.comidas += 1
        self.interfaz.actualizar_contador(self.id, self.comidas)

    def detener(self):
        self.vivo = False


class Interfaz:
    def __init__(self, root, num_filosofos):
        self.root = root
        self.root.title("La Cena de los Filósofos")
        self.texto_log = tk.Text(root, height=10, width=50)
        self.texto_log.grid(row=0, column=0, columnspan=3)

        self.etiquetas = []
        self.contadores = []

        for i in range(num_filosofos):
            etiqueta = tk.Label(root, text=f"Filósofo {i+1}", bg="white", width=15)
            etiqueta.grid(row=i+1, column=0)
            self.etiquetas.append(etiqueta)

            contador = tk.Entry(root, width=5)
            contador.grid(row=i+1, column=1)
            contador.insert(0, "0")
            self.contadores.append(contador)

    def actualizar_estado(self, id, estado, color):
        self.etiquetas[id].config(text=f"Filósofo {id+1}: {estado}", bg=color)
        self.texto_log.insert(tk.END, f"Filósofo {id+1}: {estado}\n")
        self.texto_log.see(tk.END)

    def actualizar_contador(self, id, cuenta):
        self.contadores[id].delete(0, tk.END)
        self.contadores[id].insert(0, str(cuenta))


def main():
    num_filosofos = 5
    max_comensales = 4  # Permitir que coman hasta 4 filósofos al mismo tiempo

    root = tk.Tk()
    interfaz = Interfaz(root, num_filosofos)

    tenedores = [Tenedor(i) for i in range(num_filosofos)]
    portero = Portero(max_comensales)

    filosofos = [Filosofo(i, tenedores[i], tenedores[(i + 1) % num_filosofos], portero, interfaz) for i in range(num_filosofos)]

    for filosofo in filosofos:
        filosofo.start()

    root.protocol("WM_DELETE_WINDOW", lambda: [filosofo.detener() for filosofo in filosofos] or root.destroy())
    root.mainloop()


if __name__ == "__main__":
    main()