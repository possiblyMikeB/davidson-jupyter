from setuptools import setup, find_packages, findall

package_data = \
    findall(dir='./davidson/runtime/share')+\
    findall(dir='./davidson/runtime/icons')

setup(
    name="davidson-jupyter",
    version='0.3.1',
    python_requires='>=3.8',
    packages=[
        'davidson.hub',
        'davidson.hub.ctl',
        'davidson.runtime',
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
        
        ('etc/jupyterhub/conf.d',
            findall(dir='config/conf.d')
        ),
        ('etc/jupyterhub', [
            'config/jupyterhub_config.py',
            'config/batch-script.sh.j2'
        ]),
        ('share/jupyterhub/templates',
            findall(dir='share/jupyterhub/templates')
        )
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
        # all
        'setuptools_rust',
        'jupyterhub==1.4.2',

    ],
    extras_require={
        'hub': [
            'batchspawner==1.0.1',
            'jupyterhub-ldapauthenticator==1.3.2',
            'jupyterhub-traefik-proxy @ git+https://github.com/possiblyMikeB/traefik-proxy.git@traefik-v2-hack',
            'jupyterhub-duoauthenticator @ git+https://github.com/possiblyMikeB/jupyter-duoauthenticator.git#a6178272cc3153296a1fd5eab50bfd0a41658bff',
            'jupyterhub-idle-culler @ git+https://github.com/jupyterhub/jupyterhub-idle-culler.git#80c8c17e4b2aac11dab1c59079e7fc24e8c8ca48',
            'jupyterhub-announcement @ git+https://github.com/rcthomas/jupyterhub-announcement.git#1504bf2ff1f91a1524511c79f1bf44247aa226ca',
            'html-sanitizer',
            'duo_web'
        ],
        'runtime': [
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
            'calysto_bash>=0.2.2',
            
            # all, runtime
            'numpy>=1.19.5',
            'scipy>=1.5',
            'sympy>=1.9',
            'pandas>=1.2',
            'scikit-learn>=0.24',
            'scitools3>=1.0',
            'beautifulsoup4>=4',
            'lxml>=4.7'
        ]
    },
    include_package_data=True,
    zip_safe=False
)
