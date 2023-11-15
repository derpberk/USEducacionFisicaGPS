import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
from tkinter import filedialog
import os
import pandas as pd
import sv_ttk
import utm
import numpy as np
from tkcalendar import Calendar, DateEntry
from functools import reduce

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from matplotlib.figure import Figure as MatplotlibFigure

import matplotlib.pyplot as plt

dataframe = None
loaded_analisis_frame = False
directory_path = None

class windows(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        # Titulo y tamano
        self.geometry("900x500")
        self.resizable(False, False) 
        # Disable size modification
        self.wm_title("ACE-TI - Analisis de Comportamiento Físico")
        # ICONO
        self.iconbitmap(r'./ico.ico')


        # Creamos el contenedor
        self.container = ttk.Frame(self, height=750, width=600)

        # specifying the region where the frame is packed in root
        self.container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)


        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames themselves later but let's add the components to the dictionary.
        for num, F in enumerate((MainPage, Analisis)):
            frame = F(self.container, self)
            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.show_frame(MainPage)

    def show_frame(self, cont):
        
        if cont == Analisis:
            global loaded_analisis_frame
            # Regenerar el frame de Analisis tras cargar el dataset o si este ha cambiado
            if not loaded_analisis_frame:
                self.frames[cont] = Analisis(self.container, self)
                self.frames[cont].grid(row=0, column=0, sticky="nsew")

        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Configuración de datos", font=("Arial", 12, "bold"))
        self.label.place(x=10, y=10)

        # Image logo
        img = Image.open("aceti.png")
        img = img.resize((140, 60))
        img = ImageTk.PhotoImage(img)
        self.logo = tk.Label(self, image=img)
        self.logo.image = img
        self.logo.place(x=700, y=10)

        # Botón para seleccionar la carpeta #
        self.directory_path = None
        self.select_directory = ttk.Button(self, text="Cargar archivos de carpeta", command=self.browse_button)
        self.select_directory.place(x=10, y=110)

        # Botón para cargar un dataset completo #
        self.load_button = ttk.Button(
            self,
            text="Cargar un archivo de datos",
            command=self.load_button_fn,
        )
        self.load_button.place(x=10, y = 160)

        # Label para mostrar el path
        self.directory_label_width = 95
        self.directory_label = ttk.Label(self, text="Seleccione la ruta con los archivos", width=self.directory_label_width)
        self.directory_label.place(x=210, y=75)

        # Caja de dialogo
        self.dialog_box = scrolledtext.ScrolledText(self, undo=True, width=80, height=20, font=("Arial", 11))
        self.dialog_box.insert(tk.END, "Selecciona un archivo de datos o una carpeta.")
        self.dialog_box.config(state=tk.DISABLED)
        self.dialog_box.place(x = 210, y = 100)

        # Boton para guardar un dataset completo #
        self.save_button = ttk.Button(
            self,
            text="Guardar datos en archivo",
            command=self.save_button_fn,
        )

        self.save_button.place(x=10, y = 410)

        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = ttk.Button(
            self,
            text="Análisis de datos",
            command=lambda: controller.show_frame(Analisis),
        )

        switch_window_button.pack(side="bottom", fill=tk.X)

    def browse_button(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        self.directory_path = filedialog.askdirectory()
        if self.directory_path is not None and self.directory_path != '':
            global directory_path
            directory_path = self.directory_path
            directory_label_text = self.directory_path[:self.directory_label_width-3] + "..." if len(self.directory_path) > self.directory_label_width else self.directory_path
            self.directory_label.configure(text=directory_label_text)
            self.convert_files_fn()

    def load_button_fn(self):

        global dataframe, loaded_analisis_frame, directory_path

        # Cargar dataset
        # file_path_hanlder = filedialog.askopenfile()
        file_path_hanlder = filedialog.askopenfile(title="Seleccionar archivo", filetypes=[("Archivo de datos", "*.csv")]
    )

        if file_path_hanlder is not None:

            file_path = file_path_hanlder.name
            directory_path = os.path.dirname(file_path)
            self.directory_path = os.path.dirname(file_path)

            if file_path[-4:] == '.csv':
                
                dataframe = pd.read_csv(file_path, dtype={'player_id': str})
                self.dialog("Se ha cargado un nuevo archivo de: " + file_path)

            else:
                self.popup_showinfo("Error", "No es un archivo valido.")
            
        loaded_analisis_frame = False

    def save_button_fn(self):

        global dataframe

        if dataframe is None:
            self.dialog("No hay ningún conjunto de datos cargado. Por favor, cargue uno o seleccione una carpeta.")
        else:
            file_path = filedialog.askdirectory()

            print(file_path)

            if file_path is not None and dataframe is not None and file_path != "":

                try: 
                    dataframe.to_csv(file_path + '/all_data.csv')
                    self.dialog("Dataset guardado en: " + file_path + '/all_data.csv')

                except:
                    self.popup_showinfo("Error", "Ha habido un error en el guardado.")

    def convert_files_fn(self):
        # Función para leer los archivos, pasarlos a pandas y convertirlos #
        global dataframe, loaded_analisis_frame

        if self.directory_path is None:
            # No se ha seleccionado nada
            self.dialog("No se ha seleccionado ningún directorio.")
            
        else:

            # Leemos todos los archivos de ese path y seleccionamos los que terminan es CSV
            files_in_path = os.listdir(self.directory_path)

            csv_files = []

            for file in files_in_path:
                if file[-4:] == '.csv' and file != "all_data.csv":
                    csv_files.append(file)

            if len(csv_files) == 0:
                self.dialog(f"No hay archivos válidos en ese directorio. Por favor, seleccione otro.")
                self.popup_showinfo("Error", "No hay ningún archivo csv en el directorio.")
            else:
                self.dialog(f"¡Se han encontrado {len(csv_files)} archivos!")

                datafiles = []

                for n, file in enumerate(csv_files):
                    name = file[:-4]
                    df = pd.read_csv(self.directory_path + '/' + file)
                    df['player_id'] = name
                    df['player_id'] = df['player_id'].astype(str)
                    datafiles.append(df.copy())

                    self.dialog(f"Leyendo archivo {n+1}/{len(csv_files)}: {file}")

                dataframe = pd.concat(datafiles, ignore_index=True)

                # Save dataframe
                
                new_file_name = self.directory_path + '/all_data.csv'
                dataframe.to_csv(new_file_name)
                self.dialog(f"Experimento guardado en: {new_file_name}")

        loaded_analisis_frame = False

    def dialog(self, text):

        self.dialog_box.config(state = tk.NORMAL)
        self.dialog_box.insert(tk.END, "\n")
        self.dialog_box.insert(tk.END, text)
        self.dialog_box.see("end")
        self.dialog_box.config(state = tk.DISABLED)

    @staticmethod
    def popup_showinfo(title, msg):
        tk.messagebox.showinfo(message=msg, title=title)

class Analisis(tk.Frame):


    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # Título
        self.label = ttk.Label(self, text="Análisis de resultados", font=("Arial", 12, "bold"))
        self.label.place(x=10, y=10)

        switch_window_button = ttk.Button(
            self,
            text="Carga de datos",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

        global dataframe
        if dataframe is not None:
            global loaded_analisis_frame
            loaded_analisis_frame = True
            
            # Botón para analizar los resultados
            self.analyze_results_button = ttk.Button(
                self,
                text="Analizar resultados",
                command=self.analyze_results_fn,
            )
            self.analyze_results_button.place(x=10, y=70)

            self.date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=1, 
                                        date_pattern='dd/mm/y', showweeknumbers=False, locale='es_ES')
            self.last_event_date = pd.to_datetime(dataframe['timestamp'].max())
            self.date_entry.set_date(self.last_event_date) # fecha por defecto la del último evento
            self.date_entry.place(x=10, y=110)

            # Botón para poner como fecha la última misión encontrada
            self.last_event_button = ttk.Button(
                self,
                text="Ir al último evento",
                command=self.last_event_fn,
            )
            self.last_event_button.place(x=10, y=150)

            # Plot space
            with plt.style.context('seaborn-darkgrid'):
                self.fig = MatplotlibFigure(figsize=(7, 3.5))
                self.plot_space = FigureCanvasTkAgg(self.fig, master=self)
                self.plot_space.draw()
                self.plot_space.get_tk_widget().place(x=200, y=70)

                # Remove fig background
                self.fig.patch.set_facecolor('#2b2b2b')

                self.ax = self.fig.add_subplot(111)
                # Set axis colrs in white
                self.ax.spines['bottom'].set_color('white')

                # Set ticks numbers on white
                self.ax.tick_params(axis='x', colors='white')
                self.ax.tick_params(axis='y', colors='white')

                # Set axis labels in white
                self.ax.xaxis.label.set_color('white')
                self.ax.yaxis.label.set_color('white')

                self.ax.set_xlabel('X (m)')
                self.ax.set_ylabel('Y (m)')

                # Aspect ratio 1:1
                self.ax.set_aspect('equal', adjustable='box')

                self.fig.set_tight_layout(True)

                toolbar = NavigationToolbar2Tk(self.plot_space, self)
                toolbar.update()
                self.plot_space.get_tk_widget().place(x=200, y=70)
            
            # Icono e información de carga
            img = Image.open("loading.png")
            img = img.resize((25, 25))
            img = ImageTk.PhotoImage(img)
            self.loading_image = tk.Label(self, image=img)
            self.loading_image.image = img
            self.loading_label = ttk.Label(self, text=f"Analizando datos, por favor espere.", font=("Arial", 12))

            # Label para mostrar fecha del evento
            self.event_date_label = ttk.Label(self, font=("Arial", 12, "bold"))
        else:
            self.nodata_label = ttk.Label(self, text="¡Aún no hay datos cargados!", width=90, font=("Arial", 16, "bold"))
            self.nodata_label.place(x=310, y=230)

    def last_event_fn(self):
        self.date_entry.set_date(self.last_event_date)

    def analyze_results_fn(self):

        global dataframe

        if dataframe is None:
            self.popup_showinfo("Error", "No hay ningún archivo cargado.")

        else:
            # Avisamos de que se está analizando
            self.loading_image.place(x=200, y=35)
            self.loading_label.place(x=238, y=42)
            self.event_date_label.place_forget()
            self.update() # refresh frame

            # Filtramos y curamos los datos #
            transformed_dataset = self.transform_dataset(dataframe, self.date_entry.get_date())

            if transformed_dataset is not None:
                # Sacamos las metricas más importantes #
                metrics = get_metrics(transformed_dataset)
                print(metrics)

                # Plot the trajectories
                self.plot_trajectories(transformed_dataset)

                # Label para mostrar fecha del evento
                fecha_ini = transformed_dataset['timestamp'].iloc[-1].strftime("%H:%M del %d/%m/%Y")
                self.event_date_label.config(text=f"Evento con fecha de inicio: {fecha_ini}")
                self.event_date_label.place(x=345, y=40)

            # Eliminar aviso después de completar el análisis
            self.loading_image.place_forget()
            self.loading_label.place_forget()

    def transform_dataset(self, dataset: pd.DataFrame, date=None):
        """ Cura el dataset para que sea más facil de analizar """

        transformed_dataset = dataset.copy()

        if date is None:
            # Raise a warning
            self.popup_showinfo("Error", "No hay ninguna fecha seleccionada.")

            return None
        

        # 1) Transformamos las fechas en milisegundos
        transformed_dataset['timestamp'] = pd.to_datetime(dataset['timestamp'])

        # 2) Ordenamos por fecha
        transformed_dataset = transformed_dataset.sort_values(by=['timestamp'])

        # Cambiamos el formato de la fecha a YYYY-MM-DD
        # transformed_dataset['timestamp'] = pd.to_datetime(transformed_dataset['timestamp'], format='%Y-%m-%d %H:%M:%S')

        # 3) Filtramos por fecha
        date = pd.to_datetime(date, format='%Y-%m-%d')
        transformed_dataset = transformed_dataset[transformed_dataset['timestamp'].dt.date == date.date()]

        if len(transformed_dataset) == 0:
            # Raise a warning
            self.popup_showinfo("Error", "No hay ningún dato para esa fecha.")

            return None
        
        # 4) Filtramos por timestamps que todos los player_id tengan
        # 4.1) Obtenemos los player_id
        player_ids = transformed_dataset['player_id'].unique()

        # 4.2) Obtenemos los timestamps de cada player_id
        timestamps_player_id = [transformed_dataset[transformed_dataset['player_id'] == player_id]['timestamp'] for player_id in player_ids]

        # 4.3) Obtenemos los timestamps comunes a todos
        common_timestamps = reduce(np.intersect1d, timestamps_player_id)

        # 4.4) Filtramos por los timestamps comunes
        transformed_dataset = transformed_dataset[transformed_dataset['timestamp'].isin(common_timestamps)]

        # 5) Agrupamos datos cada 1 segundo
        # 5.1 Obtenemos el nombre de las columnas que son numéricas
        numeric_columns = transformed_dataset.select_dtypes(include=np.number).columns.tolist()

        # 5.2) Agrupamos y calculamos la media
        transformed_dataset = transformed_dataset.groupby([pd.Grouper(key='timestamp', freq='1S'), 'player_id'])[numeric_columns].mean().reset_index()

        
        # 6) Transformamos los datos de latitud y longitud a X e Y en metros
        # Tomamos el punto de inicio de latitud longitud como el valor mas bajo de cada uno

        # 6.1) Latitud
        min_lat = dataset['lat'].min()
        min_lon = dataset['lon'].min()
        punto_0 = utm.from_latlon(min_lat, min_lon)

        # 6.2) Transformamos a metros
        res = utm.from_latlon(np.asarray(transformed_dataset['lat']), np.asarray(transformed_dataset['lon']))
        transformed_dataset['X'] = res[0]-punto_0[0]
        transformed_dataset['X_filtered'] = transformed_dataset['X']
        transformed_dataset['Y'] = res[1]-punto_0[1]
        transformed_dataset['Y_filtered'] = transformed_dataset['Y']

        # 7) Aplica el filtro de mediana a los datos para cada player_id
        # Agrupa por player_id y aplicamos el filtro de mediana a X e Y

        for player_id in player_ids:

            # 7.2.1) Filtramos por player_id
            df_player = transformed_dataset[transformed_dataset['player_id'] == player_id]

            # 7.2.2) Aplicamos el filtro de mediana a X e Y
            X_filtered = df_player['X'].rolling(window=5, center=True, min_periods=1).median()
            Y_filtered = df_player['Y'].rolling(window=5, center=True, min_periods=1).median()

            # 7.2.3) Sustituimos los valores de X e Y por los filtrados
            transformed_dataset.loc[transformed_dataset['player_id'] == player_id, 'X_filtered'] = X_filtered
            transformed_dataset.loc[transformed_dataset['player_id'] == player_id, 'Y_filtered'] = Y_filtered
            
        # transformed_dataset.to_csv('{directory_path}/test_transformed_dataset.csv')
        return transformed_dataset

    @staticmethod
    def popup_showinfo(title, msg):
        tk.messagebox.showinfo(message=msg, title=title)

    def plot_trajectories(self, dataset):

        # Obtenemos los player_id
        players_ids = dataset['player_id'].unique()

        # Limpiamos el plot space si ya hay algo
        if hasattr(self.ax, 'lines'):
            for line in self.ax.lines:
                line.remove()

        for player_id in players_ids:

            # Plot the X_filtered and Y_filtered in the plot space
            df_player = dataset[dataset['player_id'] == player_id]

            data = self.ax.plot(df_player['X_filtered'], df_player['Y_filtered'], label=player_id, alpha=0.5)

        
        # Show
        self.ax.legend()
        self.plot_space.draw()


def get_metrics(dataset: pd.DataFrame):

    # 1) Calculamos la distancia total recorrida por cada jugador

    # 1.1) Obtenemos los player_id
    player_ids = dataset['player_id'].unique()

    results = []

    # 1.2) Calculamos la distancia total recorrida por cada jugador

    for player_id in player_ids:

        # 1.2.1) Filtramos por player_id
        df_player = dataset[dataset['player_id'] == player_id]

        # 1.2.2) Calculamos la distancia total recorrida como la suma de las distancias entre cada punto
        distancia = 0

        for n in range(len(df_player)-1):
                distancia += np.sqrt((df_player['X_filtered'].iloc[n+1] - df_player['X_filtered'].iloc[n])**2 + (df_player['Y_filtered'].iloc[n+1] - df_player['Y_filtered'].iloc[n])**2)

        tiempo = (df_player['timestamp'].iloc[-1] - df_player['timestamp'].iloc[0]).total_seconds()
        velocidad_media = distancia/tiempo

        results.append((player_id, distancia, velocidad_media))


    # 2) Calculamos la distancia entre cada jugador
    distances_matrix = pd.DataFrame(columns=['timestamp', 'player_id'] + list(player_ids))

    for fecha in dataset['timestamp'].unique():
        fecha_str = fecha.strftime("%d-%m-%Y %H:%M:%S")
        rows_to_add = pd.DataFrame({'timestamp': [fecha_str] * len(player_ids), 'player_id': player_ids})
        distances_matrix = pd.concat([distances_matrix, rows_to_add], ignore_index=True)
        for i in range(len(player_ids)-1):
            for j in range(i + 1, len(player_ids)):
                # Filtrar para que x1 sea el valor del dataset que coincida con el player_id y el timestamp
                x1 = dataset[(dataset['player_id'] == player_ids[i]) & (dataset['timestamp'] == fecha)]['X_filtered'].iloc[0]
                y1 = dataset[(dataset['player_id'] == player_ids[i]) & (dataset['timestamp'] == fecha)]['Y_filtered'].iloc[0]
                x2 = dataset[(dataset['player_id'] == player_ids[j]) & (dataset['timestamp'] == fecha)]['X_filtered'].iloc[0]
                y2 = dataset[(dataset['player_id'] == player_ids[j]) & (dataset['timestamp'] == fecha)]['Y_filtered'].iloc[0]

                distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                distances_matrix.loc[(distances_matrix['player_id'] == player_ids[i]) & (distances_matrix['timestamp'] == fecha_str), player_ids[j]] = distance
                distances_matrix.loc[(distances_matrix['player_id'] == player_ids[j]) & (distances_matrix['timestamp'] == fecha_str), player_ids[i]] = distance
    distances_matrix.fillna(0, inplace=True)

    # distances_matrix.to_csv(f'{directory_path}/test_distances_matrix.csv')
    
    df_results = pd.DataFrame(results, columns=['player_id', 'distancia', 'velocidad_media'])

    return df_results





if __name__ == "__main__":

    
    # sv_ttk.set_theme("dark")
    testObj = windows()
    sv_ttk.set_theme("dark")
    testObj.mainloop()