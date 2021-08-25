import random, math

def is_prime(x):
    count = 0
    for i in range(int(x/2)):
        if x % (i+1) == 0:
            count = count+1
    return count == 1

def find_prime_below(n):
	if not n % 2:
		n = n-1
	for i in range(n, 0, -2):
		if is_prime(i):
			return i

	return 2

#primes = [i for i in range(2000,100000) if isPrime(i)]
primes = [10000019,10000079,10000103,10000121,10000139,10000141,10000169,10000189,10000223,10000229,10000247,10000253,10000261,10000271,10000303,10000339,10000349,10000357,10000363,10000379,10000439,10000451,10000453,10000457,10000481,10000511,10000537,10000583,10000591,10000609,10000643,10000651,10000657,10000667,10000687,10000691,10000721,10000723,10000733,10000741,10000747,10000759,10000763,10000769,10000789,10000799,10000813,10000819,10000831,10000849,10000867,10000871,10000873,10000877,10000891,10000931,10000943,10000961,10000967,10000987,10000993,10001009,10001053,10001081,10001093,10001107,10001119,10001203,10001207,10001209,10001213,10001221,10001227,10001231,10001237,10001261,10001269,10001281,10001311,10001347,10001357,10001363,10001399,10001401,10001419,10001441,10001443,10001461,10001473,10001483,10001501,10001521,10001531,10001533,10001567,10001569,10001587,10001603,10001617,10001659,10001687,10001701,10001707,10001713,10001759,10001777,10001779,10001791,10001801,10001807,10001813,10001819,10001821,10001833,10001837,10001861,10001881,10001891,10001903,10001921,10001963,10002007,10002017,10002019,10002029,10002053,10002059,10002061,10002067,10002077,10002121,10002127,10002133,10002149,10002191,10002197,10002199,10002203,10002257,10002259,10002277,10002283,10002287,10002323,10002331,10002347,10002397,10002403,10002407,10002431,10002437,10002439,10002449,10002463,10002481,10002521,10002527,10002529,10002547,10002563,10002571,10002589,10002599,10002623,10002649,10002653,10002659,10002661,10002667,10002731,10002761,10002763,10002779,10002791,10002803,10002809,10002823,10002829,10002833,10002847,10002859,10002871,10002887,10002929,10002943,10002959,10002983,10003001,10003003,10003027,10003031,10003043,10003073,10003087,10003121,10003127,10003159,10003181,10003193,10003199]

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
#so for each bootsrtapper we get a different location.

# for reputables there is also an attack vector foe collusion


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

def get_meetup_location(participant_index, N, n, s1, s2):
	return ((participant_index * s1 + s2) % N) % n


def get_participants(meetup_index, N, n, s1, s2):
	# fix maximum participants with custom N and n
	result = []
	for i in range(int(math.ceil((N-meetup_index)/n))):
		t1 = (n * i + meetup_index - s2) % N
		t2 = modinv(s1, N)
		t3 = (t1*t2) % N
		result.append(t3)
	return result



BOOTSTRAPPER = 1
REPUTABLE = 2
ENDORSEE = 3
NEWBIE = 4
class Participant():
	def __init__(type, index):
		assert(type in [BOOTSTRAPPER, REPUTABLE, ENDORSEE, NEWBIE])
		this.type = type
		this.index = index

def test_core_functions():
	# number of participants
	N = 1200

	# number of meetups
	n = 101

	s1 = random.choice(primes)
	#s1 = 425374829251
	s2 = random.randint(0, N)
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
		assert(participants == expected_participants)

def analyze_meetups(meetups):
	max_num_bootstrappers = 0
	min_num_bootstrappers = math.inf
	max_num_reputables = 0
	min_num_reputables = math.inf

	min_bootstrapers_and_reputable = math.inf

	min_length = math.inf
	max_length = 0

	num_meetups_without_bootstrapper_or_reputable = 0

	for meetup in meetups:
		length = len(meetup)
		num_reputables = sum([1 for x in meetup if x[0] == 'R'])
		num_bootstrappers = sum([1 for x in meetup if x[0] == 'B'])

		max_num_reputables = max(max_num_reputables, num_reputables)
		min_num_reputables = min(min_num_reputables, num_reputables)

		max_num_bootstrappers = max(max_num_bootstrappers, num_bootstrappers)
		min_num_bootstrappers = min(min_num_bootstrappers, num_bootstrappers)

		num_bootstrapper_and_reputables = num_bootstrappers + num_reputables
		if num_bootstrapper_and_reputables == 0:
			num_meetups_without_bootstrapper_or_reputable += 1

		min_bootstrapers_and_reputable = min(min_bootstrapers_and_reputable, num_bootstrapper_and_reputables)

		max_length = max(max_length, length)
		min_length = min(min_length, length)

	num_meetups = len(meetups)
	print(f"""
		Number of meetups: {num_meetups}
		Number of meetups without bootstrappers or reputables: {num_meetups_without_bootstrapper_or_reputable}
		Boostrappers in [{min_num_bootstrappers}, {max_num_bootstrappers}]
		Reputables in [{min_num_reputables}, {max_num_reputables}]
		Minimum number of bootstrapper/reputables: {min_bootstrapers_and_reputable}
		Length in [{min_length},{max_length}]
		""")
	return num_meetups, num_meetups_without_bootstrapper_or_reputable, min_num_bootstrappers, max_num_bootstrappers, min_num_reputables, max_num_reputables, min_bootstrapers_and_reputable, min_length, max_length

def test_distribution():
	num_locations = 10000

	num_bootstrappers = 12
	num_reputables = 10
	num_endorsees = 123
	num_newbies = 3010

	# number of participants per meetup if distribution was strictly equal
	MEETUP_MULTIPLIER = 12

	assert(num_locations >=2)

	num_meetups = min(num_locations, int(num_bootstrappers + num_reputables))

	available_slots = int(num_meetups * MEETUP_MULTIPLIER - num_bootstrappers)

	num_allowed_reputables = min(num_reputables, available_slots)
	available_slots -= num_allowed_reputables

	num_allowed_endorsees = min(num_endorsees, available_slots)
	available_slots -= num_allowed_endorsees

	max_allowed_newbies  = (num_bootstrappers + num_allowed_reputables + num_allowed_endorsees) // 3
	num_allowed_newbies = min(num_newbies, available_slots)
	num_allowed_newbies = min(num_allowed_newbies, max_allowed_newbies)
	available_slots -= num_allowed_newbies

	
	num_participants = num_bootstrappers + num_allowed_reputables + num_allowed_endorsees + num_allowed_newbies
	print(f'number of participants: {num_participants}')
	num_meetups = int(math.ceil(num_participants / MEETUP_MULTIPLIER))
	num_allowed_bootstrappers = num_bootstrappers

	params_by_cat = {
	'bootstrappers':{
		's1' : random.choice(primes),
		's2' : random.choice(primes),
		'N' : num_meetups,
		'n' : num_meetups,
		'prefix' : 'B'
	},
	'reputables':{
		's1' : random.choice(primes),
		's2' : random.choice(primes),
		'N' : find_prime_below(num_allowed_reputables),
		'n' : num_meetups,
		'prefix' : 'R'
	},
	'endorsees':{
		's1' : random.choice(primes),
		's2' : random.choice(primes),
		'N' : find_prime_below(num_allowed_endorsees),
		'n' : num_meetups,
		'prefix' : 'E'
	},
	'newbies':{
		's1' : random.choice(primes),
		's2' : random.choice(primes),
		'N' : find_prime_below(num_allowed_newbies),
		'n' : num_meetups,
		'prefix' : 'N'
	}

	}


	meetups = [[] for _ in range(num_meetups)]
	# distribute participants
	for cat in ['bootstrappers', 'reputables', 'endorsees', 'newbies']:
		params = params_by_cat[cat]
		num = locals()[f'num_allowed_{cat}']
		s1 = params['s1']
		s2 = params['s2']
		N = params['N']
		n = params['n']
		prefix = params['prefix']

		for i in range(num):
			meetup = get_meetup_location(i, N, n, s1, s2)
			meetups[meetup].append(f'{prefix}{i}')

	for m in meetups:
		print(m)
	analyze_meetups(meetups)




if __name__ == '__main__':
	test_distribution()


