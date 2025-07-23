from setuptools import setup, find_packages

setup(
    name='vscheduler',
    version='2.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'paramiko', 
        'PyMySQL', 
        'numpy', 
        'tabulate', 
        'rich', 
        'jinja2', 
        'plotly', 
        'kaleido', 
        'calmap', 
        'calplot',
        'setuptools',
        'pyyaml',
        'requests',
        'guacamole-api-wrapper'
    ],
    entry_points={
        'console_scripts': [
            'vkill = vscheduler.tools.kill:main',
            'vsync = vscheduler.tools.guaca:main',
            'vquota = vscheduler.tools.quota:main',
            'vmanage = vscheduler.tools.booked:main',
            'valloc = vscheduler.tools.allocate:main',
            'vreport = vscheduler.tools.report:main',
            # 'vset = vscheduler.tools.set:main',
            'vinfo = vscheduler.tools.info:main',
            'vexcept = vscheduler.tools.excepted:main',
            'vcontrol = vscheduler.tools.control:main',
        ],
    },
)
# print (setuptools.find_packages())