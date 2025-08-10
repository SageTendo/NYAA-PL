kawaii init_tape(size) => {
    for _ => (0, size) {
        tape[_] = 0
    }
}

kawaii scan_loops() => {
    pc = 0
    sp = -1

    daijoubu (pc < program_size) { # 106 is the length of the BF program
        byte = program[pc]
        nani (byte == "[") {
            sp++
            stack[sp] = pc
        } nandesuka (byte == "]") {
            loops[stack[sp]] = pc
            sp--
        }

        pc++
    }
}

kawaii interpret() => {
    pc = 0
    pointer = 0
    sp = -1

    daijoubu(pc < program_size) {
        byte = program[pc]
        pc++

        nani (byte == "[") {
            nani (tape[pointer] == 0) {
                pc = loops[pc]
                motto
            }
            sp++
            stack[sp] = pc
        } nandesuka (byte == "]") {
            nani (tape[pointer] != 0) {
                pc = stack[sp]
                motto
            }
            sp--
        } nandesuka (byte == ">") {
            nani (pointer + 1 < tape_size) {
                pointer++
            } baka { pointer = 0 }
        } nandesuka (byte == "<") {
            nani (pointer > 0) {
                pointer--
            }
        } nandesuka (byte == "+") {
            new_val = tape[pointer] + 1
            nani (new_val <= 255) {
                tape[pointer] = new_val
            } baka { tape[pointer] = 0 }
        } nandesuka (byte == "-") {
            new_val = tape[pointer] - 1
            nani (new_val >= 0) {
                tape[pointer] = new_val
            } baka { tape[pointer] = 255 }
        } nandesuka (byte == ".") {
            val = tape[pointer]
            yomu_ln(val)
        } nandesuka (byte == ",") {
            val = ohayo("user input: ")
            tape[pointer] = val
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
    program_size = 106


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
    tape_size = 10000
    tape => [tape_size]
    init_tape(tape_size)
    interpret()
}