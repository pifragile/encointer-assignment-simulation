import os
with open('skips_prime_below.csv', 'w') as skip_f:
    skip_f.write('num_skips\n')
    with open('lens_prime_below.csv', 'w') as len_f:
        len_f.write('len_meetups,num_newbies\n')
        num_verified = 0
        num_meetups = 0
        for filename in os.listdir('.'):
            if 'below' in filename and '.txt' in filename:
                print(f'analyzing {filename}')
                with open(filename, 'r') as f:
                    for l in f:
                        if l.startswith('['):
                            len_meetup = 0
                            num_newbies = 0
                            for c in l:
                                if c in ['B', 'R', 'E']:
                                    len_meetup += 1
                                elif c == 'N':
                                    len_meetup += 1
                                    num_newbies += 1
                            len_f.write(f'{len_meetup},{num_newbies}\n')
                        else:
                            l = l.strip()
                            s = 'Skipped primes X times: '
                            if s in l:
                                num_skip = int(l.split(s)[1][0])
                                skip_f.write(f'{num_skip}\n')

                            elif 'Meetups verified' in l:
                                num_verified += 1
                            elif 'Running Test' in l:
                                num_meetups += 1
        print(f'Number of meetups verified: {num_verified}/{num_meetups}')