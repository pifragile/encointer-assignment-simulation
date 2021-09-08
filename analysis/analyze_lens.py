import matplotlib.pyplot as plt
import pandas as pd
import csv

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
    lens = {3: 1884, 4: 17977, 11: 849570493, 10: 656302972, 9: 1354037135, 8: 30858292, 5: 6470, 7: 29127, 6: 17907,
            12: 258253969, 13: 10003897, 14: 132896, 15: 627}
    newbie_ratios = {}

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
plt.savefig('plots/meetup_size_distribution.png')


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
plt.savefig('plots/newbie_ratio_distribution.png')