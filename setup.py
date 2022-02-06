
from setuptools import setup, find_packages, findall

package_data = \
    findall(dir='./davidson/runtime/share')+\
    findall(dir='./davidson/runtime/icons')

setup(
    name="jupyter-davidson",
    version='0.3.1',
    python_requires='>=3.8',
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
        ('share/jupyter/kernels/python3', [
            'kernels/bundle/python-3.8/kernel.json',
            'kernels/bundle/python-3.8/logo-32x32.png',
            'kernels/bundle/python-3.8/logo-64x64.png'
        ]),
        ('share/jupyter/kernels/octave', [
            'kernels/bundle/octave/kernel.json',
            'kernels/bundle/octave/logo-32x32.png',
            'kernels/bundle/octave/logo-64x64.png'
        ]),
        ('share/jupyter/kernels/ir', [
            'kernels/bundle/ir/kernel.json',
            'kernels/bundle/ir/kernel.js',
            'kernels/bundle/ir/logo-64x64.png'
        ]),
        ('share/jupyter/kernels/python2', [
            'kernels/bundle/python-2.7/kernel.json',
            'kernels/bundle/python-2.7/logo-32x32.png',
            'kernels/bundle/python-2.7/logo-64x64.png'
        ]),
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
        ]),
        ('etc/jupyterhub', [
            'config/jupyterhub_config.py',
            'config/batch-script.sh.j2'
        ])
    ],
    entry_points={
        # install site jupyterhub-singleuser wrapper
        'console_scripts': [
            'jupyterhub-runner = davidson.runtime.singleuser:main'
        ],
        # server-proxy definitions 
        'jupyter_serverproxy_servers': [
            'desktop = davidson.runtime:setup_desktop',
            'rstudio = davidson.runtime:setup_rserver',
            'theia = davidson.runtime:setup_theia'
        ]
    },
    install_requires=[
        # build requirements
        'setuptools_rust',
        'duo_web',

        # hub
        'jupyterhub==1.4.2',
        'batchspawner==1.0.1',
        'jupyterhub-ldapauthenticator==1.3.2',
        'jupyterhub-traefik-proxy @ git+https://github.com/possiblyMikeB/traefik-proxy.git@traefik-v2-hack',
        'jupyterhub-duoauthenticator @ git+https://github.com/possiblyMikeB/jupyter-duoauthenticator.git#a6178272cc3153296a1fd5eab50bfd0a41658bff',
        'jupyterhub-idle-culler @ git+https://github.com/jupyterhub/jupyterhub-idle-culler.git#80c8c17e4b2aac11dab1c59079e7fc24e8c8ca48',
        'jupyterhub-announcement @ git+https://github.com/rcthomas/jupyterhub-announcement.git#1504bf2ff1f91a1524511c79f1bf44247aa226ca',
        
        # runtime
        'jupyterlab==3.2',
        'jupyter-archive>=3.2.0',
        'jupyter-server-proxy>=1.2.0',
        'jupyterlab-git>=0.34',
        'jupyter-resource-usage @ git+https://www.github.com/possiblyMikeB/nbresuse.git@davidson',
        'jupyterlab-system-monitor @ git+https://www.github.com/possiblyMikeB/jupyterlab-system-monitor.git',
        'jupyterlab_widgets',
        'nbgitpuller',
        'ipympl>=0.8.2',
        'ipywidgets>=7.6.5',
        'numpy>=1.19.5',
        'scipy>=1.5',
        'sympy>=1.9',
        'pandas>=1.2',
        'scikit-learn>=0.24',
        'scitools3>=1.0',
        
        # additional kernels
        'calysto_bash>=0.2.2'
    ],
    include_package_data=True,
    zip_safe=False
)
