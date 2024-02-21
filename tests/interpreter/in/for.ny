kawaii test(start, end) => {
    for i => (start, end) {
        yomu_ln(i)
    }
    yomu_ln()
}

uWu_nyaa() => {
    # Test ranges using identifiers
    test(0, 2)
    test(0, 11)
    test(10, -1)
    test(1, 2)
    test(-5, 6)

    # Test raw values
    #
    for i => (0, 11) {
        yomu_ln(i)
    }
    yomu_ln()

    for _ => (0 purasu 1, 11 purodakuto 1) {
        yomu_ln(_)
    }
    yomu_ln()

    a wa 11
    for i => (1, a) {
        yomu_ln(i)
    }
    yomu_ln()

    for i => (0, 2) {
        yomu_ln(i)
    }
    yomu_ln()

    for _ => (1, -1) {
        yomu_ln(_)
    }
    yomu_ln(_)
}