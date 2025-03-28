uWu_nyaa() => {
  new_file_name wa "./tests/interpreter/out/file_test.out"
  access_mode wa "w"
  f => f_open(new_file_name, access_mode)

  #f wa "file.txt"
  #r wa "r"
  #f => f_open(f, r)

  #f_read(f, 1)
  #out wa f_read(f, 1)

  #f_readline(f)
  #out wa f_readline(f)

  #buff => {0, 1, 2}
  #f_write(f, "Hello")
  #f_write(f, buff)
  #f_write(f, f)

  #f_writeline(f, "Hello")
  #f_writeline(f, buff)
  #f_writeline(f, f)
  #f_close(f)
}