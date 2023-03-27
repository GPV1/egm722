import random

# pick a random number for the user to guess
rand = random.randint(1, 20)

for guessesTaken in range(1, 10):
    print('Guess a number between 1 and 20.')
    guess = int(input())  # number needs to be an integer

    if guess > rand:  # if the guess is too high, tell the user.
        print('Too high. Guess again.')
    elif guess < rand:  # if the guess is too low, tell the user.
        print('Too low. Guess again.')
    else:
        break # this condition is the right guess

if guess == rand:
    print('You got it! The number was {}'.format(rand) + ' You have guessed it in ' + str(guessesTaken) + ' guesses!')
else:
    print('Nope, the number was' + str(rand))