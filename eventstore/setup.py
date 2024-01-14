from setuptools import setup, find_namespace_packages

description = "EventStore component of testcontainers-python."

setup(
    name="testcontainers-eventstore",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description=description,
    long_description=description,
    long_description_content_type="text/x-rst",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "esdbclient",
    ],
    python_requires=">=3.7",
)
