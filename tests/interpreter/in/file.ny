uWu_nyaa() => {
  new_file_name = "./tests/interpreter/out/file_out.txt"
  f => f_open(new_file_name, "w")
  buff => {new_file_name, " ", "write", "\n"}
  f_write(f, "Hello ")
  f_write(f, " ")
  f_write(f, "World\n")
  f_write(f, buff)
  f_close(f)

  f => f_open(new_file_name, "a")
  buff => {new_file_name, " ", "append"}
  f_writeline(f, "Hello")
  f_writeline(f, buff)
  f_close(f)

  f => f_open(new_file_name, "r")
  out = f_read(f, 1)
  yomu_ln(out)
  yomu_ln(f_read(f, 1))

  yomu(f_readline(f))
  yomu(f_readline(f))

  yomu_ln(f_read(f, 1))
  yomu(f_read(f))
}