uWu_nyaa() => {
    buff_b => [10]
    yomu_ln(buff_b[0])

    for i => (1, 10) {
        buff_b[i] wa 0
        yomu_ln(buff_b[i])
    }
    yomu_ln()

    buff_c => {1, 2, 3}
    yomu_ln(buff_c)
    for i => (0, 3) {
        yomu_ln(buff_c[i])
    }
}