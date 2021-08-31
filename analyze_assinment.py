import csv
import math
import random
import time

from primes import primes


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


#
# THIS SECTION of comments are internal notes of pifragile
# do not quote me on that stuff.
#
# if n = x and N = 12x, the groups are very predictable
# it will always go in steps of x, because mod N mod n boils down to mod n

# number of participants can be influenced by attacker

# approach: chose n and N such that they are coprime
# if n is increased or decreased: more or fewer persons per meetup
# if N is increased or decreased: permutation not perfect, there might be meetups with no
# participants (problematic for bootstrappers and reputables)

# approach:
# take the modulus M as the next prime smaller than N, the ones between M and N, will be
# mapped to duplicate indices between 0 and M. but thats ok, because it is not predictable,
# where they will land

# for reputables+bootstrappers rb:
# if there are X rb, we cannot make X meetups, but the prime  below X, because otherwise it could
# be that there are meetups without rp

# come up with algo to find best n, and M for each rp, newbie, endorsees group


# for bootstrappers there can be no attack, so we just distribute them, take M as num_locations,
# so for each bootsrtapper we get a different location.

# for reputables there is also an attack vector foe collusion

###
###
# UTILS
#

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


def get_participants(meetup_index, N, n, s1, s2):
    # this function is simply the inversed formula of get_meetup_location
    result = []
    for i in range(int(math.ceil((N - meetup_index) / n))):
        t1 = (n * i + meetup_index - s2) % N
        t2 = modinv(s1, N)
        t3 = (t1 * t2) % N
        result.append(t3)
    return result


def get_participants_full(meetup_index, num_locations, num_b, num_r, num_e, num_n, s1_br, s2_br, s1_e, s2_e, s1_n,
                          s2_n):
    n = num_locations
    result = []

    # bootstrappers
    num_br = num_b + num_r
    N_br = find_prime_above(num_br)
    participants = get_participants(meetup_index, N_br, n, s1_br, s2_br)
    for p in participants:
        if p < num_br:
            if p < num_b:
                result.append(f'B{p}')
            else:
                result.append((f'R{p - num_b}'))

    # endorsees
    N_e = find_prime_above(num_e)
    participants = get_participants(meetup_index, N_e, n, s1_e, s2_e)
    for p in participants:
        if p < num_e:
            result.append(f'E{p}')

    # newbies
    N_n = find_prime_above(num_n)
    participants = get_participants(meetup_index, N_n, n, s1_n, s2_n)
    for p in participants:
        if p < num_n:
            result.append(f'N{p}')

    return result


###
###
###

def test_core_functions():
    # number of participants
    N = 1201

    # number of meetups
    n = 100

    s1 = random.choice(primes)
    # s1 = 425374829251
    # s2 = random.randint(0, N)
    s2 = random.choice(primes)

    meetups = [[] for _ in range(n)]
    for i in range(N):
        meetup_location = get_meetup_location(i, N, n, s1, s2)
        meetups[meetup_location].append(i)

    for j in range(n):
        participants = get_participants(j, N, n, s1, s2)
        participants.sort()
        expected_participants = meetups[j]
        expected_participants.sort()
        print(participants)
        assert (participants == expected_participants)


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
        num_reputables = sum([1 for x in meetup if x[0] == 'R'])
        num_bootstrappers = sum([1 for x in meetup if x[0] == 'B'])
        num_newbies = sum([1 for x in meetup if x[0] == 'N'])

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

    num_participants = sum([len(l) for l in meetups])

    print(f"""
		Number of meetups: {num_meetups}
		Number of meetups without bootstrappers or reputables: {num_meetups_without_bootstrapper_or_reputable}
		Number of Boostrappers in [{min_num_bootstrappers}, {max_num_bootstrappers}]
		Number of Reputables in [{min_num_reputables}, {max_num_reputables}]
		Minimum number of bootstrapper/reputables: {min_bootstrapers_and_reputable}
		Newbie ratio in [{min_newbie_ratio}, {max_newbie_ratio}]
		Length in [{min_length},{max_length}]
		Number of participants is {num_participants}
		""")
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
            }


def validate_meetups(meetups, num_locations, num_b, num_r, num_e, num_n, s1_br, s2_br, s1_e, s2_e, s1_n, s2_n):
    for idx, meetup in enumerate(meetups):
        expected_meetup = get_participants_full(idx, num_locations, num_b, num_r, num_e, num_n, s1_br, s2_br, s1_e,
                                                s2_e, s1_n, s2_n)
        expected_meetup.sort()
        meetup.sort()
        assert (expected_meetup == meetup)
    print_colored('Meetups verified.', bcolors.OKGREEN)


def calculate_meetups(num_locations, num_bootstrappers, num_reputables, num_endorsees, num_newbies, validate=False):
    """
    This function does the logic that will later be implementd in Substrate.
    """

    # number of participants per meetup if distribution was strictly equal
    MEETUP_MULTIPLIER = 10

    assert (num_locations >= 2)

    num_meetups = min(num_locations, num_bootstrappers + num_reputables)

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

    num_allowed_bootstrappers_reputables = num_allowed_bootstrappers + num_allowed_reputables

    meetups = [[] for _ in range(num_meetups)]

    # distribute boostrappers and reputables
    # they are distributed in one go to minimize the number of meetups without
    # at least one bootstrapper or reputable
    s1_br = random.choice(primes)
    s2_br = random.choice(primes)
    N = find_prime_above(num_allowed_bootstrappers + num_allowed_reputables)
    n = num_meetups
    print(s1_br, s2_br, N, n)
    for i in range(num_allowed_bootstrappers):
        meetup = get_meetup_location(i, N, n, s1_br, s2_br)
        meetups[meetup].append(f'B{i}')

    for i in range(num_allowed_reputables):
        j = i + num_allowed_bootstrappers
        meetup = get_meetup_location(j, N, n, s1_br, s2_br)
        meetups[meetup].append(f'R{i}')

    # distribute endorsees
    s1_e = random.choice(primes)
    s2_e = random.choice(primes)
    N = find_prime_above(num_allowed_endorsees)
    n = num_meetups
    for i in range(num_allowed_endorsees):
        meetup = get_meetup_location(i, N, n, s1_e, s2_e)
        meetups[meetup].append(f'E{i}')

    # distribute_newbies
    s1_n = random.choice(primes)
    s2_n = random.choice(primes)
    N = find_prime_above(num_allowed_newbies)
    n = num_meetups
    for i in range(num_allowed_newbies):
        meetup = get_meetup_location(i, N, n, s1_n, s2_n)
        meetups[meetup].append(f'N{i}')

    if validate:
        validate_meetups(meetups, num_meetups, num_allowed_bootstrappers, num_allowed_reputables, num_allowed_endorsees,
                         num_allowed_newbies, s1_br, s2_br, s1_e, s2_e, s1_n, s2_n)

    return meetups


def test_distributions(num_locations, num_bootstrappers, num_reputables, num_endorsees, num_newbies):
    """
    Change parameters here and run the script in order to get the distribution of participants
    and some heuristics printed to the console.
    """

    print(f"""
		Running Test:
			Number of Locations = {num_locations}
			Number of Bootstrappers = {num_bootstrappers}
			Number of Reputables = {num_reputables}
			Number of Endorseeds = {num_endorsees}
			Number of Newbies = {num_newbies}
		""")

    meetups = calculate_meetups(num_locations, num_bootstrappers, num_reputables, num_endorsees, num_newbies)
    for m in meetups:
        print(m)
    data = analyze_meetups(meetups)

    print('#########################\n\n\n')

    return data


if __name__ == '__main__':
    write = None
    t = time.time()
    with open(f'analysis.csv', 'w', newline='') as csvfile:
        first = True
        for num_locations in [5] + random.sample(range(6, 50000), 5) + [50000]:
            for num_bootstrappers in [3, 6, 12]:
                for num_reputables in [0] + random.sample(range(0, 50 * num_bootstrappers), 3) + [10000]:
                    for num_endorsees in [0] + random.sample(range(0, 10000), 3) + [10000]:
                        for num_newbies in [0] + random.sample(range(0, 10000), 3) + [10000]:
                            for i in range(2):
                                config = {
                                    'num_locations': num_locations,
                                    'num_bootstrappers': num_bootstrappers,
                                    'num_reputables': num_reputables,
                                    'num_endorsees': num_endorsees,
                                    'num_newbies': num_newbies
                                }

                                data = test_distributions(num_locations, num_bootstrappers, num_reputables,
                                                          num_endorsees, num_newbies)
                                row = {**config, **data}

                                if first:
                                    fieldnames = row.keys()
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                    writer.writeheader()
                                    first = False
                                writer.writerow(row)
    print(f'Done in {time.time() - t} seconds')

# Problem
# if the output of get_meetup_location are as follows:
# x
# x - y
# x - 2*y
# ...
# z
# z - y
# z - 2*y

# and y happens to be n
# then there are consecutive groups of numbers that map to the same location
# this becaomes a problem together with the fact that we take the prime below 
# the number of bootstrappers and reuptables, because at the point where it wraps around,
# all the consequtive numbers land in the same location and this location will have
# too many participants

# Mitigations:
# 1. do not take prime below
# 2. check for this property and do not take the primes if it is the case
# 3. take prime above insetad of below, and accept that there will be meetups without reputable or bootstrapper
# --> this looks like a tradeoff of randomness vs. equal distribution


# example:
# 	s1 = 72914169386263772687
# 	s2 = 74123226946075602539
# num_locations = 28179
# num_bootstrappers = 3
# num_reputables = 2761
# num_endorsees = 437
# num_newbies = 9951
# test_distributions(num_locations, num_bootstrappers, num_reputables, num_endorsees, num_newbies)


# if we take prime above and accept some meetups without bootstrapper and reputable
# prove that there can be no more than 12 participants

# claim: if meetup multipler is x, then max_length will be at most x + 3
# intuition: in every of the 3 assignment steps(b+r, e, n) there can be at most 1 user per bucket too much.
# how to prove? hard to prove with all the different possible configurations of number of meetups,n, N etc....

# issue is if n is smaller than the gap between N and prime_above(N), then more than 1 additional user could end up in
# a meeupt

# maybe not prove, not accept up to xyz.

# i dont know if i am capable to come up with such a proof.
