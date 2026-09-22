import time


def with_retries(fn, attempts: int = 3, delay: float = 0.2):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            if i < attempts - 1:
                time.sleep(delay * (i + 1))
    raise last
