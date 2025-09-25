from setuptools import setup, find_packages

setup(
    name="hcp-config-validator",
    version="1.0.0",
    description="HashiCorp Configuration Validator - Security and best practice validation for Vault, Consul, and Nomad",
    author="Himanshu Sharma",
    author_email="himanshu.sharma@example.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'validator': ['rules/*.yaml'],
    },
    install_requires=[
        "click>=8.0.0",
        "jmespath>=1.0.0",
        "pyyaml>=6.0",
        "rich>=10.0.0",
        "python-hcl2>=3.0.0",
        "jsonschema>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "hcp-config-validator=validator.main:cli",
            "check-hcp-config=validator.cli:main",  # Keep backward compatibility
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="hashicorp vault consul nomad configuration validation security",
)
