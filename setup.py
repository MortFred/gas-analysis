from setuptools import find_packages, setup

setup(
    name="gas-analysis",
    description="Analysis of thermal video files to identify gas.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Equinor ASA",
    author_email="fg_robots_dev@equinor.com",
    url="https://github.com/equinor/gas-analysis",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "numpy"
    ],
    extras_require={
        "dev": [
            "black"
        ]
    },
    python_requires=">=3.10",
)
