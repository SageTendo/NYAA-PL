kawaii say_hello() => {
    yomu("Hello")
}

kawaii say_world() => {
    yomu("World")
}

kawaii greet(hello_func, world_func) => {
    hello_func()
    yomu(" ")
    world_func()
}

kawaii first_class() => {
    yomu_ln("First class")
}

kawaii first_class_with_arg(x) => {
    modoru x
}

kawaii first_class_with_func_arg(func) => {
    modoru func
}

uWu_nyaa() => {
    # This should print "First class" twice
    first_class()
    x = first_class
    x()

    # This should print 10 twice
    yomu_ln(first_class_with_arg(10))
    x = first_class_with_arg
    yomu_ln(x(10))

    # This should print "Hello"
    # What doesn't work: returnSomeFunc(someFunc)(), and probably won't support it
    wrapped = first_class_with_func_arg(say_hello)
    wrapped()
    yomu_ln()

    # This should print "Hello World"
    greet(say_hello, say_world)
    yomu_ln()

    arr => {say_hello, say_world}
    greet(arr[0], arr[1])
}

