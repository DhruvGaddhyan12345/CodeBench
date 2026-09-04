def classify_failure(grade_status: str, trajectory: list[dict], repeated_statuses: list[str] | None = None) -> str | None:
    if repeated_statuses and len(set(repeated_statuses)) > 1:
        return "Flakiness"
    if grade_status == "PASS":
        return None
    if grade_status == "TIMEOUT":
        return "Timeout"
    if grade_status == "EXECUTION_ERROR":
        return "Test-execution failure"
    if "repository_search" not in [entry["tool"] for entry in trajectory]:
        return "Localization failure"
    return "Patch-generation failure"
