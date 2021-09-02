# importing the module
import csv
 
# open the file in read mode
filename = open('ls30000000.csv', 'r')
 
# creating dictreader object
file = csv.reader(filename)
 
# creating empty lists
primes = []

# iterating over each row and append
# values to empty list
for row in file:
	num = int(row[0])
	primes.append(num)
	if num > 100000:
		break

print(f'analyzing primes up to {primes[-1]}')
biggest = (0, 0, 0)
for i in range(len(primes) - 1):
	prime = primes[i]
	next_prime = primes[i + 1]
	difference = next_prime - prime
	if difference > biggest[0]:
		biggest = (difference, prime, next_prime)

print(f'The biggest gap between primes is {biggest[0]} between {biggest[1]} and {biggest[2]}')
