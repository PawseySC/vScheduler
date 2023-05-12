from setuptools import setup, find_packages

setup(
    name='vscheduler',
    version='2023.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click','paramiko==3.0.0', 'PyMySQL==1.0.2', 'numpy==1.24.3', 'tabulate',
    ],
    entry_points={
        'console_scripts': [
            'vsync = vscheduler.tools.guaca:main',
            'vquota = vscheduler.tools.quota:main',
            'vmanage = vscheduler.tools.booked:main',
            # 'vinfo = vscheduler.tools.info:cli',
            # 'vreport = vscheduler.tools.report:main',
            'valloc = vscheduler.tools.allocate:main',
            # 'vcontrol = vscheduler.tools.control:cli',
        ],
    },
)