def truncate(text: str, width: int, suffix: str = "…") -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - len(suffix))] + suffix


def indent(block: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line for line in block.splitlines())
