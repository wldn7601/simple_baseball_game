def game_check(guess: str, target: str):
    strike = 0
    ball = 0

    for i in range(4):
        if guess[i] == target[i]:
            strike += 1
        elif guess[i] in target:
            ball += 1

    return strike, ball
