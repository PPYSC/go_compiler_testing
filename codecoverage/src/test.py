from cal_coverage import CalCoverage

cal_coverage = CalCoverage()

path = "/home/shareduser/ysc/go_compiler_testing/codecoverage/test_unit"

name = "t_cal"

code = "package main\n\n\nfunc Generate(ch chan<- int) {\n\tfor i := 2; ; i++ {\n\t\tch <- i \n\t}\n}\n\n\n\nfunc Filter(in <-chan int, out chan<- int, prime int) {\n\tfor {\n\t\ti := <-in \n\t\tif i%prime != 0 {\n\t\t\tout <- i \n\t\t}\n\t}\n}\n\n\nfunc Sieve() {\n\tch := make(chan int) \n\tgo Generate(ch)      \n\tfor {\n\t\tprime := <-ch\n\t\tprint(prime, \"\\n\")\n\t\tch1 := make(chan int)\n\t\tgo Filter(ch, ch1, prime)\n\t\tch = ch1\n\t}\n}\n\nfunc main() {\n\tSieve()\n}"
rst_cov = cal_coverage.cal_coverage(path, name, code)

print(rst_cov)



