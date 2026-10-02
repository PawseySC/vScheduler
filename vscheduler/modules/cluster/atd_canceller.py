import re
import subprocess


def _matches_job(script, user, node):
    command = re.compile(
        r"^\s*vkill\s+-u\s+"
        + re.escape(user)
        + r"\s+-n\s+"
        + re.escape(node)
        + r"\s+-v(?:\s|$)",
        re.MULTILINE,
    )
    return command.search(script) is not None


def cancel_atd(user, node):
    atq_result = subprocess.run(
        ["atq"], check=True, capture_output=True, text=True
    )
    cancelled_jobs = []

    for line in atq_result.stdout.splitlines():
        fields = line.split()
        if not fields or not fields[0].isdigit():
            continue

        job_id = fields[0]
        job_script = subprocess.run(
            ["at", "-c", job_id], check=True, capture_output=True, text=True
        ).stdout
        if _matches_job(job_script, user, node):
            subprocess.run(
                ["atrm", job_id], check=True, capture_output=True, text=True
            )
            cancelled_jobs.append(job_id)

    return cancelled_jobs
