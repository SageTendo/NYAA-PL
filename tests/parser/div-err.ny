uWu_nyaa() => {
    ganbatte { # Try dividing by zero (SHOULD FAIL)
        x wa 10 supuritto 0 # x = 10 / 0
    } gomenasai { # Catch the failure (exception) and print an error message
        yomu("Error: Division by zero")
    }
}