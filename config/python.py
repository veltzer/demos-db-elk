""" python deps for this project """

install_requires: list[str] = [
    "elasticsearch",
]
build_requires: list[str] = [
    "pymakehelper",
    "pydmt",
]
requires = install_requires + build_requires
