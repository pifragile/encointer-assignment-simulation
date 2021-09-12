import csv
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm

from analyze_assignment import BENCHMARK_NAME

with open(os.path.join('data', f'meetup_lengths_{BENCHMARK_NAME}.csv')) as csv_file:
    reader = csv.reader(csv_file)
    out = dict(reader)
    lens = {}
    for key, value in out.items():
        lens[int(key)] = int(value)

with open(os.path.join('data', f'newbie_ratios_{BENCHMARK_NAME}.csv')) as csv_file:
    reader = csv.reader(csv_file)
    out = dict(reader)
    newbie_ratios = {}
    for key, value in out.items():
        newbie_ratios[float(key)] = int(value)

df = pd.DataFrame(lens.items(), columns=['num_participants', 'amount_meetups'])

print(f"""
Sum of meetups: {df['amount_meetups'].sum()}
""")

df = df.sort_values('num_participants')
ax = df.plot.bar(x='num_participants', y='amount_meetups', rot=0)
ax.get_legend().remove()
plt.yscale('log')
plt.title('Meetup size distribution')
plt.xlabel('Number of participants')
plt.ylabel('Number of meetups')
plt.savefig(f'plots/meetup_size_distribution_{BENCHMARK_NAME}.png')
plt.clf()

max_newbie_ratio = max(newbie_ratios.keys())
i = 0.0
while i <= max_newbie_ratio:
    i = round(i,2)
    if not i in newbie_ratios.keys():
        newbie_ratios[i] = 0
    i += 0.01

df = pd.DataFrame(newbie_ratios.items(), columns=['newbie_ratio', 'amount_meetups'])

print(f"""
Sum of meetups: {df['amount_meetups'].sum()}
""")

df = df.sort_values('newbie_ratio')
ax = df.plot.bar(x='newbie_ratio', y='amount_meetups', rot=0)
ax.get_legend().remove()


ax.set_xticklabels([t if not i % 5 else "" for i, t in enumerate(ax.get_xticklabels())])

plt.yscale('log')
plt.title('Newbie ratio distribution')
plt.xlabel('Newbie ratio')
plt.ylabel('Number of meetups')
plt.savefig(f'plots/newbie_ratio_distribution_{BENCHMARK_NAME}.png')
plt.clf()

# analyze data
all_filenames = [fn for fn in os.listdir('./data') if fn.split('.')[-1] == 'csv' and f'analysis_{BENCHMARK_NAME}' in fn]

df = pd.concat([pd.read_csv(os.path.join('data', f)) for f in all_filenames])

num_rows = len(df)
max_length_max = df['max_length'].max()
max_num_without_br = df['num_meetups_without_bootstrapper_or_reputable'].max()
sum_meetups = df['num_meetups'].sum()

print(f"""
    Number of simulated assignments: {num_rows}
    Max number of participants per meetup: {max_length_max}
    Max number of meetups without br: {max_num_without_br}
    Sum of calculated meetups: {sum_meetups}
    Max newbie ratio: {df['max_newbie_ratio'].max()}
    """)

df_newbies = df[df['max_newbie_ratio'] > 0.3]

# set to True if you want to preprocess counting of rows grouped by min_length and max_length
# as sns.distplot is way too slow for our large dataset
preprocess_min_length_max_length = True
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
    output = {}

print(f'Number of simulated assignments check:{sum(output.values())}')

df_count = df.groupby(['min_length', 'max_length']).size().reset_index()

df_heatmap = df_count.pivot(index='max_length', columns='min_length', values=0)
ax = sns.heatmap(df_heatmap, cmap=sns.cubehelix_palette(start=.5, rot=-.5, as_cmap=True), linewidths=0.5,
                 linecolor='white', norm=LogNorm(), cbar_kws={'label': 'Number of ceremony phases'})
ax.invert_yaxis()
plt.yscale('linear')
plt.title('Bounds on meetup size for simulated meetup assignments')
plt.xlabel('Minimum Meetup Size')
plt.ylabel('Maximum Meetup Size')
plt.savefig(f'plots/meetup_size_bounds_{BENCHMARK_NAME}.png')
plt.clf()

# analyze skips
df1 = df[['skip_count_br']]
df2 = df[['skip_count_e']]
df3 = df[['skip_count_n']]
df1.columns = ['num_skips']
df1.append(df2)
df1.append(df3)

max_skips = df1['num_skips'].max()

bins = range(1, 10)
plt.hist(df1, range(1, 11), align='left', edgecolor='black', linewidth=1)
plt.xticks(range(1, 10))
plt.yscale('log')
# plt.xlim([0.5, 9.5])

plt.title('Distribution loop iterations for bad prime number configurations')
plt.xlabel('Number of loop iterations')
plt.ylabel('Count')

plt.savefig(f'plots/skip_distribution_{BENCHMARK_NAME}.png')
plt.clf()

print(f"""
Max number of skips: {max_skips}
Total runs where there were minimum 1 skip: {len(df1[df1['num_skips'] > 0])}
""")

grouped_df = df1.groupby('num_skips').size()
print(grouped_df)
print(f"""
Number of simulated assignments check: {grouped_df.sum()}
""")