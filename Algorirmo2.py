import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Credenciais para autenticação com permissões de usuário
client_id = '48878443a03d418494ed63d658196de8'
client_secret = '96d0dfacf4ba469f8cda39032fbb0e37'
redirect_uri = 'http://localhost:8888/callback'

# Escopo necessário para acessar as faixas salvas do usuário e modificar playlists
scope = 'user-library-read playlist-modify-private playlist-modify-public user-top-read'

# Autenticação com OAuth para acessar a biblioteca do usuário
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope,
                                               show_dialog=True))


# Dicionário para armazenar as músicas salvas
musicas = {
    'nome': [],
    'id': [],
    'danceability': [],
    'energy': [],
    'speechiness': [],
    'loudness': [],
    'valence': [],
    'tempo': []
}

# Função para obter as 100 músicas mais ouvidas do usuário
def get_top_tracks():
    offset = 0
    while offset < 100: 
        results = sp.current_user_top_tracks(limit=50, offset=offset)
        if len(results['items']) == 0:
            break
        for track in results['items']:
            musicas['nome'].append(track['name'])
            musicas['id'].append(track['id'])
        offset += 50  
    return musicas

# Função para obter os parâmetros das músicas, com verificação de nulos
def get_parametros(musicas):
    for id_musica in musicas['id']:
        features = sp.audio_features(id_musica)[0]
        if features:  # Verifica se os audio features estão disponíveis
            musicas['danceability'].append(features['danceability'])
            musicas['energy'].append(features['energy'])
            musicas['speechiness'].append(features['speechiness'])
            musicas['loudness'].append(features['loudness'])
            musicas['valence'].append(features['valence'])
            musicas['tempo'].append(features['tempo'])
        else:
            # Se não houver dados, insere None ou um valor padrão
            musicas['danceability'].append(None)
            musicas['energy'].append(None)
            musicas['key'].append(None)
            musicas['speechiness'].append(None)
            musicas['loudness'].append(None)
            musicas['valence'].append(None)
            musicas['tempo'].append(None)
    return musicas

# Obtendo as músicas salvas
musicas = get_top_tracks()
get_parametros(musicas)

# Convertendo para DataFrame
df_musicas = pd.DataFrame(musicas)
print(df_musicas)

# Escalando as colunas numéricas, ignorando valores nulos
scaler = StandardScaler()
musicas_scaled = scaler.fit_transform(df_musicas[['danceability', 'energy', 'speechiness', 'loudness', 'valence', 'tempo']].fillna(0))

# Definindo o número de clusters
k = 5 
kmeans = KMeans(n_clusters=k, random_state=42)

# Atribuindo os clusters ao DataFrame
df_musicas['cluster'] = kmeans.fit_predict(musicas_scaled)

# Função para criar playlists para cada cluster
def create_playlists_for_clusters(sp, df_musicas, user_id):
    for i in range(k):
        # Criar uma nova playlist
        playlist_name = f'Cluster {i + 1}'
        playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
        playlist_id = playlist['id']
        
        # Obter os IDs das músicas no cluster
        track_ids = df_musicas[df_musicas['cluster'] == i]['id'].tolist()
        
        # Adicionar as músicas à nova playlist
        if track_ids:  # Verifica se existem músicas no cluster
            sp.playlist_add_items(playlist_id, track_ids)
            print(f'Músicas do {playlist_name} adicionadas à playlist.')
        else:
            print(f'O {playlist_name} não contém músicas.')

# Obtendo o ID do usuário
user_id = sp.current_user()['id']

# Criando playlists para cada cluster
create_playlists_for_clusters(sp, df_musicas, user_id)

