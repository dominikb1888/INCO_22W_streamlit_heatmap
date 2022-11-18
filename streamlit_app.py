import streamlit as st
import pandas as pd
import json
from datetime import datetime
from datetime import timedelta
import seaborn as sns

with open('github_repos_with_users.json') as json_file:
    data = json.load(json_file)
df = pd.json_normalize(data, record_path='mentionableUsers', meta=['name', 'updatedAt', 'url'], record_prefix='user_')

df = df[df.user_login != 'dominikb1888']
df = df[df.user_login != 'ProfEnergyHuber']

# df.apply(lambda x: x['Formula'].replace('Length', str(x['Length'])), axis=1)

# Remove String 'user_login' from 'name'
df['new'] = df.apply(lambda x: x['name'].replace((x['user_login']), ''), 1)
df['session_no'] = df['new'].str.split('-', expand=True)[0]
df['exercise_no'] = df['new'].str.split('-', expand=True)[1]
df['exercise_name'] =  df['new'].str.split('-', expand=True)[2] + ' ' +  df['new'].str.split('-', expand=True)[3]

dff = df[['session_no', 'exercise_no', 'exercise_name', 'user_login', 'url','updatedAt']]
dff = (dff
  .astype({
     'session_no':  'int8',
     'exercise_no': 'int8',
     'exercise_name': 'category',
     'user_login': 'category',
     'updatedAt': 'datetime64[ns]',
  })
  .sort_values('updatedAt', ascending=True)
)

pivot_table = dff.pivot_table(index="user_login", columns="session_no", values='url', aggfunc='count')
#pivot_table[pivot_table == 0] = np.nan
pivot_table['sum_cols'] = pivot_table.sum(axis=1)
pivot_table = pivot_table.sort_values('sum_cols', ascending=False).iloc[0:20]
pivot_table.drop('sum_cols', axis=1, inplace=True)

def color_hide_nan(val):
    if val < 1:
        color = 'transparent'
    elif 2<val<30:
        color = 'dimgray'
    else:
        color = "white"
    return 'color: %s' % color



st.set_option('deprecation.showPyplotGlobalUse', False)
# my_date = st.sidebar.date_input('start date', datetime(2022,3,3,11,0,0))

my_date = st.slider(
    "Until?",
    value=datetime(2022, 3, 16, 8, 30, 0),
    step=timedelta(days=1),
    min_value = datetime(2022, 3, 16, 8,30, 0) - timedelta(days=0),
    max_value = datetime(2022, 3 ,16, 8, 30, 0) + timedelta(days=300),
    format="MM/DD/YY - hh:mm:ss")

st.table(pivot_table.style.background_gradient(axis=None, cmap="YlGnBu").applymap(color_hide_nan))
