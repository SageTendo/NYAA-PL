kawaii init_tape(size) => {
    for _ => (0, size) {
        tape[_] wa 0
    }
}

kawaii scan_loops() => {
    pc wa 0
    sp wa -1

    daijoubu (pc < program_size) { # 106 is the length of the BF program
        byte wa program[pc]
        nani (byte == "[") {
            sp++
            stack[sp] wa pc
        } nandesuka (byte == "]") {
            loops[stack[sp]] wa pc
            sp--
        }

        pc++
    }
}

kawaii interpret() => {
    pc wa 0
    pointer wa 0
    sp wa -1

    daijoubu(pc < program_size) {
        byte wa program[pc]
        pc++

        nani (byte == "[") {
            nani (tape[pointer] == 0) {
                pc wa loops[pc]
                motto
            }
            sp++
            stack[sp] wa pc
        } nandesuka (byte == "]") {
            nani (tape[pointer] != 0) {
                pc wa stack[sp]
                motto
            }
            sp--
        } nandesuka (byte == ">") {
            nani (pointer purasu 1 < tape_size) {
                pointer++
            } baka { pointer wa 0 }
        } nandesuka (byte == "<") {
            nani (pointer > 0) {
                pointer--
            }
        } nandesuka (byte == "+") {
            new_val wa tape[pointer] purasu 1
            nani (new_val <= 255) {
                tape[pointer] wa new_val
            } baka { tape[pointer] wa 0 }
        } nandesuka (byte == "-") {
            new_val wa tape[pointer] mainasu 1
            nani (new_val >= 0) {
                tape[pointer] wa new_val
            } baka { tape[pointer] wa 255 }
        } nandesuka (byte == ".") {
            val wa tape[pointer]
            yomu(asChar(val))
        } nandesuka (byte == ",") {
            val wa ohayo("user input: ")
            tape[pointer] wa val
        }
    }
    yomu_ln()
}

uWu_nyaa() => {
    ##
        A test example of "Hello World" in BrainFuck.
    ##
    program => {"+", "+", "+", "+", "+", "+", "+", "+", "[", ">", "+", "+", "+", "+", "[",
    ">", "+", "+", ">", "+", "+", "+", ">", "+", "+", "+", ">", "+", "<", "<", "<", "<",
    "-", "]", ">", "+", ">", "+", ">", "-", ">", ">", "+", "[", "<", "]", "<", "-", "]",
    ">", ">", ".", ">", "-", "-", "-", ".", "+", "+", "+", "+", "+", "+", "+", ".", ".",
    "+", "+", "+", ".", ">", ">", ".", "<", "-", ".", "<", ".", "+", "+", "+", ".", "-",
    "-", "-", "-", "-", "-", ".", "-", "-", "-", "-", "-", "-", "-", "-", ".", ">", ">",
    "+", ".", ">", "+", "+", "."}
    program_size wa 106


    ##
        Scan for loops and keep references to opening and closing positions
    ##
    loops => [1000]
    stack => [1000]
    scan_loops()

    ##
        Program execution
    ##
    stack => [100]
    tape_size wa 10000
    tape => [tape_size]
    init_tape(tape_size)
    interpret()
}