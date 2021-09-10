import matplotlib.pyplot as plt
import pandas as pd

# use this to preprocess the data, as distplot is way too slow for our huge dataset
pre_process = True
if pre_process:
    with open('data/lens_large_meetups.csv', 'r') as f:
        length_counter = {}
        newbie_ratio_counter = {}
        f.readline()
        for l in f:
            length, num_newbies = l.split(',')
            length = int(length)
            num_newbies = int(num_newbies)
            newbie_ratio = round(num_newbies / length, 2)
            if length in length_counter.keys():
                length_counter[length] += 1
            else:
                length_counter[length] = 1

            if newbie_ratio in newbie_ratio_counter.keys():
                newbie_ratio_counter[newbie_ratio] += 1
            else:
                newbie_ratio_counter[newbie_ratio] = 1

    print('length count:')
    print(length_counter)
    print('newbie ratio count:')
    print(newbie_ratio_counter)
    lens = length_counter
    newbie_ratios = newbie_ratio_counter
else:
    lens = {12: 4083634, 13: 69725, 11: 361169120, 10: 188089196, 9: 369822398, 8: 1848, 14: 115}
    newbie_ratios = {0.25: 3133927, 0.23: 53525, 0.27: 307483351, 0.3: 2913218, 0.22: 314520094, 0.2: 101114979,
                     0.17: 572923, 0.15: 9883, 0.18: 42057928, 0.1: 67366911, 0.09: 11610741, 0.11: 43309580,
                     0.33: 205960, 0.08: 173754, 0.0: 28701968, 0.31: 3387, 0.36: 2840, 0.29: 52, 0.12: 952, 0.21: 56,
                     0.07: 4, 0.14: 3}

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
plt.savefig('plots/meetup_size_distribution_large_meetups.png')

df = pd.DataFrame(newbie_ratios.items(), columns=['newbie_ratio', 'amount_meetups'])

print(f"""
Sum of meetups: {df['amount_meetups'].sum()}
""")

df = df.sort_values('newbie_ratio')
ax = df.plot.bar(x='newbie_ratio', y='amount_meetups', rot=0)
ax.get_legend().remove()
plt.yscale('log')
plt.title('Newbie ratio distribution')
plt.xlabel('Newbie ratio')
plt.ylabel('Number of meetups')
plt.savefig('plots/newbie_ratio_distribution_large_meetups.png')
