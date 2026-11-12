"""Prompted start/stop of the vScheduler management systemd service."""
import shutil
import subprocess

MGMT_SERVICE = "mgmt_socket.service"
PAST_TENSE = {"start": "started", "stop": "stopped"}


def confirm(question):
    try:
        return input(question + " [y/N]: ").strip().casefold() in ("y", "yes")
    except EOFError:
        return False


def _is_active(systemctl, service):
    return subprocess.run(
        [systemctl, "is-active", "--quiet", service],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    ).returncode == 0


def control_service(action, service=MGMT_SERVICE):
    """Prompt, then start or stop service.

    Returns (status, message) where status is PASS, SKIP or FAIL. Nothing is
    prompted when the service is already in the requested state.
    """
    systemctl = shutil.which("systemctl")
    if not systemctl:
        return "SKIP", "systemctl is not available"

    want_active = action == "start"
    if _is_active(systemctl, service) == want_active:
        return "PASS", "{} is already {}".format(service, "active" if want_active else "inactive")

    if not confirm("{} {}?".format(action.capitalize(), service)):
        return "SKIP", "{} was not {}; declined".format(service, PAST_TENSE[action])

    result = subprocess.run(
        [systemctl, action, service],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, check=False,
    )
    if result.returncode != 0 or _is_active(systemctl, service) != want_active:
        error = result.stderr.strip() or "service state did not change"
        return "FAIL", "could not {} {}: {}".format(action, service, error)
    return "PASS", "{} {}".format(service, PAST_TENSE[action])
