from cal_coverage import CalCoverage

cal_coverage = CalCoverage()

path = "/home/shareduser/ysc/go_compiler_testing/difftest/src/test_unit"

name = "t_cal"

code = "package main\n\nimport \"fmt\"\n\nvar tbd string\nvar overwrite string = \"dibs\"\n\nvar tbdcopy = tbd\nvar overwritecopy = overwrite\nvar arraycopy = [2]string{tbd, overwrite}\n\nvar b bool\nvar x int\n\nfunc main() {\n\tfmt.Println(tbd)\n\tfmt.Println(tbdcopy)\n\tfmt.Println(arraycopy[0])\n\n\tfmt.Println(overwrite)\n\tfmt.Println(overwritecopy)\n\tfmt.Println(arraycopy[1])\n\n\tif b || x != 0 {\n\t\tpanic(\"b or x overwritten\")\n\t}\n}"

rst_cov = cal_coverage.cal_coverage(path, name, code)

print(rst_cov)
