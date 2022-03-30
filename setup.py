import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="notiondb",
    version="1.0.2",
    author="Viet Hoang",
    author_email="ngviethoang0212@gmail.com",
    description="Python 3 tools for interacting with Notion API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ngviethoang/notiondb",
    project_urls={
        "Bug Tracker": "https://github.com/ngviethoang/notiondb/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
