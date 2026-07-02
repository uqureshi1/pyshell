class JobTable:
    """Tracks background (`&`) jobs for the current shell session."""

    def __init__(self):
        self._jobs = []

    def add(self, process, command_str):
        job = {"id": len(self._jobs) + 1, "process": process, "command": command_str}
        self._jobs.append(job)
        return job

    def render(self, completed_only=False):
        """Return status lines for the current jobs."""
        lines = []
        keep = []
        last_index = len(self._jobs) - 1
        for index, job in enumerate(self._jobs):
            marker = "+" if index == last_index else "-" if index == last_index - 1 else " "
            status = "Running" if job["process"].poll() is None else "Done"

            if status == "Running":
                keep.append(job)
                if completed_only:
                    continue

            suffix = " &" if status == "Running" else ""
            lines.append(f"[{job['id']}]{marker}  {status:<24}{job['command']}{suffix}")

        self._jobs = keep
        return lines
