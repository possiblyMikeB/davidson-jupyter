# 0.3.1 
- Move JupyterHub site classes into package `davidson.hub` and reference `davidson.hub` from JupyterHub drop-in files.
- Add default pack of kernel definitions (these assume the existence of site-specific conda environments)
- Add site JupyterHub drop-in configuration files (`config/hub.d`)
- Add preliminary rough-out of JupyterHub dynamic configuration provider (located in package `davidson.hub.ctl`)

# 0.2.1

- Add requirements setting up JupyterLab 3.0 with JupyterHub==1.4.2 and the following extensions
- Add dependency on local forks of `jupyterlab-system-monitor` & `jupyter-resource-usage` (aka nbresuse)
- Combine disporia of `jupyter-server-proxy` modules used in production under the single package `davidson_jupyter`, providing proxied Theia, RStudio, and XFCE Desktop configurations.
- Include site specific jupyterlab, classic notebook, and jupyter server configuration, which is installed with package  

# 0.1.1

- Initial release
