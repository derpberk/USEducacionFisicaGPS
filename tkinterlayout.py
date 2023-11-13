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

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from matplotlib.figure import Figure as MatplotlibFigure

import matplotlib.pyplot as plt

dataframe = None

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
        container = ttk.Frame(self, height=750, width=600)

        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames themselves later but let's add the components to the dictionary.
        for num, F in enumerate((MainPage, Analisis)):
            frame = F(container, self)
            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Configuracion de datos", font=("Arial", 12, "bold"))
        self.label.place(x=10, y=10)

        # Image logo
        img = Image.open("aceti.png")
        img = img.resize((140, 60))
        img = ImageTk.PhotoImage(img)
        self.logo = tk.Label(self, image=img)
        self.logo.image = img
        self.logo.place(x=700, y=10)

        # Boton para seleccionar el archivo

        self.directory_path = None
        self.select_directory = ttk.Button(self, text="Seleccionar carpeta", command=self.browse_button)
        self.select_directory.place(x=10, y=70)

        # Label para mostrar el path
        self.directory_label = ttk.Label(self, text="Seleccione la ruta con los archivos", width=90)
        self.directory_label.place(x=170, y=75)

        # Caja de dialogo
        self.dialog_box = scrolledtext.ScrolledText(self, undo=True, width=80, height=20)
        self.dialog_box.insert(tk.END, "Selecciona un archivo de datos o una carpeta")
        self.dialog_box.config(state=tk.DISABLED)
        self.dialog_box.place(x = 170, y = 100)


        # Boton para leer los archivos, pasarlos a pandas y convertirlos #
        self.convert_button = ttk.Button(
            self,
            text="Crear dataset",
            command=self.convert_files_fn,
        )
        self.convert_button.place(x=10, y = 120)

        # Boton para cargar un dataset completo #
        self.load_button = ttk.Button(
            self,
            text="Cargar dataset",
            command=self.load_button_fn,
        )
        self.load_button.place(x=10, y = 160)

        # Boton para cargar un dataset completo #
        self.save_button = ttk.Button(
            self,
            text="Guardar dataset",
            command=self.save_button_fn,
        )

        self.save_button.place(x=10, y = 200)

        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = ttk.Button(
            self,
            text="Análisis de datos",
            command=lambda: controller.show_frame(Analisis),
        )

        switch_window_button.pack(side="bottom", fill=tk.X)

    def load_button_fn(self):

        global dataframe

        # Cargar dataset
        file_path_hanlder = filedialog.askopenfile()
        

        if file_path_hanlder is not None:

            file_path = file_path_hanlder.name

            if file_path[-4:] == '.csv':

                dataframe = pd.read_csv(file_path)
                self.dialog("Se ha cargado un nuevo archivo de: " + file_path)

            else:
                self.popup_showinfo("Error", "No es un archivo valido.")

    def save_button_fn(self):

        global dataframe

        file_path = filedialog.askdirectory()

        print(file_path)

        if file_path is not None and dataframe is not None and file_path != "":

            try: 
                dataframe.to_csv(file_path + '/all_data.csv')
                self.dialog("Dataset guardado en: " + file_path + '/all_data.csv')

            except:
                self.popup_showinfo("Error", "Ha habido un error en el guardado.")


    def dialog(self, text):

        self.dialog_box.config(state = tk.NORMAL)
        self.dialog_box.insert(tk.END, "\n")
        self.dialog_box.insert(tk.END, text)
        self.dialog_box.see("end")
        self.dialog_box.config(state = tk.DISABLED)


    def convert_files_fn(self):

        global dataframe

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

            self.dialog(f"Se han encontrado {len(csv_files)} archivos!")

            if len(csv_files) == 0:
                self.popup_showinfo("Error", "No hay ningún archivo csv en el directorio.")

            else:

                datafiles = []

                for n, file in enumerate(csv_files):
                    name = file[:-4]
                    df = pd.read_csv(self.directory_path + '/' + file)
                    df['player_id'] = name
                    datafiles.append(df.copy())

                    self.dialog(f"Leyendo archivo {n+1}/{len(csv_files)}: {file}")

                dataframe = pd.concat(datafiles, ignore_index=True)

                # Save dataframe
                
                new_file_name = self.directory_path + '/all_data.csv'
                dataframe.to_csv(new_file_name)
                self.dialog(f"Experimento guardado en: {new_file_name}")

    @staticmethod
    def popup_showinfo(title, msg):
        tk.messagebox.showinfo(message=msg, title=title)

    def browse_button(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        self.directory_path = filedialog.askdirectory()
        if self.directory_path is not None:
            self.directory_label.configure(text=self.directory_path)

        print(self.directory_path)

class Analisis(tk.Frame):


    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # Titulo
        self.label = ttk.Label(self, text="Analisis de resultados", font=("Arial", 12, "bold"))
        self.label.place(x=10, y=10)

        switch_window_button = ttk.Button(
            self,
            text="Carga de datos",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

        # Boton para seleccionar el archivo
        self.analyze_results_button = ttk.Button(
            self,
            text="Analizar resultados",
            command=self.analyze_results_fn,
        )
        self.analyze_results_button.place(x=10, y=70)

        
        self.date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=1)
        self.date_entry.place(x=10, y=110)

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


    def analyze_results_fn(self):

        global dataframe

        if dataframe is None:
            self.popup_showinfo("Error", "No hay ningún archivo cargado.")

        else:

            # Filtramos y curamos los datos #
            transformed_dataset = self.transform_dataset(dataframe, self.date_entry.get_date())

            if transformed_dataset is not None:
                # Sacamos las metricas más importantes #
                metrics = get_metrics(transformed_dataset)

            print(metrics)

            # Plot the trajectories
            self.plot_trajectories(transformed_dataset)


    def transform_dataset(self, dataset: pd.DataFrame, date=None):
        """ Cura el dataset para que sea más facil de analizar """

        transformed_dataset = dataset.copy()

        if date is None:
            # Raise a warning
            self.popup_showinfo("Error", "No hay ninguna fecha seleccionada.")

            return None
        

        # 1) Transformamos las fechas en milisegundos
        transformed_dataset['timestamp'] = pd.to_datetime(dataset['timestamp'])

        #print(dataset['timestamp'].dt.date)

        # 2) Ordenamos por fecha
        transformed_dataset = transformed_dataset.sort_values(by=['timestamp'])

        # Cambiamos el formato de la fecha a YYYY-MM-DD
        transformed_dataset['timestamp'] = pd.to_datetime(transformed_dataset['timestamp'], format='%Y-%m-%d %H:%M:%S')

        # 3) Filtramos por fecha
        date = pd.to_datetime(date, format='%Y-%m-%d')
        transformed_dataset = transformed_dataset[transformed_dataset['timestamp'].dt.date == date.date()]

        if len(dataset) == 0:
            # Raise a warning
            self.popup_showinfo("Error", "No hay ningún dato para esa fecha.")

            return None

        # 3) Transformamos los datos de latitud y longitud a X e Y en metros
        # Tomamos el punto de inicio de latitud longitud como el valor mas bajo de cada uno

        # 3.1) Latitud
        min_lat = dataset['lat'].min()
        min_lon = dataset['lon'].min()
        punto_0 = utm.from_latlon(min_lat, min_lon)

        # 3.2) Transformamos a metros
        res = utm.from_latlon(np.asarray(transformed_dataset['lat']), np.asarray(transformed_dataset['lon']))
        transformed_dataset['X'] = res[0]-punto_0[0]
        transformed_dataset['X_filtered'] = transformed_dataset['X']
        transformed_dataset['Y'] = res[1]-punto_0[1]
        transformed_dataset['Y_filtered'] = transformed_dataset['Y']

        # 4) Aplica el filtro de mediana a los datos para cada player_id
        # 4.1) Obtenemos los player_id
        player_ids = transformed_dataset['player_id'].unique()

        # 4.2) Agrupa por player_id y aplicamos el filtro de mediana a X e Y

        for player_id in player_ids:

            # 4.2.1) Filtramos por player_id
            df_player = transformed_dataset[transformed_dataset['player_id'] == player_id]

            # 4.2.2) Aplicamos el filtro de mediana a X e Y
            X_filtered = df_player['X'].rolling(window=5, center=True, min_periods=1).median()
            Y_filtered = df_player['Y'].rolling(window=5, center=True, min_periods=1).median()

            # 4.2.3) Sustituimos los valores de X e Y por los filtrados
            transformed_dataset.loc[transformed_dataset['player_id'] == player_id, 'X_filtered'] = X_filtered
            transformed_dataset.loc[transformed_dataset['player_id'] == player_id, 'Y_filtered'] = Y_filtered
            

        return transformed_dataset

    @staticmethod
    def popup_showinfo(title, msg):
        tk.messagebox.showinfo(message=msg, title=title)

    def plot_trajectories(self, dataset):

        # 1) Obtenemos los player_id

        players_ids = dataset['player_id'].unique()

        for player_id in players_ids:

            # Plot the X_filtered and Y_filtered in the plot space
            df_player = dataset[dataset['player_id'] == player_id]

            self.ax.plot(df_player['X_filtered'], df_player['Y_filtered'], label=player_id, alpha=0.5)

        
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

    df_results = pd.DataFrame(results, columns=['player_id', 'distancia', 'velocidad_media'])

    return df_results





if __name__ == "__main__":

    
    # sv_ttk.set_theme("dark")
    testObj = windows()
    sv_ttk.set_theme("dark")
    testObj.mainloop()