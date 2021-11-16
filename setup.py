
from setuptools import setup, find_namespace_packages, findall

package_data = \
    findall(dir='./davidson/runtime/share')+\
    findall(dir='./davidson/runtime/icons')

setup(
    name="jupyter-davidson",
    version='0.3.1',
    packages=find_namespace_packages(
        include=['davidson.*']
    ),
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
            'config/hub.d/*.py'
        ]),
        ('share/jupyterhub/templates', [
            'share/jupyterhub/templates/duo.html',
            'share/jupyterhub/static/components/duo/css',
            'share/jupyterhub/static/components/duo/css/Duo-Frame.css',
            'share/jupyterhub/static/components/duo/js',
            'share/jupyterhub/static/components/duo/js/Duo-Web-v2.js',
            'share/jupyterhub/static/components/duo/js/Duo-Web-v2.min.js'
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
        # build requirement
        'setuptools_rust',
        'duo_web',
        
        # hub
        'jupyterhub==1.4.2',
        'batchspawner @ git+https://github.com/jupyterhub/batchspawner@ab0e00e',
        'jupyterhub-ldapauthenticator @ git+https://github.com/jupyterhub/ldapauthenticator@24f11eb',
        
        #'jupyterhub-duoauthenticator @ git+https://github.com/possiblyMikeB/jupyter-duoauthenticator.git@a617827',
        'jupyterhub-traefik-proxy @ git+https://github.com/possiblyMikeB/traefik-proxy@traefik-v2',
        'jupyterhub-idle-culler @ git+https://github.com/jupyterhub/jupyterhub-idle-culler@80c8c17',
        'jupyterhub-announcement @ git+https://github.com/rcthomas/jupyterhub-announcement.git@1504bf2'
        
        # runtime
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
