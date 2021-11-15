
from setuptools import setup, find_packages, findall

package_data = \
    findall(dir='./davidson_jupyter/share')+\
    findall(dir='./davidson_jupyter/icons')

setup(
    name="davidson-jupyter-runtime",
    packages=find_packages(),
    version='0.2.1',
    package_data={
        'davidson_jupyter':
           [ obj.replace('/davidson_jupyter','') for obj in package_data ]
    },
    data_files=[
        ('etc/jupyter', [
            'config/jupyter_lab_config.py',
            'config/jupyter_server_config.py',
            'config/jupyter_notebook_config.py'
        ])
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'desktop = davidson_jupyter:setup_desktop',
            'rstudio = davidson_jupyter:setup_rserver',
            'theia = davidson_jupyter:setup_theia'
        ]
    },
    install_requires=[
        'jupyterhub==1.4.2',
        'jupyter-archive>=3.2.0',
        'jupyter-server-proxy>=1.2.0',
        'jupyterlab==3.2',
        'jupyterlab-git>=0.34 ',
        'jupyter-resource-usage @ git+https://www.github.com/possiblyMikeB/nbresuse.git@davidson',
        'jupyterlab-system-monitor @ git+https://www.github.com/possiblyMikeB/jupyterlab-system-monitor.git',
        'jupyterlab_widgets',
        'nbgitpuller',
        'ipympl>=0.8.2'
    ],
    include_package_data=True,
    zip_safe=False
)
