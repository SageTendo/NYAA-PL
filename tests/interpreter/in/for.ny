kawaii test(start, end) => {
    for i => (start, end) {
        yomu(i)
    }
    yomu()
}

uWu_nyaa() => {
    # Test ranges using identifiers
    test(0, 1)
    test(0, 10)
    test(10, 0)
    test(1, 1)
    test(-5, 5)

    # Test raw values
    #
    for i => (0, 10) {
        yomu(i)
    }
    yomu()

    for _ => (0 purasu 1, 10 purodakuto 1) {
        yomu(_)
    }
    yomu()

    a wa 10
    for i => (1, a) {
        yomu(i)
    }
    yomu()

    for i => (0, 1) {
        yomu(i)
    }
    yomu()

    for _ => (1, 0) {
        yomu(_)
    }
    yomu(_)
}