from setuptools import setup, find_packages, findall

package_data = findall(dir='./davidson_jupyter/share')+\
    findall(dir='./davidson_jupyter/icons')

setup(
    name="davidson-jupyter",
    packages=find_packages(),
    version='0.1.1',
    package_data={
        'davidson_jupyter':
           [ obj.replace('/davidson_jupyter','') for obj in package_data ]
    },
    entry_points={
        'jupyter_serverproxy_servers': [
            'desktop = davidson_jupyter:setup_desktop',
            'rstudio = davidson_jupyter:setup_rserver',
            'theia = davidson_jupyter:setup_theia'
        ]
    },
    install_requires=['jupyter-server-proxy>=1.2.0'],
    include_package_data=True,
    zip_safe=False
)
