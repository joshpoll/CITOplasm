from fvalues import F


from src.api.classify import *


@dataclass(frozen=True)
class Yes(BaseOption):
    desc: Optional[str] = None


@dataclass(frozen=True)
class No(BaseOption):
    desc: Optional[str] = None


@dataclass(frozen=True)
class Quote1(BaseOption):
    desc: str = "Quote 1"


@dataclass(frozen=True)
class Quote2(BaseOption):
    desc: str = "Quote 2"


@dataclass(frozen=True)
class Neither(BaseOption):
    desc: str = "Neither"


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
        "Do these quotes mean approximately the same thing?",
        [Yes, No],
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
        "Which quote is more informative?",
        [
            Quote1,
            Quote2,
            Neither,
        ],
    )
    if res == Quote2:
        raise ApproximateCmpError(str1, str2)
    return True
