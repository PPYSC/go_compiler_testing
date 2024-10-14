import subprocess


class CmdRunner:
    def __init__(self, compile_cmd, execute_cmd):
        self.compile_cmd = compile_cmd
        self.execute_cmd = execute_cmd
    def __repr__(self):
        return f"<CmdRunner: {self.compile_cmd}, {self.execute_cmd}>"

    def _run_cmd(self, cmd, cwd):
        try:
            return subprocess.run(cmd, cwd=cwd, shell=True, encoding="utf8", errors='replace', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="Command timed out",
            )

    def run(self, project_path):
        completed_progress_list = []
        completed_progress_list.append(self._run_cmd(self.compile_cmd, project_path))
        completed_progress_list.append(self._run_cmd(self.execute_cmd, project_path))
        return completed_progress_list
