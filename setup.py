from setuptools import setup, find_packages

setup(
    name="amazon-paapi5-python-sdk",
    version="1.0.3",
    description="Amazon Product Advertising API v5 Python SDK (Most Advance SDK)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Hitesh Rajpurohit",
    url="https://github.com/rajpurohithitesh/amazon-paapi5-python-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.28.0",
        "aiohttp>=3.8.0",
        "cachetools>=5.0.0",
        "cryptography>=3.4.8",
    ],
    extras_require={
        "redis": ["redis>=4.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)