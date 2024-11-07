from setuptools import setup, find_packages

setup(
    name="ml-trading-system",
    version="0.1.0",
    description="Advanced ML-Driven Algorithmic Trading System",
    author="Trading System Team",
    packages=find_packages(),
    install_requires=[
        "yfinance>=0.2.0",
        "pandas<2.0.0",  # Ensure compatibility with Python 3.8
        "numpy<1.25.0",  # Ensure compatibility with Python 3.8
        "influxdb-client>=1.36.0",
        "redis>=4.5.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0.0",
        "asyncio>=3.4.3",
        "prometheus-client>=0.17.0",
        "python-logging-loki>=0.3.1",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pyyaml>=6.0.0",
        "ta>=0.10.0"
    ],
    extras_require={
        'ml': [
            "scikit-learn<1.3.0",  # Ensure compatibility with Python 3.8
            "torch>=1.13.1,<2.0.0",  # Last version supporting Python 3.8
        ],
        'dev': [
            "black>=23.3.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ]
    },
    python_requires=">=3.8,<3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
