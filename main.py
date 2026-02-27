import pandas as pd
import numpy as np
import plotly.graph_objs as go

folder = 'C:/Users/noturno/Desktop/LucasTrindade/AirBnB_Analisys/'
t_ny = 'ny.csv'
t_rj = 'rj.csv'
t_bsw = 'listings.csv'
t_ct = 'ct.csv'

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
    out['lon'] = pd.to_numeric(df[lon_col], errors='coerce')
    out['custo'] = pd.to_numeric(df[cost_col], errors='coerce') if cost_col is not None else np.nan
    out['nome'] = df[name_col].astype(str) if name_col is None else [f"Ponto {i}" for i in range(len(df))]

    out = out.dropna(subset=['lat', 'lon']).reset_index(drop=True) # apagar qualquer subset ou linha vazia no lat e long. reset_index(drop=True) vai fazer a linha debaixo da apagada subir para a apagada.

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
        size = np.full_like(c, 10.0, dtype=float)

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
        name = f"{name} - Pontos",
        hovertemplate = hover,
        customdata = custom
    )

def make_density_trace(df: pd.DataFrame, name: str) -> go.Densitymapbox:
    return go.Densitymapbox(
        lat = df['lat'],
        lon = df['lon'],
        z = df['custo'],
        radius = 20,
        colorscale = 'Inferno', 
        name = f"{name} - Pontos",
        showscale = True,
        colorbar = dict(title = 'Custo')
    )

def main():
    # carregar e padronizar os dados!
    ny = standartize_columns(pd.read_csv(f"{folder}{t_ny}"))
    rj = standartize_columns(pd.read_csv(f"{folder}{t_rj}"))
    bsw = standartize_columns(pd.read_csv(f"{folder}{t_bsw}"))
    ct = standartize_columns(pd.read_csv(f"{folder}{t_ct}"))

    # cria os quatro races )ny pontos / ny calor / rj pontos / rj calor)
    ny_point = make_point_trace(ny, "Nova York")
    ny_heat = make_density_trace(ny, "Nova York")
    rj_point = make_point_trace(rj, "Rio de Janeiro")
    rj_heat = make_density_trace(rj, "Rio de Janeiro")
    bsw_point = make_point_trace(bsw, "Barwon South West")
    bsw_heat = make_density_trace(bsw, "Barwon South West")
    ct_point = make_point_trace(ct, "Cape Town")
    ct_heat = make_density_trace(ct, "Cape Town")

    fig = go.Figure([ny_point, ny_heat, rj_point, rj_heat, bsw_point, bsw_heat, ct_point, ct_heat])

    fig.data[1].visible = False
    fig.data[2].visible = False
    fig.data[3].visible = False
    fig.data[4].visible = False
    fig.data[5].visible = False
    fig.data[6].visible = False
    fig.data[7].visible = False

    def update_map_layout(df, zoom):
        return {
            "mapbox.center": city_center(df),
            "mapbox.zoom": zoom
        }

    def center_zoom(df, zoom):
        return dict(center = city_center(df), zoom = zoom)
    
    buttons = [
        dict(
            label = "Nova York - Pontos",
            method = "update",
            args = [
                {"visible":[True, False, False, False, False, False, False, False]},
                update_map_layout(ny, 9)
            ]
        ),
        dict(
            label = "Nova York - Calor",
            method = "update",
            args = [
                {"visible":[False, True, False, False, False, False, False, False]},
                update_map_layout(ny, 9)
            ]
        ),
        dict(
            label = "Rio de Janeiro - Pontos",
            method = "update",
            args = [
                {"visible":[False, False, True, False, False, False, False, False]},
                update_map_layout(rj, 10)
            ]
        ),
        dict(
            label = "Rio de Janeiro - Calor",
            method = "update",
            args = [
                {"visible":[False, False, False, True, False, False, False, False]},
                update_map_layout(rj, 10)
            ]
        ),
        dict(
            label = "Barwon South West - Pontos",
            method = "update",
            args = [
                {"visible":[False, False, False, False, True, False, False, False]},
                update_map_layout(bsw, 11)
            ]
        ),
        dict(
            label = "Barwon South West - Calor",
            method = "update",
            args = [
                {"visible":[False, False, False, False, False, True, False, False]},
                update_map_layout(bsw, 11)
            ]
        ),
        dict(
            label = "Cape Town - Ponto",
            method = "update",
            args = [
                {"visible":[False, False, False, False, False, False, True, False]},
                update_map_layout(ct, 12)
            ]
        ),
        dict(
            label = "Cape Town - Calor",
            method = "update",
            args = [
                {"visible":[False, False, False, False, False, False, False, True]},
                update_map_layout(ct, 12)
            ]
        )
    ]

    fig.update_layout(
        title = "Mapa interativo de Custos - Pontos e Mapa de Calor",
        mapbox_style = "open-street-map",
        mapbox = dict(center = city_center(rj), zoom = 10),
        margin = dict(l = 10, r = 10, t = 50, b = 10),
        updatemenus = [dict(
            buttons = buttons,
            direction = "down",
            x = 0.01,
            y = 0.99,
            xanchor = "left", 
            yanchor = "top",
            bgcolor = "white",
            bordercolor = "lightgray"
        )],
        legend = dict(
            orientation = 'h',
            yanchor = "bottom",
            xanchor = "right",
            y = 0.01,
            x = 0.99
        )
    )

    # Salva o HTML de apresentação
    fig.write_html(f"{folder}mapa_custos_interativos.html", include_plotlyjs = 'cdn', full_html = True)
    print(f"Arquivo gerado com sucesso em: {folder}mapa_custo_interativos.html")

    # Inicia o servidor:
if __name__ == '__main__':
    main()