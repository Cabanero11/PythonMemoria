import os
import heapq
import concurrent.futures
import tkinter as tk
from tkinter import ttk, filedialog
import threading

# Colores
BG_COLOR = "#2E2E2E"   # gris oscuro
FG_COLOR = "#ADD8E6"   # azul clarito
BTN_COLOR = "#4EA3D6"  # azul más fuerte

EXCLUDE_DIRS = [
    "C:\\Windows",
    "C:\\ProgramData",
    "C:\\$Recycle.Bin",
    "C:\\Users\\Default",
    "C:\\Users\\All Users",
]

def get_file_size(fp):
    try:
        return os.path.getsize(fp), fp
    except Exception:
        return None

def scan_folder(path, n, progress_var, progress_bar, tree):
    heap = []
    futures = []

    # Contar total de archivos
    total_files = 0
    for root, dirs, files in os.walk(path):
        if any(root.startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        total_files += len(files)

    progress_var.set(0)
    progress_bar["maximum"] = max(1, total_files)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for root, dirs, files in os.walk(path):
            if any(root.startswith(ex) for ex in EXCLUDE_DIRS):
                continue
            for f in files:
                fp = os.path.join(root, f)
                futures.append(executor.submit(get_file_size, fp))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            progress_var.set(progress_var.get() + 1)
            if result:
                size, fp = result
                if len(heap) < n:
                    heapq.heappush(heap, (size, fp))
                else:
                    heapq.heappushpop(heap, (size, fp))

    # Limpiar tabla
    for row in tree.get_children():
        tree.delete(row)

    # Insertar nuevos resultados
    for size, file in sorted(heap, reverse=True):
        tree.insert("", tk.END, values=(f"{size/1024/1024:.2f} MB", os.path.basename(file), file))

def start_scan(folder, n_var, progress_var, progress_bar, tree):
    n = int(n_var.get())
    threading.Thread(
        target=scan_folder, 
        args=(folder, n, progress_var, progress_bar, tree),
        daemon=True
    ).start()

def choose_folder(folder_var):
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def main():
    root = tk.Tk()
    root.title("Top Archivos Pesados")
    root.configure(bg=BG_COLOR)

    folder_var = tk.StringVar()
    n_var = tk.IntVar(value=10)
    progress_var = tk.IntVar()

    # Selector carpeta
    folder_frame = tk.Frame(root, bg=BG_COLOR)
    folder_frame.pack(pady=10)
    tk.Entry(folder_frame, textvariable=folder_var, width=40, bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=5)
    tk.Button(folder_frame, text="Elegir carpeta", command=lambda: choose_folder(folder_var), 
              bg=BTN_COLOR, fg="white").pack(side=tk.LEFT)

    # Spinbox cantidad archivos
    tk.Label(root, text="Número de archivos a mostrar:", bg=BG_COLOR, fg=FG_COLOR).pack()
    tk.Spinbox(root, from_=5, to=100, increment=1, textvariable=n_var, width=5, bg=BTN_COLOR, fg=BG_COLOR).pack()

    # Botón escanear
    scan_btn = tk.Button(root, text="ESCANEAR", 
                         command=lambda: start_scan(folder_var.get(), n_var, progress_var, progress_bar, tree),
                         bg=BTN_COLOR, fg="white", font=("Arial", 14, "bold"), width=10, height=1)
    scan_btn.pack(pady=15)

    # Barra de progreso
    progress_bar = ttk.Progressbar(root, variable=progress_var, length=400)
    progress_bar.pack(pady=5)

    # Tabla de resultados
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
                    background=BG_COLOR,
                    foreground=FG_COLOR,
                    rowheight=25,
                    fieldbackground=BG_COLOR)
    style.map("Treeview", background=[("selected", BTN_COLOR)])

    columns = ("Tamaño", "Nombre", "Ruta")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
    tree.heading("Tamaño", text="Tamaño")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Ruta", text="Ruta")

    tree.column("Tamaño", width=100, anchor="center")
    tree.column("Nombre", width=200, anchor="w")
    tree.column("Ruta", width=400, anchor="w")

    tree.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
