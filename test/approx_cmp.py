from fvalues import F


from src.api.defs import classify


class ApproximateEqualityError(AssertionError):
    def __init__(self, str1, str2):
        super().__init__(
            f"Strings not approximately equal:\nExpected: {str2}\nActual  : {str1}"
        )


class ApproximateCmpError(AssertionError):
    def __init__(self, str1, str2):
        super().__init__(
            f"Actual string not at least as informative as expected:\nExpected: {str2}\nActual  : {str1}"
        )


# TODO: these comparisons may need to include context to more accurately assess the outputs


async def approx_eq(str1: str, str2: str) -> bool:
    res = await classify(
        F(
            f"""Quote 1: "{str1}"

Quote 2: "{str2}"
"""
        ).strip(),
        ["Yes", "No"],
        "Do these quotes mean approximately the same thing?",
    )
    if res == "No":
        raise ApproximateEqualityError(str1, str2)
    return True


async def approx_gt(str1: str, str2: str) -> bool:
    res = await classify(
        F(
            f"""Quote 1: "{str1}"

Quote 2: "{str2}"
"""
        ).strip(),
        [
            "Quote 1",
            "Quote 2",
            "Neither",
        ],
        "Which quote is more informative?",
    )
    if res == "Quote 2":
        raise ApproximateCmpError(str1, str2)
    return True
