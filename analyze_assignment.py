import csv
import math
import multiprocessing as mp
import os
import random
import time

from primes import primes

BENCHMARK_NAME = 'run_test'
NUM_BENCHMARKS = 48
BENCHMARK_SIZE = 8


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

###
###
# UTILS
#

def merge_dicts(dicts):
    first = dicts[0].copy()
    for mergedfrom in dicts[1:]:
        for k, v in mergedfrom.items():
            if k in first:
                first[k] += v
            else:
                first[k] = v
    return first


def proc_wrapper(func, *args, **kwargs):
    """Print exception because multiprocessing lib doesn't return them right."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(e)
        raise


def print_colored(text, color):
    print(f'{color}{text}{bcolors.ENDC}')


def is_prime(x):
    count = 0
    for i in range(int(x / 2)):
        if x % (i + 1) == 0:
            count = count + 1
    return count == 1


def find_prime_below(n):
    if not n % 2:
        n = n - 1
    for i in range(n, 0, -2):
        if is_prime(i):
            return i

    return 2


def find_prime_above(n):
    if not n % 2:
        n = n + 1
    for i in range(n, 2 * n, 2):
        if is_prime(i):
            return i

    return 2


def find_nearest_prime(n):
    if not n % 2:
        n = n - 1
    i = 0
    f = 1
    while True:
        n = n + i * f
        if is_prime(n):
            return n
        i += 1
        f * -1

    return 2


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


###
###
###


###
###
# CORE FUNCTIONS
#
def get_meetup_location(participant_index, N, n, s1, s2):
    # we are in an additive group of order N, this group is cyclic
    # and s1 is a generator of the group (becasue it is by definition coprime to N)
    #
    # ((participant_index * s1 + s2) % N) shuffles N participants in a random order
    # % n distributes the participants to a random location within n avaible locations.

    # if N is coprime with n then the output of this formula gets more predictable,
    # because % N % n boils down to % n
    # so we chose N as a prime number as well in most cases, see below.
    #
    # Also note that it is not a requirement that this distribution is truly random,
    # it has to be random enough to make it infeasible to guess your meetup location,
    # or to reigsiter in a certain order with some collutors in order to end up in the same meetup.

    return ((participant_index * s1 + s2) % N) % n


def get_participants(meetup_index, N, n, s1, s2, num_participants=None):
    # this function is simply the inversed formula of get_meetup_location
    result = []
    for i in range(int(math.ceil((N - meetup_index) / n))):
        t1 = (n * i + meetup_index - s2) % N
        t2 = modinv(s1, N)
        t3 = (t1 * t2) % N
        result.append(t3)

        # when we chose prime_below, the participants in the gap are not represented by get_participants, so we add them here
        if num_participants and t3 < num_participants - N:
            result.append(t3 + N)
    return result


def get_participants_full(meetup_index, num_locations, num_b, num_r, num_e, num_n, s1_br, s2_br, s1_e, s2_e, s1_n,
                          s2_n, N_br, N_e, N_n):
    n = num_locations
    result = []

    # bootstrappers
    num_br = num_b + num_r
    participants = get_participants(meetup_index, N_br, n, s1_br, s2_br, num_br)

    for p in participants:
        if p < num_b:
            result.append(f'B{p}')
        else:
            result.append((f'R{p - num_b}'))

    # endorsees
    participants = get_participants(meetup_index, N_e, n, s1_e, s2_e, num_e)
    for p in participants:
        if p < num_e:
            result.append(f'E{p}')

    # newbies
    participants = get_participants(meetup_index, N_n, n, s1_n, s2_n, num_n)
    for p in participants:
        if p < num_n:
            result.append(f'N{p}')

    return result


def validate_equal_mapping(num_participants, N, n, s1, s2):
    # show that this loop is bounded by the gap between prime numbers in a sensible range
    meetup_index_count = {}

    # let gap = num_participants - N
    # if there are no more than ceil(gap / n) participants per meetup in the range(N, num_participants)
    # the distribution is equal
    meetup_index_count_max = math.ceil((num_participants - N) / n)
    for i in range(N, num_participants):
        meetup_index = get_meetup_location(i, N, n, s1, s2)

        if not meetup_index in meetup_index_count.keys():
            meetup_index_count[meetup_index] = 1
        else:
            meetup_index_count[meetup_index] += 1
            if meetup_index_count[meetup_index] > meetup_index_count_max:
                return False
    return True


def get_N_s1_s3(num_participants, num_locations):
    # we chose N to be a prime number, because this prevents attacks, where an attacker, registers new users in
    # a specific order and fills up the users such that N and n are not coprime which will let him guess the
    # other particiopants in his meetup
    # make example with 100 meetups, 1200 participants, show no matter s1 and s2, the gaps are always 100
    N = find_prime_below(num_participants)

    # we have to make sure that all the numbers between N and num_participants map to different locations,
    # like this we can make sure that the participants are split equally and the maximum number of participants
    # per meetup is num_participants // num_locations + 1
    skip_count = 0
    while True:
        s1 = random.choice(primes)
        s2 = random.choice(primes)
        if validate_equal_mapping(num_participants, N, num_locations, s1, s2):
            break
        else:
            skip_count += 1
    return N, s1, s2, skip_count


###
###
###


def analyze_meetups(meetups):
    num_meetups_without_bootstrapper_or_reputable = 0

    newbie_ratio_list = []
    num_bootstrappers_list = []
    num_reputables_list = []
    num_newbies_list = []
    length_list = []
    num_bootstrapper_and_reputable_list = []

    for meetup in meetups:
        length = len(meetup)

        num_reputables = 0
        num_bootstrappers = 0
        num_newbies = 0
        for x in meetup:
            if x[0] == 'R':
                num_reputables += 1
            elif x[0] == 'B':
                num_bootstrappers += 1
            elif x[0] == 'N':
                num_newbies += 1

        num_bootstrappers_list.append(num_bootstrappers)
        num_reputables_list.append(num_reputables)
        num_newbies_list.append(num_newbies)
        length_list.append(length)

        num_bootstrapper_and_reputables = num_bootstrappers + num_reputables
        if num_bootstrapper_and_reputables == 0:
            num_meetups_without_bootstrapper_or_reputable += 1

        num_bootstrapper_and_reputable_list.append(num_bootstrapper_and_reputables)

        newbie_ratio = num_newbies / length
        newbie_ratio_list.append(newbie_ratio)

    max_newbie_ratio = max(newbie_ratio_list)
    min_newbie_ratio = min(newbie_ratio_list)

    max_num_bootstrappers = max(num_bootstrappers_list)
    min_num_bootstrappers = min(num_bootstrappers_list)
    max_num_reputables = max(num_reputables_list)
    min_num_reputables = min(num_reputables_list)

    min_bootstrapers_and_reputable = min(num_bootstrapper_and_reputable_list)

    min_length = min(length_list)
    max_length = max(length_list)

    num_meetups = len(meetups)

    num_participants = sum(length_list)

    return {'num_meetups': num_meetups,
            'num_meetups_without_bootstrapper_or_reputable': num_meetups_without_bootstrapper_or_reputable,
            'min_num_bootstrappers': min_num_bootstrappers,
            'max_num_bootstrappers': max_num_bootstrappers,
            'min_num_reputables': min_num_reputables,
            'max_num_reputables': max_num_reputables,
            'min_bootstrapers_and_reputable': min_bootstrapers_and_reputable,
            'min_newbie_ratio': min_newbie_ratio,
            'max_newbie_ratio': max_newbie_ratio,
            'min_length': min_length,
            'max_length': max_length,
            'num_participants': num_participants
            }, newbie_ratio_list, length_list


def validate_meetups(meetups, num_locations, num_b, num_r, num_e, num_n, s1_br, s2_br, s1_e, s2_e, s1_n, s2_n, N_br,
                     N_e, N_n):
    for idx, meetup in enumerate(meetups):
        expected_meetup = get_participants_full(idx, num_locations, num_b, num_r, num_e, num_n, s1_br, s2_br, s1_e,
                                                s2_e, s1_n, s2_n, N_br, N_e, N_n)
        expected_meetup.sort()
        meetup.sort()
        assert (expected_meetup == meetup)


def calculate_meetups(num_locations, num_bootstrappers, num_reputables, num_endorsees, num_newbies, validate=False):
    """
    This function does the logic that will later be implementd in Substrate.
    """

    # number of participants per meetup if distribution was strictly equal
    MEETUP_MULTIPLIER = 10

    assert (num_locations >= 2)

    # Tradeoff: if we only accept prime_below number of meetups, we have the same number of meetups as
    # N and so, we will have at least 1 bootstrapper or reputable per meetup
    num_meetups = min(num_locations, find_prime_below(num_bootstrappers + num_reputables))

    available_slots = int(num_meetups * MEETUP_MULTIPLIER - num_bootstrappers)

    num_allowed_reputables = min(num_reputables, available_slots)
    available_slots -= num_allowed_reputables

    num_allowed_endorsees = min(num_endorsees, available_slots)
    available_slots -= num_allowed_endorsees

    max_allowed_newbies = (num_bootstrappers + num_allowed_reputables + num_allowed_endorsees) // 3
    num_allowed_newbies = min(num_newbies, available_slots)
    num_allowed_newbies = min(num_allowed_newbies, max_allowed_newbies)
    available_slots -= num_allowed_newbies

    num_participants = num_bootstrappers + num_allowed_reputables + num_allowed_endorsees + num_allowed_newbies

    num_meetups = int(math.ceil(num_participants / MEETUP_MULTIPLIER))
    num_allowed_bootstrappers = num_bootstrappers

    meetups = [[] for _ in range(num_meetups)]

    # distribute boostrappers and reputables
    # they are distributed in one go to minimize the number of meetups without
    # at least one bootstrapper or reputable
    n = num_meetups
    N_br, s1_br, s2_br, skip_count_br = get_N_s1_s3(num_allowed_bootstrappers + num_allowed_reputables, n)
    for i in range(num_allowed_bootstrappers):
        meetup = get_meetup_location(i, N_br, n, s1_br, s2_br)
        meetups[meetup].append(f'B{i}')

    for i in range(num_allowed_reputables):
        j = i + num_allowed_bootstrappers
        meetup = get_meetup_location(j, N_br, n, s1_br, s2_br)
        meetups[meetup].append(f'R{i}')

    # distribute endorsees
    N_e, s1_e, s2_e, skip_count_e = get_N_s1_s3(num_allowed_endorsees, n)
    for i in range(num_allowed_endorsees):
        meetup = get_meetup_location(i, N_e, n, s1_e, s2_e)
        meetups[meetup].append(f'E{i}')

    # distribute_newbies
    N_n, s1_n, s2_n, skip_count_n = get_N_s1_s3(num_allowed_newbies, n)
    for i in range(num_allowed_newbies):
        meetup = get_meetup_location(i, N_n, n, s1_n, s2_n)
        meetups[meetup].append(f'N{i}')

    if validate:
        validate_meetups(meetups, num_meetups, num_allowed_bootstrappers, num_allowed_reputables, num_allowed_endorsees,
                         num_allowed_newbies, s1_br, s2_br, s1_e, s2_e, s1_n, s2_n, N_br, N_e, N_n)

    skip_counts = {'skip_count_br': skip_count_br,
                   'skip_count_e': skip_count_e,
                   'skip_count_n': skip_count_n}
    return meetups, skip_counts


def run_benchmark(identifier, validate, benchmark_size):
    print(f'Running benchmark {identifier}')
    t = time.time()
    writer = None

    newbie_ratio_counter = {}
    meetup_length_counter = {}

    with open(os.path.join('data', f'analysis_{identifier}.csv'), 'w', newline='') as f_analysis:
        with open(os.path.join('data', f'log_{identifier}.csv'), 'w', newline='') as f_log:
            f_log.write('run_number,meetup\n')
            first = True
            run_number = 0
            for num_locations in [5] + random.sample(range(6, 50000), benchmark_size) + [50000]:
                for num_bootstrappers in [3, 6, 12]:
                    for num_reputables in [0] + random.sample(range(0, 10000), benchmark_size) + [10000]:
                        for num_endorsees in [0] + random.sample(range(0, 50 * num_bootstrappers), benchmark_size + 1):
                            for num_newbies in [0] + random.sample(range(0, 10000), benchmark_size) + [10000]:
                                config = {
                                    'benchmark_identifier': identifier,
                                    'run_number': run_number,
                                    'num_locations': num_locations,
                                    'num_bootstrappers': num_bootstrappers,
                                    'num_reputables': num_reputables,
                                    'num_endorsees': num_endorsees,
                                    'num_newbies': num_newbies
                                }

                                meetups, skip_counts = calculate_meetups(num_locations, num_bootstrappers,
                                                                         num_reputables,
                                                                         num_endorsees, num_newbies,
                                                                         validate=validate)

                                data, newbie_ratio_list, length_list = analyze_meetups(meetups)

                                for meetup in meetups:
                                    f_log.write(f'{run_number},{".".join(meetup)}\n')

                                for length in length_list:
                                    if length in meetup_length_counter.keys():
                                        meetup_length_counter[length] += 1
                                    else:
                                        meetup_length_counter[length] = 1

                                for newbie_ratio in newbie_ratio_list:
                                    newbie_ratio = round(newbie_ratio, 2)
                                    if newbie_ratio in newbie_ratio_counter.keys():
                                        newbie_ratio_counter[newbie_ratio] += 1
                                    else:
                                        newbie_ratio_counter[newbie_ratio] = 1

                                row = {**config, **data, **skip_counts}

                                if first:
                                    fieldnames = row.keys()
                                    writer = csv.DictWriter(f_analysis, fieldnames=fieldnames)
                                    writer.writeheader()
                                    first = False
                                writer.writerow(row)

                                run_number += 1

    print(f'Process {identifier} done in {time.time() - t} seconds')

    return meetup_length_counter, newbie_ratio_counter


if __name__ == '__main__':
    t = time.time()
    print('Starting Processes')
    num_workers = mp.cpu_count()
    pool = mp.Pool(num_workers)
    results = []
    for i in range(NUM_BENCHMARKS):
        run_name = f'{BENCHMARK_NAME}_{i}'
        results.append(pool.apply_async(proc_wrapper, args=(run_benchmark, run_name, True, BENCHMARK_SIZE,)))

    res = [result.get() for result in results]

    meetup_length_counters, newbie_ratio_counters = zip(*res)

    meetup_length_counter = merge_dicts(meetup_length_counters)
    newbie_ratio_counter = merge_dicts(newbie_ratio_counters)


    with open(os.path.join('data', f'meetup_lengths_{BENCHMARK_NAME}.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in meetup_length_counter.items():
            writer.writerow([key, value])

    with open(os.path.join('data', f'newbie_ratios_{BENCHMARK_NAME}.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in newbie_ratio_counter.items():
            writer.writerow([key, value])

    print(f'Done after {time.time() - t} seconds.')
