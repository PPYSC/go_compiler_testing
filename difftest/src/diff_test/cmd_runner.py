import subprocess


class CmdRunner:
    def __init__(self, compile_cmd, execute_cmd):
        self.compile_cmd = compile_cmd
        self.execute_cmd = execute_cmd
    def __repr__(self):
        return f"<CmdRunner: {self.compile_cmd}, {self.execute_cmd}>"

    def _run_cmd(self, cmd):
        return subprocess.run(cmd, capture_output=True, shell=True, encoding="utf8")

    def run(self, project_path):
        completed_progress_list = []
        cmd = f"cd {project_path} && {self.compile_cmd}"
        completed_progress_list.append(self._run_cmd(cmd))
        cmd = f"cd {project_path} && {self.execute_cmd}"
        completed_progress_list.append(self._run_cmd(cmd))
        return completed_progress_list
