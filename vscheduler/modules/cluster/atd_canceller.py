import re
import subprocess
from vscheduler.log.log import Capture_log

atd_records = Capture_log("atd", __file__)
logger_unix = atd_records.log_agent("linux")

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
    try:
        atq_result = subprocess.run(
            ["/usr/bin/atq"], check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as error:
        logger_unix.error(
            "Could not list atd jobs with atq: %s; stderr: %s",
            error,
            getattr(error, "stderr", None),
        )
        raise

    cancelled_jobs = []

    for line in atq_result.stdout.splitlines():
        fields = line.split()
        if not fields or not fields[0].isdigit():
            continue

        job_id = fields[0]
        try:
            job_script = subprocess.run(
                ["/usr/bin/at", "-c", job_id], check=True, capture_output=True, text=True
            ).stdout
        except (OSError, subprocess.CalledProcessError) as error:
            logger_unix.error(
                "Could not inspect atd job %s with at -c: %s; stderr: %s",
                job_id,
                error,
                getattr(error, "stderr", None),
            )
            raise

        if _matches_job(job_script, user, node):
            subprocess.run(
                ["/usr/bin/atrm", job_id], check=True, capture_output=True, text=True
            )
            cancelled_jobs.append(job_id)

    return cancelled_jobs
