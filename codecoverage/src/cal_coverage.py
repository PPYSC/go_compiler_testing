import json
import subprocess
import shlex
import os
import shutil
import jsonlines
from tqdm import tqdm
import re


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        return True
    else:
        return False


def rmdir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


class CalCoverage:
    def make_test_unit(self, path, name, code):
        dir_path = path + "/" + name
        if mkdir(dir_path):
            cmd = f"cd {dir_path} && exec 2>/dev/null && go mod init {name}"
            subprocess.run(cmd, shell=True)

            with open(dir_path + "/main.go", "w") as file:
                file.write(code)
            if not os.path.isfile(dir_path + "/main.go"):
                return False
            
            cmd = f"cd {dir_path} && exec 2>/dev/null && go list -f '{{{{.ImportPath}}}}' -deps . | paste -sd ',' > pkgs.txt"
            subprocess.run(cmd, shell=True)

            if not os.path.isfile(dir_path + "/pkgs.txt"):
                return False

            return True
        else:
            return False


    # 删除所有文件以便下一个数据开始处理
    def clear(self, path, name):
        dir_path = path + "/" + name
        rmdir(dir_path)
    
    def cal_result(self, path):
        with open(path, 'r') as file:
            lines = file.readlines()

        percentage_sum = 0.0
        for line in lines:
            match = re.search(r'coverage:\s*([\d.]+)%', line)
            if match:
                percentage = float(match.group(1))
                percentage_sum += percentage

        return percentage_sum

    def cal_coverage(self, path, name, code):
        self.clear(path, name)
        if self.make_test_unit(path, name, code):
            dir_path = path + "/" + name

            coverpkg = "`cat pkgs.txt`"
            cmd = f"cd {dir_path} && exec 2>/dev/null && go build -o exe -coverpkg={coverpkg} ."
            subprocess.run(cmd, shell=True)

            if not os.path.isfile(dir_path + "/exe"):
                data = {"code": code}
                fail_path = path + "/fail_compile.jsonl"
                with jsonlines.open(fail_path, "a") as f:
                    f.write(data)
                return 0

            mkdir(dir_path + "/covdata")

            cmd = f"cd {dir_path} && exec 2>/dev/null && GOCOVERDIR=covdata ./exe"
            #subprocess.run(cmd, shell=True)
            try:
                subprocess.run(cmd, shell=True, timeout=60)
            except subprocess.TimeoutExpired:
                print("timeout")

            cmd = f"cd {dir_path} && exec 2>/dev/null && go tool covdata percent -i=covdata > result.txt"
            subprocess.run(cmd, shell=True)

            merged_path = path + "/merged"
            cmd = f"cd {dir_path} && exec 2>/dev/null && go tool covdata merge -i=covdata -o {merged_path}"
            subprocess.run(cmd, shell=True)

            if not os.path.isfile(dir_path + "/result.txt"):
                return 0

            percentage_sum = self.cal_result(dir_path + "/result.txt")

            self.clear(path, name)

            return percentage_sum
        else:
            print("can't make unit")
            return 0

