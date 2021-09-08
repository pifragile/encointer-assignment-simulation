import matplotlib.pyplot as plt
import pandas as pd

# use this to preprocess the data, as distplot is way too slow for our huge dataset
pre_process = False
if pre_process:
    with open('data/lens_prime_below.csv', 'r') as f:
        counter = {}
        for l in f:
            l = int(l)
            if l in counter.keys():
                counter[l] += 1
            else:
                counter[l] = 1

    print(counter)
    lens = counter
else:
    lens = {3: 1884, 4: 17977, 11: 849570493, 10: 656302972, 9: 1354037135, 8: 30858292, 5: 6470, 7: 29127, 6: 17907,
            12: 258253969, 13: 10003897, 14: 132896, 15: 627}

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
