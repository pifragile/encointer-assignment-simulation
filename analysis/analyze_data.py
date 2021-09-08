import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm

all_filenames = [fn for fn in os.listdir('./data') if fn.split('.')[-1] == 'csv' and 'below' in fn]

df = pd.concat([pd.read_csv(os.path.join('data', f)) for f in all_filenames])

num_rows = len(df)
max_length_max = df['max_length'].max()
max_num_without_br = df['num_meetups_without_bootstrapper_or_reputable'].max()
sum_meetups = df['num_meetups'].sum()

print(f"""
    NUmber of simulated ceremony phases: {num_rows}
    Max number of participants per meetup: {max_length_max}
    Max number of meetups without br: {max_num_without_br}
    Sum of calculated meetups: {sum_meetups}
    """)


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
else:
    output = {'3|3': 1884, '4|4': 17079, '8|11': 52349, '9|11': 922117, '10|10': 103863, '5|5': 1233, '6|6': 4070,
              '8|8': 22436, '8|10': 5107, '7|10': 5761, '6|11': 1424, '6|12': 177, '7|11': 3356, '6|10': 6961,
              '9|12': 1110179, '5|7': 1645, '7|9': 11780, '9|13': 2296616, '8|12': 602047, '8|13': 81800, '8|9': 2195,
              '7|8': 577, '6|9': 1258, '9|14': 124902, '9|10': 6575, '9|15': 626, '8|14': 1128, '5|8': 1699, '6|7': 189,
              '9|9': 2218, '5|11': 189, '5|10': 259, '6|8': 2721, '7|7': 325, '5|9': 1364, '4|8': 732, '7|12': 882,
              '7|13': 30, '5|6': 81, '4|7': 63, '4|9': 103}

    print(f'Number of simulated phases check:{sum(output.values())}')

    df_count = df.groupby(['min_length', 'max_length']).size().reset_index()

    print(df_count)

    df_heatmap = df_count.pivot(index='max_length', columns='min_length', values=0)
    ax = sns.heatmap(df_heatmap, cmap=sns.cubehelix_palette(start=.5, rot=-.5, as_cmap=True), linewidths=0.5,
                     linecolor='white', norm=LogNorm(), cbar_kws={'label': 'Number of ceremony phases'})
    ax.invert_yaxis()
    plt.title('Bounds on meetup size for simulated ceremony phases')
    plt.xlabel('Minimum Meetup Size')
    plt.ylabel('Maximum Meetup Size')
    plt.savefig('plots/meetup_size_bounds')
