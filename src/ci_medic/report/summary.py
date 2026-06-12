def write_summary(text: str, path: str = "GITHUB_STEP_SUMMARY") -> None:
    """Append markdown to the GitHub step summary file."""
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)
        handle.write("\n")
