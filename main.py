import pandas as pd
import numpy as np
import plotly.graph_objs as go

folder = 'C:/Users/noturno/Desktop/LucasTrindade/AirBnB_Analisys/'
t_ny = 'ny.csv'
t_rj = 'rj.csv'

def standartize_columns(df: pd.DataFrame) -> pd.DataFrame: 
    '''
    Tenta detectar as colunas latitude e logintude, custo e nome
    aceita varias nomes comuns como lat/latitude custo, valor, etc
    Preenche custos ausentes com a mediana (ou 1 se tudo for ausente)
    '''

    df = df.copy()

    lat_candidates = ['lat', 'latitude', 'Latitude', 'Lat', 'LATITUDE']
    lon_candidates = ['LON', 'lon', 'Longitude', 'Long', 'Lng', 'longitude']
    cost_candidates = ['custo', 'cost', 'preço', 'preco', 'price', 'valor', 'valor_total']
    name_candidates = ['nome', 'descricao', 'titulo', 'name', 'title', 'local', 'place']

    def pick(colnames, candidates):
        # colnames: lista de nomes das colunas da tabela
        # candidates: lista de possíveis nomes de colunas a serem encontrados

        for c in candidates:
            # percorre da candidato (c) dentro da lista de cancidatos
            if c in colnames:
                # se o candidato for exatamente igual a um dos nomes de colunas em colnames
                return c
            #... retorna esse candidato imediatamente
        for c in candidates:
            # se não encontrou a correspondencia exata percorre novamente cada candidato
            for col in colnames:
                # aqui percorre cada nome da coluna
                if c.lower() in col.lower():
                    # faz igual o de cima, mas trabalhando em minusculos apenas
                    return col
        return None
        # se nao encontrou nada nem exato nem parcial, retorna None (nenhum match encontrado)

    lat_col = pick(df.columns, lat_candidates)
    lon_col = pick(df.columns, lon_candidates)
    cost_col = pick(df.columns, cost_candidates)
    name_col = pick(df.columns, name_candidates)

    if lat_col is None or lon_col is None:
        raise ValueError(f'Não encontrei colunas de latitude e/ou longitude na lista de colunas {list(df.columns)}')
    
    out = pd.DataFrame() # criou o dataframe do 0
    out['lat'] = pd.to_numeric(df[lat_col], errors='coerce') # aqui voce ta criando a coluna lat e ta puxando a coluna lat_col e forçando ele a ser númerico
    out['ion'] = pd.to_numeric(df[lon_col], errors='coerce')
    out['custo'] = pd.to_numeric(df[cost_col], errors='coerce') if cost_col is not None else np.nan
    out['nome'] = df[name_col].astype(str) if name_col is None else ["Ponto {i}" for i in range(len(df))]

    out = out.dropna(subset=['lat', 'long']).reset_index(drop=True) # apagar qualquer subset ou linha vazia no lat e long. reset_index(drop=True) vai fazer a linha debaixo da apagada subir para a apagada.

    # preenche o custo ausente com a mediana
    if out['custo'].notna().any(): # any é em qualquer caso
        med = float(out['custo'].median())
        if not np.isfinite(med):
            med = 0.1
        out['custo'] = out['custo'].fillna(med) # preenche quem ta vazio
    else:
        out['custo'] = 0.1
        return out

def city_center(df: pd.DataFrame) -> dict:
    return dict(
        lat = float(df['lat'].mean()),
        lon = float(df['lon'].mean())
    )

#------------------------------ TRACES -------------------------------
def make_point_trace(df: pd.DataFrame, name:str) -> go.Scattermapbox:
    hover = ("<b>{customdata[0]}</b><br>"
             "custo: %{customdata[1]}"
             "Lat:%{lat:.5f} - Lon:%{lon:.5f}"
             )
    
    # tamanho dos marcadores (normalizados pelo custo)
    c = df["custo"].astype(float).values
    c_min, c_max = float(np.min(c)), float(np.max(c))

    # Caso Especial: se não existirem valores numericos ou se todos os custos forem praticamente iguais (diferença menor que 1e -9)
    # criar m array de tamanho fixo 10 para todos os pontos

if not np.isfinite(c_min) or not np.isfinite(c_max) or abs(c_max - c_min) < 1e-9:
    sizze = np.full_like(c, 10.0, dtype=float)
else:
# Caso Normal: normaliza os custos para o intervalo [0,1] e escala para variar entre 6 e 26 (20 de amplitude mais deslocamento de 6) pontos de custo ~6, ponto de custo alto ~26
    size = (c - c_min) / (c_max) * 20 + 6
    # mesmo que os dados estejam fora da faixa de 6,26, ele evita a sua apresentação, forçando a ficar entre o intervalo
sizes = np.clip(size, 6, 26)

custom = np.stack([df['nome'].values, df['custo'].values], axis=1)
return go.Scattermapbox(
    lat = df['lat'],
    lon = df['lon'],
    mode = 'markers',
    marker = dict(
        size = sizes,
        color = df['custo'],
        colorscale = "Viridis",
        colorbar = dict(title = 'custo')
    ),
    name = f"{name} - Pontos"
    hovertemplate = hover,
    customdata = custom
)