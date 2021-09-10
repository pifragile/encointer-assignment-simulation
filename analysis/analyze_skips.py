import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('data/skips_large_meetups.csv')
max_skips = df['num_skips'].max()

# ax = sns.histplot(df, log_scale=(False,True))


bins = range(1, 10)
plt.hist(df, range(1, 11), align='left', edgecolor='black', linewidth=1)
plt.xticks(range(1, 10))
plt.yscale('log')
#plt.xlim([0.5, 9.5])

plt.title('Distribution loop iterations for bad prime number configurations')
plt.xlabel('Number of loop iterations')
plt.ylabel('Count')

plt.savefig('plots/skip_distribution_large_meetups.png')

print(f"""
Max number of skips: {max_skips}
Total runs where there were minimum 1 skip: {len(df)}
""")

grouped_df = df.groupby('num_skips').size()
print(grouped_df)