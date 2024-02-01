import os
from setuptools import setup, find_packages

files = []
for item in os.walk("pyi/aiophoenixdb"):
    base_path = item[0][4:]
    files.append((base_path, [os.path.join(item[0], f) for f in item[-1]]))

with open("README.rst", "r") as f:
    long_desc_text = f.read()

setup(
    name="aiophoenixdb"
    , version="0.0.6"
    , author="Nick Hao"
    , author_email="nickwike72@gmail.com"
    , package_dir={"aiophoenixdb": "./src/aiophoenixdb"}
    , description="Asyncio with phoenixdb"
    , packages=find_packages(include=['aiophoenixdb*'], where="./src")
    , data_files=files
    , long_description_content_type="text/x-rst"
    , long_description=long_desc_text
    , license="Apache 2"
    , project_urls={
        "Github: repo": "https://github.com/NickWike/async_phoenixdb"
    }
    , install_requires=[
        "betterproto>=2.0.0b6",
        "aiohttp>=3.8.6",
        "requests-gssapi",
        "requests~=2.31.0",
        "gssapi"
    ]
    , classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)
