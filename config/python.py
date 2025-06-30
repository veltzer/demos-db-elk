""" python deps for this project """


import config.shared


install_requires: list[str] = [
    "elasticsearch",
]
build_requires: list[str] = config.shared.BUILD
requires = install_requires + build_requires
