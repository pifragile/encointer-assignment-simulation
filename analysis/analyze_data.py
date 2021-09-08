import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm

all_filenames = [fn for fn in os.listdir('./data') if fn.split('.')[-1] == 'csv' and 'large_meetups' in fn and 'analysis' in fn]

df = pd.concat([pd.read_csv(os.path.join('data', f)) for f in all_filenames])

num_rows = len(df)
max_length_max = df['max_length'].max()
max_num_without_br = df['num_meetups_without_bootstrapper_or_reputable'].max()
sum_meetups = df['num_meetups'].sum()

print(f"""
    NUmber of simulated assignments: {num_rows}
    Max number of participants per meetup: {max_length_max}
    Max number of meetups without br: {max_num_without_br}
    Sum of calculated meetups: {sum_meetups}
    Max newbie ratio: {df['max_newbie_ratio'].max()}
    """)

df_newbies = df[df['max_newbie_ratio'] > 0.34]
print(df_newbies)

# set to True if you want to preprocess counting of rows grouped by min_length and max_length
# as sns.distplot is way too slow for our large dataset
preprocess_min_length_max_length = False
if preprocess_min_length_max_length:
    min_max_counts = {}
    for index, row in df.iterrows():
        key = f"{int(row['min_length'])}|{int(row['max_length'])}"
        if key in min_max_counts:
            min_max_counts[key] += 1
        else:
            min_max_counts[key] = 1
    print(min_max_counts)
    output = min_max_counts
else:
    output = {'9|13': 10063, '9|12': 9, '9|14': 17, '9|11': 258, '8|12': 21}


print(f'Number of simulated assignments check:{sum(output.values())}')

df_count = df.groupby(['min_length', 'max_length']).size().reset_index()

print(df_count)

df_heatmap = df_count.pivot(index='max_length', columns='min_length', values=0)
ax = sns.heatmap(df_heatmap, cmap=sns.cubehelix_palette(start=.5, rot=-.5, as_cmap=True), linewidths=0.5,
                 linecolor='white', norm=LogNorm(), cbar_kws={'label': 'Number of ceremony phases'})
ax.invert_yaxis()
plt.title('Bounds on meetup size for simulated meetup assignments')
plt.xlabel('Minimum Meetup Size')
plt.ylabel('Maximum Meetup Size')
plt.savefig('plots/meetup_size_bounds')
