from diff_test.cmd_runner import CmdRunner
from diff_test.diff_test_runner import DiffTestRunner


cmdrunnerlist = [CmdRunner("go build -o exe0", "./exe0"), CmdRunner("go build -compiler=gccgo -o exe1", "./exe1")]

difftestrunner = DiffTestRunner(cmdrunnerlist, "/home/shareduser/ysc/go_compiler_testing/difftest/tb")

check, rst = difftestrunner.run()

print(check)
print(rst)

