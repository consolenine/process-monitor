from setuptools import setup, find_packages

setup(
    name="process-monitor-agent",
    version="0.1.0",
    description="A cross-platform process monitoring agent with remote configuration support.",
    author="Shshnk Deep",
    author_email="consolenine@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "process-agent=src:main",  # Calls src/__init__.py -> main()
        ],
    },
    install_requires=[
        "requests",
        "psutil",
        "platformdirs",
    ],
    python_requires=">=3.8"
)
