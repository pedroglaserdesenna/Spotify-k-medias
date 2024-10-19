import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Credenciais
client_id = '48878443a03d418494ed63d658196de8'
client_secret = '96d0dfacf4ba469f8cda39032fbb0e37'

# Autenticação
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)) 

# Dicionário para armazenar as músicas
musicas = {
    'nome':[],
    'id':[],
    'danceability':[],
    'energy':[],
    'key':[],
    #'loudness':[],
    #'mode':[],
    'speechiness':[],
    #'acousticness':[],
    'instrumentalness':[],
    #'liveness':[],
    'valence':[],
    'tempo':[]
    }

# Funcao para pegar as musicas da playlist
def get_playlist(playlist_id):
    playlist = sp.playlist_tracks(playlist_id)
    for musica in playlist['items']:
        musicas['nome'].append(musica['track']['name'])
        musicas['id'].append(musica['track']['id'])
    return musicas

# Funcao para pegar os parametros das musicas
def get_parametros(musicas):
    for id_musica in musicas['id']:
        features = sp.audio_features(id_musica)[0]
        musicas['danceability'].append(features['danceability'])
        musicas['energy'].append(features['energy'])
        musicas['key'].append(features['key'])
        #musicas['loudness'].append(features['loudness'])
        #musicas['mode'].append(features['mode'])
        musicas['speechiness'].append(features['speechiness'])
        #musicas['acousticness'].append(features['acousticness'])
        musicas['instrumentalness'].append(features['instrumentalness'])
        #musicas['liveness'].append(features['liveness'])
        musicas['valence'].append(features['valence'])
        musicas['tempo'].append(features['tempo'])
    return musicas

# Teste
playlist_id = '4W9cv1W6Tk4kk2jbfzKbsO'
musicas = get_playlist(playlist_id)
get_parametros(musicas)

df_musicas = pd.DataFrame(musicas)
print(df_musicas)

# Escalando as colunas numéricas
scaler = StandardScaler()
data_scaled = scaler.fit_transform(musicas[['danceability', 'energy', 'key', 'speechiness', 'instrumentalness', 'valence', 'tempo']])  

# Definindo o número de clusters
k = 2  # Número de clusters pode ser ajustado
kmeans = KMeans(n_clusters=k, random_state=42)

# Atribuindo os clusters ao musicasFrame
musicas['cluster'] = kmeans.fit_predict(musicas_scaled)

weights = {
    'danceability': 1,
    'energy': 1,
    'key': 1,
    'speechiness': 1,
    'instrumentalness': 1,
    'valence': 1,
    'tempo': 1
}

# Aplicando os pesos
musicas_weighted = musicas[['danceability', 'energy', 'key', 'speechiness', 'instrumentalness', 'valence', 'tempo']].copy()
for metric, weight in weights.items():
    musicas_weighted[metric] = musicas_weighted[metric] * weight

# Escalando as colunas numéricas
scaler = StandardScaler()
musicas_scaled = scaler.fit_transform(musicas_weighted)

# Definindo o número de clusters
k = 2  # Número de clusters pode ser ajustado
kmeans = KMeans(n_clusters=k, random_state=42)

# Atribuindo os clusters ao musicasFrame
musicas['cluster'] = kmeans.fit_predict(musicas_scaled)

for i in range(k):
    print(f"Cluster {i}:")
    print(musicas[musicas['cluster'] == i][['nome','BPM', 'danceability', 'energy', 'valence']])
    print("\n")