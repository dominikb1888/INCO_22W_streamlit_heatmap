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

sns.set(rc={'figure.figsize':(11,44)})


def heatmap_plot(my_date=datetime.strptime("2022-03-16 11:00:00", '%Y-%m-%d %H:%M:%S')):
    pivot_table = (dff[dff.updatedAt < my_date]
                   .pivot_table(index="user_login", columns="session_no", values='url', aggfunc='count'))

    heatmap_plot = sns.heatmap(
        pivot_table,
        annot_kws = {
            'fontsize': 11,
            'va':'center_baseline',
        },
        vmin = 1,
        vmax = 17,
        cmap = 'crest',
        annot = True,
        linecolor = 'white',
        linewidths = .6,
        cbar = False,
        square = True,
    )
    heatmap_plot.set_xlabel('')
    heatmap_plot.set_ylabel('')
    heatmap_plot.set_yticklabels(heatmap_plot.get_yticklabels(), va='center_baseline')
    heatmap_plot.set_xticklabels(heatmap_plot.get_xticklabels(), ha='center')
    heatmap_plot.xaxis.tick_top()

st.set_option('deprecation.showPyplotGlobalUse', False)
my_date = st.sidebar.date_input('start date', datetime(2022,3,3,11,0,0))
heatmap_plot(my_date)
st.pyplot()
