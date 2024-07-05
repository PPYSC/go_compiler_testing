

class DiffTestRunner:
    def __init__(self, cmd_runner_list, project_path):
        self.cmd_runner_list = cmd_runner_list
        self.project_path = project_path

        self.runner_rst_list = []

    def check(self):
        '''
        1 is same
        -1 is different
        0 is unknown
        '''
        # check compile returncode
        compile_returncode_check = all(runner_rst[0].returncode == self.runner_rst_list[0][0].returncode for runner_rst in self.runner_rst_list)
        # check execute returncode
        execute_returncode_check = all(runner_rst[1].returncode == self.runner_rst_list[0][1].returncode for runner_rst in self.runner_rst_list)
        # check execute stdout
        execute_stdout_check = all(runner_rst[1].stdout == self.runner_rst_list[0][1].stdout for runner_rst in self.runner_rst_list)
        # check execute stderr
        # execute_check = all(runner_rst[1].stderr == self.runner_rst_list[0][1].stderr for runner_rst in self.runner_rst_list)

        if compile_returncode_check:
            if self.runner_rst_list[0][0].returncode == 0:
                if execute_returncode_check:
                    if self.runner_rst_list[0][1].returncode == 0:
                        if execute_stdout_check:
                            return 1
                        else:
                            return -1
                    else:
                        return 0
                else:
                    return -1
            else:
                return 0
        else:
            return -1

    def run(self):
        for cmd_runner in self.cmd_runner_list:
            self.runner_rst_list.append(cmd_runner.run(self.project_path))
        
        return self.check(), self.runner_rst_list







