from ice.recipe import recipe


async def say_josh():
    return "Josh"


async def say_hello():
    josh = await say_josh()
    return f"Hello, {josh}!"


recipe.main(say_hello)
