uWu_nyaa() => {
    yomu_ln("Welcome to the guessing game!")

    num_to_guess = 10
    guesses_left = 5
    guess = 5

    yomu_ln("Guess the number...")
    yomu_ln("You have", guesses_left, "left")

    # Game loop
    daijoubu (guesses_left != 0) {
        guess++

        # Check if guessed number is correct
        nani (guess == num_to_guess) {
            yomu_ln("You guessed the correct number!")
            guesses_left = 0
        } baka {
            guesses_left--
            yomu_ln("You have", guesses_left, "left")
        }
    }
}
