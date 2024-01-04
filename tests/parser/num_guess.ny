uWu_nyaa() => {
    yomu("Welcome to the guessing game!")

    num_to_guess wa 10
    guesses_left wa 5
    guess wa 5

    yomu("Guess the number...")
    yomu("You have", guesses_left, "left")

    # Game loop
    daijoubu (guesses_left != 0) {
        guess++

        # Check if guessed number is correct
        nani (guess == num_to_guess) {
            yomu("You guessed the correct number!")
            guesses_left wa 0
        } baka {
            guesses_left--
            yomu("You have", guesses_left, "left")
        }
    }
}
