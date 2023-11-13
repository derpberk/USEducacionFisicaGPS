import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

import utm

plt.switch_backend('TkAgg')

# Load data
df = pd.read_csv(r"DATOS\PRUEBA_4_10_2023\all_data.csv")


interval_of_lat = (37.4101990, 37.4106198)
interval_of_lon = (-6.0025772, -6.0021329)

# Transform to meters the lat lon respecto to the min 

with plt.style.context('bmh'):
    fig, axs = plt.subplots(1, 3, figsize=(5, 5), sharex=True, sharey=True)

    for n, player_id in enumerate(df['player_id'].unique()):
        df_player = df[df['player_id'] == player_id]


        filtered_result = []

        # Print the number of rows
        print(f"Number of points for player {player_id}: {len(df_player)}")


        # Filter out the rows ion the interval of lat lon
        df_player = df_player[(df_player['lat'] > interval_of_lat[0]) & (df_player['lat'] < interval_of_lat[1])]
        df_player = df_player[(df_player['lon'] > interval_of_lon[0]) & (df_player['lon'] < interval_of_lon[1])]

        res = utm.from_latlon(np.asarray(df_player['lat']), np.asarray(df_player['lon']))

        res_0= utm.from_latlon(interval_of_lat[0], interval_of_lon[0])

        df_player['X'] = res[0]-res_0[0]
        df_player['Y'] = res[1]-res_0[1]

        # Print the number of rows
        print(f"Number of points for player after filtering {player_id}: {len(df_player)}")

        

        f_lat = KalmanFilter(dim_x=1, dim_z=1)
        f_lon = KalmanFilter(dim_x=1, dim_z=1)
        f_angle = KalmanFilter(dim_x=1, dim_z=1)

        f_lat.x = np.array([df_player['X'].iloc[0]])
        f_lon.x = np.array([df_player['Y'].iloc[0]]) 
        f_angle.x = np.array([df_player['heading'].iloc[0]])

        f_lat.F = np.array([[1.]])
        f_lon.F = np.array([[1.]])
        f_angle.F = np.array([[1.]])

        f_lat.H = np.array([[1.]])
        f_lon.H = np.array([[1.]])
        f_angle.H = np.array([[1.]])

        f_lat.P *= 10.0
        f_lon.P *= 10.0
        f_angle.P *= 10.0

        f_lat.R = 100
        f_lon.R = 100
        f_angle.R = 10


        for lat,lon,angle in zip(df_player['X'], df_player['Y'], df_player['heading']):
            f_lat.predict()
            f_lon.predict()
            f_angle.predict()
            f_lat.update(np.array([[lat]]))
            f_lon.update(np.array([[lon]]))
            f_angle.update(np.array([[angle]]))
            filtered_result.append((f_lat.x, f_lon.x, f_angle.x))
        
        filtered_result = np.array(filtered_result)

        """
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
 
        # Set lims
        ax.set_xlim([0, len(filtered_result)])
        ax.set_ylim([0, 365])

        
        d1=  ax.plot(0,filtered_result[0,2], alpha=1.0, linewidth=2, color='red', label=f"{player_id} original")


        for i in range(len(filtered_result)):
            d1[0].set_data(filtered_result[0:i,0], filtered_result[0:i,1])
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.001) 
        """
                

        # Set plt stle
        axs[n].plot(df_player['X'], df_player['Y'], alpha=0.5, linewidth=3, color='red', label=f"{player_id} original")
        axs[n].plot(filtered_result[:,0], filtered_result[:,1], alpha=1.0, linewidth=1.0, color='blue', label=f"{player_id} filtered")
        axs[n].legend()
        axs[n].set_xlabel("X(m)")
        axs[n].set_ylabel("Y(m)")
        # Asign the equal ratio
        axs[n].set_aspect('equal', 'box')

        


    plt.show()




