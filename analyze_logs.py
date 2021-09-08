import os
with open('skips_run2.csv', 'w') as skip_f:
    skip_f.write('num_skips\n')
    with open('lens_run2.csv', 'w') as len_f:
        for filename in os.listdir('.'):
            if 'run2' in filename and '.txt' in filename:
                print(f'analyzing {filename}')
                with open(filename, 'r') as f:
                    for l in f:
                        l = l.strip()
                        s = 'Skipped primes X times: '
                        if s in l:
                            num_skip = int(l.split(s)[1][0])
                            skip_f.write(f'{num_skip}\n')

                        if l.startswith('['):
                            len_meetup = len(l.split(','))
                            len_f.write(f'{len_meetup}\n')
