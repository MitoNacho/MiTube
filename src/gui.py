import PySimpleGUI as sg
import threading
from downloader import YouTubeDownloader

# Variable global para almacenar la carpeta seleccionada
selected_folder = ""

# Función para seleccionar la carpeta de destino
def select_folder():
    folder = sg.popup_get_folder('Seleccione la carpeta de destino')
    if folder:
        global selected_folder
        selected_folder = folder
        window['-FOLDER-'].update(folder)
    return folder

# Función para actualizar la barra de progreso
def update_progress_bar(progress):
    window['-PROGRESS-'].update_bar(progress)
    window['-PROGRESS_TEXT-'].update(f'{progress}%')

# Función para descargar el video en segundo plano
def download_video_in_thread(url, folder):
    try:
        window['-PROGRESS-'].update(visible=True, current_count=0, max=100)
        window['-DOWNLOAD-'].update(disabled=True)  # Deshabilitar botón durante la descarga

        # Crear objeto YouTubeDownloader
        downloader = YouTubeDownloader(folder)
        
        # Descargar el audio
        downloaded_file = downloader.download_audio(url, update_progress_bar)

        # Enviar mensaje de éxito al hilo principal
        window.write_event_value('-DOWNLOAD_COMPLETE-', downloaded_file)
        
        window['-PROGRESS-'].update(visible=False)  # Ocultar barra de progreso

    except Exception as e:
        # Enviar mensaje de error al hilo principal
        window.write_event_value('-DOWNLOAD_ERROR-', str(e))

    window['-DOWNLOAD-'].update(disabled=False)  # Habilitar el botón de descarga

# Layout de la interfaz gráfica
layout = [
    [sg.Text("URL de YouTube:", font=("Verdana", 12))],
    [sg.Input(key='-URL-', size=(50, 1), font=("Verdana", 12)), sg.Button("Pegar enlace", key='-PASTE-', font=("Verdana", 12))],
    [sg.Button("Seleccionar Carpeta de Destino", key='-SELECT-', font=("Verdana", 12), button_color=("black", "#e9d8a6"))],
    [sg.Text("", key='-FOLDER-', size=(50, 1), font=("Verdana", 12))],  # Este es el texto que se actualizará con la carpeta seleccionada
    [sg.Button("Descargar y Convertir", key='-DOWNLOAD-', font=("Verdana", 12), button_color=("black", "#00b4d8"))],
    [sg.Text("", size=(50, 1))],
    [sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='-PROGRESS-', visible=False)],
    [sg.Text("", key='-PROGRESS_TEXT-', size=(50, 1), text_color='black')]
]

# Crear la ventana
icon_path = "assets/icon.ico"  # Ajusta la ruta si es necesario
window = sg.Window("Mi Tube 3.0", layout, icon=icon_path)

# Función de descarga que usa un hilo
def start_download(url, folder):
    if url and folder:
        # Crear un hilo para la descarga
        threading.Thread(target=download_video_in_thread, args=(url, folder), daemon=True).start()

# Loop de eventos
while True:
    event, values = window.read(timeout=10)

    if event == sg.WINDOW_CLOSED:
        break
    elif event == '-SELECT-':
        select_folder()  # Seleccionar carpeta
    elif event == '-DOWNLOAD-':
        url = values['-URL-']
        if selected_folder == "":  # Verificar si no se ha seleccionado una carpeta
            sg.popup("Advertencia", "Por favor, seleccione una carpeta para guardar el archivo.")
            continue
        start_download(url, selected_folder)  # Usar la carpeta seleccionada globalmente
    elif event == '-PASTE-':
        clipboard_content = window.TKroot.clipboard_get()
        window['-URL-'].update(clipboard_content)

    # Procesar eventos de descarga completada o error
    elif event == '-DOWNLOAD_COMPLETE-':
        downloaded_file = values[event]
        sg.popup("¡Listo!", f"Descargado y convertido: {downloaded_file}", icon='info')

    elif event == '-DOWNLOAD_ERROR-':
        error_message = values[event]
        sg.popup("Error", f"Error al descargar: {error_message}", icon='error')

# Cerrar la ventana
window.close()
