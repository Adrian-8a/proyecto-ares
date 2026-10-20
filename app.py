import pandas as pd
from flask import Flask, render_template, request
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from sklearn import preprocessing
from thefuzz import process

# Instances for FE
labelE = preprocessing.LabelEncoder()
scaler = MinMaxScaler()

# Important functions
def tagToIndex(tag):
    r = df[df['tag'] == tag].index
    return r[0]

def findTag(text):
    text = text.strip().upper()
    if not text.startswith('#'):
        text = '#' + text
    if text in tags:
        return text
    return process.extractOne(text, df['tag'].values)[0]

def listToTag(a,b):
    data = []

    for i in range(len(a[0])-1):
        r = b[0][i+1]
        data.append({
            'name': df.iloc[[r]].name.values[0],
            'tag': df.iloc[[r]].tag.values[0],
            'trophies': df.iloc[[r]].trophies.values[0],
            'country': df.iloc[[r]].name_pais.values[0],
            'simil': round(1-a[0][i+1], 4) })
    return data

# Data Collection
df = pd.read_csv('players.csv')
tags = set(df['tag'])

# Feature Engineering
df_r = df.drop(['name','name_clan','name_arena','tag'], axis = 1)

df_r['tag_clan'] = df_r['tag_clan'].fillna('#NoClan')
df_r['name_pais'] = labelE.fit_transform(df_r['name_pais'])
df_r['tag_clan'] = labelE.fit_transform(df_r['tag_clan'])

scaler.fit(df_r)
values = scaler.transform(df_r)

df_F = pd.DataFrame(values)
df_F.columns = ['name_pais', 'rank', 'expLevel', 'trophies', 'tag_clan', 'id_arena']

# Model
neigh = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10, n_jobs=-1)
neigh.fit(df_F)

# Use Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend',methods=['POST'])
def recommend():
    tag = findTag(request.form['tag'])
    try:
        n = int(request.form['nei'])
    except ValueError:
        n = 5
    n = max(1, min(n, 50))

    idx = tagToIndex(tag)

    a, b = neigh.kneighbors(df_F.iloc[[idx]], n_neighbors=n+1)

    res = listToTag(a,b)

    player = df.iloc[idx]
    return render_template('index.html', res = res, player = player)

if __name__ == "__main__":
    app.run()
