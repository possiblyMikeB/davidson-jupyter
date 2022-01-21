
from setuptools import setup, find_packages, findall

package_data = \
    findall(dir='./davidson/runtime/share')+\
    findall(dir='./davidson/runtime/icons')

setup(
    name="jupyter-davidson",
    version='0.3.1',
    packages=[
        'davidson.hub',
        'davidson.hub.api',
        'davidson.hub.ctl',
        'davidson.hub.ctl.tests',
        'davidson.runtime'
    ],
    package_data={
        'davidson.runtime':
           [ obj.replace('/davidson/runtime','') for obj in package_data ],
        'davidson.hub': []
    },
    data_files=[
        ('etc/jupyter', [
            'config/jupyter_lab_config.py',
            'config/jupyter_server_config.py',
            'config/jupyter_notebook_config.py'
        ]),
        ('etc/jupyterhub/conf.d', [
            'config/hub.d/00-common.py',
            'config/hub.d/00-handler-pages.py',
            'config/hub.d/01-tls-cluster.py',
            'config/hub.d/01-tls-internal.py',
            'config/hub.d/01-tls-watson.py',
            'config/hub.d/02-service-common.py',
            'config/hub.d/02-service-announcements.py',
            'config/hub.d/02-service-cull-idle.py',
            'config/hub.d/03-proxy-common.py',
            'config/hub.d/03-proxy-chp-image.py',
            'config/hub.d/03-proxy-chp-managed.py',
            'config/hub.d/03-proxy-traefik-etcd.py',
            'config/hub.d/04-spawner-common.py',
            'config/hub.d/04-spawner-csystemd.py',
            'config/hub.d/04-spawner-dummy.py',
            'config/hub.d/04-spawner-local.py',
            'config/hub.d/04-spawner-slurm.py',
            'config/hub.d/05-auth-common.py',
            'config/hub.d/05-auth-duo.py',
            'config/hub.d/05-auth-ldap.py',
            'config/hub.d/05-auth-lti.py',
            'config/hub.d/05-auth-pam.py'
        ])
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'desktop = davidson.runtime:setup_desktop',
            'rstudio = davidson.runtime:setup_rserver',
            'theia = davidson.runtime:setup_theia'
        ]
    },
    install_requires=[
        # build requirement
        'setuptools_rust',
        'duo_web',

        # hub
        'jupyterhub==1.4.2',

        # runtime
        'jupyter-archive>=3.2.0',
        'jupyter-server-proxy>=1.2.0',
        'jupyterlab==3.2',
        'jupyterlab-git>=0.34',
        'jupyter-resource-usage @ git+https://www.github.com/possiblyMikeB/nbresuse.git@davidson',
        'jupyterlab-system-monitor @ git+https://www.github.com/possiblyMikeB/jupyterlab-system-monitor.git',
        'jupyterlab_widgets',
        'nbgitpuller',
        'ipympl>=0.8.2',
        'numpy>=1.19.5',
        'scipy>=1.7.3',
        'sympy>=1.9',
        'pandas>=1.3.5',
        'scikit-learn>=1.0.2'
    ],
    include_package_data=True,
    zip_safe=False
)
