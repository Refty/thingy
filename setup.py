from setuptools import setup


def get_description():
    with open("README.rst") as file:
        return file.read()


setup(
    name="Thingy",
    version="0.1.0",
    url="https://github.com/numberly/thingy",
    license="MIT",
    author="Guillaume Gelin",
    author_email="ramnes@1000mercis.com",
    description="Dictionary as an object, that can have different views",
    long_description=get_description(),
    py_modules=["thingy"],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
