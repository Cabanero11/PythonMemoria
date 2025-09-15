import os
import heapq
import concurrent.futures
import time



# Carpetas que ignoraremos (ajusta según tu sistema)
EXCLUDE_DIRS = [
    "C:\\Windows",
    "C:\\ProgramData",
    "C:\\$Recycle.Bin",
    "C:\\Users\\Default",
    "C:\\Users\\All Users",
]

def get_file_size(fp):
    """Intenta devolver el tamaño de un archivo"""
    try:
        return os.path.getsize(fp), fp
    except Exception:
        return None

def get_top_files(path="C:\\", n=10, max_workers=8):
    print("Empieza a buscar 🤯")
    heap = []  # min-heap de tamaño fijo

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for root, dirs, files in os.walk(path):
            # Filtrar directorios excluidos
            if any(root.startswith(ex) for ex in EXCLUDE_DIRS):
                continue

            for f in files:
                fp = os.path.join(root, f)
                futures.append(executor.submit(get_file_size, fp))

        # Procesar resultados a medida que terminan
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is None:
                continue

            size, fp = result
            if len(heap) < n:
                heapq.heappush(heap, (size, fp))
            else:
                heapq.heappushpop(heap, (size, fp))

    # Mostrar resultados ordenados
    for size, file in sorted(heap, reverse=True):

        print(f"{size/1024/1024:.2f} MB -> {os.path.basename(file)}")


# Ejemplo de uso
if __name__ == "__main__":
    time_start = time.time()
    get_top_files("C:\\Users\\Antonio\\Downloads\\DESCARGAS", 20)
    time_end = time.time()
    print(f"Tiempo elapsado = {time_end - time_start:.2f} s")