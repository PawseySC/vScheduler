from setuptools import setup, find_packages

setup(
    name='vscheduler',
    version='2023.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==8.1.3','paramiko==3.0.0', 'PyMySQL==1.0.2', 'numpy==1.24.3', 'tabulate==0.9.0', 'rich==13.3.5', 'jinja2==3.1.2', 'plotly==5.16.1', 'kaleido==0.2.1', 'calmap==0.0.11', 'calplot==0.1.7.5'
    ],
    entry_points={
        'console_scripts': [
            'vkill = vscheduler.tools.kill:main',
            'vsync = vscheduler.tools.guaca:main',
            'vquota = vscheduler.tools.quota:main',
            'vmanage = vscheduler.tools.booked:main',
            'valloc = vscheduler.tools.allocate:main',
            'vreport = vscheduler.tools.report:main',
            'vset = vscheduler.tools.stat:main',
            'vmaintenance = vscheduler.tools.maintain:main',
            # 'vcontrol = vscheduler.tools.control:cli',
            # 'vinfo = vscheduler.tools.info:cli',
        ],
    },
)