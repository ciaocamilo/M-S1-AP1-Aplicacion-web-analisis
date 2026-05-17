# Carga y transformación de datos
import re
import pandas as pd
import json

# 1. Carga
# utf-8-sig elimina el BOM presente en algunos archivos exportados desde Excel
# sep=None + engine='python' detecta automáticamente el delimitador (,  ó  ;)
df_codigos_muerte = pd.read_csv(
    'data/CodigosDeMuerte_CE_15-03-23.csv',
    encoding='utf-8-sig', sep=None, engine='python'
)
df_divipola = pd.read_csv(
    'data/Divipola_CE_ .csv',
    encoding='utf-8-sig', sep=None, engine='python'
)
df_grupo_edad = pd.read_csv(
    'data/Grupo_edad.csv',
    encoding='utf-8-sig', sep=None, engine='python'
)
df_nofetal = pd.read_csv(
    'data/NoFetal2019_CE_15-03-23.csv',
    encoding='utf-8-sig', sep=None, engine='python'
)

with open('data/Colombia.geo.json', encoding='utf-8') as f:
    geo_colombia = json.load(f)

# 2. CodigosDeMuerte
df_codigos_muerte.drop(columns=['Unnamed: 6'], inplace=True)
df_codigos_muerte.columns = [c.strip() for c in df_codigos_muerte.columns]
df_codigos_muerte.rename(columns={
    'Nombre capítulo': 'CAPITULO_NOMBRE',
    'Código de la CIE-10 tres caracteres': 'COD_CIE10_3',
    'Descripción  de códigos mortalidad a tres caracteres': 'DESC_CIE10_3',
    'Código de la CIE-10 cuatro caracteres': 'COD_CIE10_4',
    'Descripcion  de códigos mortalidad a cuatro caracteres': 'DESC_CIE10_4',
}, inplace=True)

# 3. Divipola
df_divipola['COD_DANE'] = df_divipola['COD_DANE'].astype(str).str.zfill(5)
df_divipola['COD_DEPARTAMENTO'] = df_divipola['COD_DEPARTAMENTO'].astype(str).str.zfill(2)
df_divipola['FECHA1erFIS'] = pd.to_datetime(
    df_divipola['FECHA1erFIS'], dayfirst=True, errors='coerce'
)

# 4. Grupo_edad: expandir rangos "a–b" a mapa entero → categoría
def _build_grupo_edad_map(df):
    mapping = {}
    for _, row in df.iterrows():
        rango = str(row['GRUPO_EDAD1']).strip()
        categoria = row['Categoría']
        partes = re.split(r'[–\-]', rango)   # soporta guión y en-dash
        if len(partes) == 2:
            for i in range(int(partes[0].strip()), int(partes[1].strip()) + 1):
                mapping[i] = categoria
        else:
            mapping[int(rango)] = categoria
    return mapping

grupo_edad_map = _build_grupo_edad_map(df_grupo_edad)

# 5. NoFetal2019
# Códigos geográficos como strings con ceros iniciales (estándar DANE)
df_nofetal['COD_DANE'] = df_nofetal['COD_DANE'].astype(str).str.zfill(5)
df_nofetal['COD_DEPARTAMENTO'] = df_nofetal['COD_DEPARTAMENTO'].astype(str).str.zfill(2)

# Sexo: códigos numéricos → etiquetas
df_nofetal['SEXO'] = df_nofetal['SEXO'].map(
    {1: 'Masculino', 2: 'Femenino', 3: 'Indeterminado'}
)

# Categoría de edad a partir del mapa expandido
df_nofetal['CATEGORIA_EDAD'] = df_nofetal['GRUPO_EDAD1'].map(grupo_edad_map)

# Estado civil: el único nulo se registra como "Sin información" (código 0)
df_nofetal['ESTADO_CIVIL'] = df_nofetal['ESTADO_CIVIL'].fillna(0).astype(int)

# Enriquecer con nombre de municipio y departamento desde Divipola
df_nofetal = df_nofetal.merge(
    df_divipola[['COD_DANE', 'DEPARTAMENTO', 'MUNICIPIO']],
    on='COD_DANE', how='left'
)

# Enriquecer con descripción CIE-10 y capítulo desde CodigosDeMuerte
df_nofetal = df_nofetal.merge(
    df_codigos_muerte[['COD_CIE10_4', 'DESC_CIE10_4', 'CAPITULO_NOMBRE']],
    left_on='COD_MUERTE', right_on='COD_CIE10_4', how='left'
).drop(columns=['COD_CIE10_4'])

# 6. Conjuntos pre-agregados para los 7 gráficos

# Mapa: total de muertes por departamento
muertes_por_dpto = (
    df_nofetal
    .dropna(subset=['COD_DEPARTAMENTO', 'DEPARTAMENTO'])
    .groupby(['COD_DEPARTAMENTO', 'DEPARTAMENTO'])
    .size()
    .reset_index(name='TOTAL_MUERTES')
)

# Gráfico de líneas: muertes por mes (Colombia total)
muertes_por_mes = (
    df_nofetal
    .groupby('MES')
    .size()
    .reset_index(name='TOTAL_MUERTES')
    .sort_values('MES')
)

# Gráfico de barras: top 5 ciudades más violentas (código X95 – homicidios)
_mask_x95 = (
    df_nofetal['COD_MUERTE']
    .fillna('')
    .astype(str)
    .str.strip()
    .str.startswith('X95')
)
ciudades_violentas_top5 = (
    df_nofetal[_mask_x95]
    .dropna(subset=['MUNICIPIO'])
    .groupby('MUNICIPIO')
    .size()
    .reset_index(name='HOMICIDIOS')
    .sort_values('HOMICIDIOS', ascending=False)
    .head(5)
)

# Gráfico circular: 10 ciudades con menor índice de mortalidad
ciudades_menor_mortalidad = (
    df_nofetal
    .dropna(subset=['MUNICIPIO'])
    .groupby('MUNICIPIO')
    .size()
    .reset_index(name='TOTAL_MUERTES')
    .sort_values('TOTAL_MUERTES')
    .head(10)
)

# Tabla: top 10 causas de muerte (agrupado por código individual)
_desc_map = (
    df_nofetal[['COD_MUERTE', 'DESC_CIE10_4']]
    .dropna(subset=['DESC_CIE10_4'])
    .drop_duplicates('COD_MUERTE')
    .set_index('COD_MUERTE')['DESC_CIE10_4']
)
_causas_count = (
    df_nofetal
    .groupby('COD_MUERTE')
    .size()
    .reset_index(name='TOTAL')
    .sort_values('TOTAL', ascending=False)
    .head(10)
    .reset_index(drop=True)
)
_causas_count['DESC_CIE10_4'] = (
    _causas_count['COD_MUERTE'].map(_desc_map).fillna('Sin descripción')
)
top10_causas = _causas_count[['COD_MUERTE', 'DESC_CIE10_4', 'TOTAL']].copy()

# Gráfico de barras apiladas: muertes por sexo en cada departamento
muertes_sexo_dpto = (
    df_nofetal
    .dropna(subset=['DEPARTAMENTO', 'SEXO'])
    .groupby(['DEPARTAMENTO', 'SEXO'])
    .size()
    .reset_index(name='TOTAL_MUERTES')
)

# Histograma: muertes por categoría de edad (orden cronológico de vida)
_ORDEN_EDAD = [
    'Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia',
    'Niñez', 'Adolescencia', 'Juventud',
    'Adultez temprana', 'Adultez intermedia', 'Vejez',
]
_conteo_edad = df_nofetal['CATEGORIA_EDAD'].value_counts()
muertes_grupo_edad = pd.DataFrame({
    'CATEGORIA_EDAD': _ORDEN_EDAD,
    'TOTAL_MUERTES': [int(_conteo_edad.get(c, 0)) for c in _ORDEN_EDAD],
})

# Dropdown: filtro por manera de muerte (todas las disponibles en los datos)
_maneras = (
    df_nofetal['MANERA_MUERTE']
    .dropna()
    .value_counts()
    .index
    .tolist()
)
opciones_causa = [{'label': 'Todas las muertes', 'value': 'ALL'}] + [
    {'label': manera, 'value': manera} for manera in _maneras
]
