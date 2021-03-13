import subprocess


def run_command(cmd: str, error: bool = False) -> str:
    output = subprocess.run(cmd.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    output_string = output.stdout.decode('utf-8')

    if error:
        output_string = output.stderr.decode('utf-8')

    return output_string
