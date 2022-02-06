
import os, sys, pwd, socket, shutil, asyncio
from traitlets import (
    Integer, Unicode, Float, Dict, default 
)

from batchspawner import SlurmSpawner
from async_generator import async_generator, yield_, yield_from_

class SiteSlurmSpawner(SlurmSpawner):
    req_gres = Unicode('',
        help='Generic consumable resources requested'
    ).tag(config=True)
    
    req_comment = Unicode('',
        help='Comment to include in slurm batch script'
    ).tag(config=True)

    req_profile = Unicode('',
        help='Job profile designation used for internal tracking'
    ).tag(config=True)

    req_conda_path = Unicode('/opt/conda',
        help="Path to conda installation"
    ).tag(config=True)

    req_conda_env = Unicode('common',
        help="Job script expects this conda environment"
    ).tag(config=True)

    req_workspace = Unicode(
        help="Specifies path to superficially isolate jupyter instance to"
    ).tag(config=True)
    
    @default('req_workspace')
    def _req_workspace_default(self):
        # XXX: this allows for terminals to open in 
        #   the notebook directory 
        path = self.notebook_dir
        self.notebook_dir = '.'
        return path

    req_username = Unicode()
    @default('req_username')
    def _req_username_default(self):
        return self.user.name + '@davidson.edu'

    req_homedir = Unicode()
    @default('req_homedir')
    def _req_homedir_default(self):
        return pwd.getpwnam(self.req_username).pw_dir
    
    def user_env(self, env):
        """Get user enivornment variables
        Overrides UserEnvMixin.user_env; adds '@davidson.edu' 
         ... to usernames before calling `getpwname`
        """
        fquser = self.req_username
        pws = pwd.getpwnam(fquser)
        
        env['USER'] = fquser
        if pws.pw_dir:
            env['HOME'] = pws.pw_dir
        if pws.pw_shell:
            env['SHELL'] = pws.pw_shell
        return env

    def state_tres(self):
        return self.req_gres

    ## SPAWNING: Progress
    @async_generator
    async def progress(self):
        """generate messages, etc... describing spawn progress"""
        while True:
            if self.state_ispending():
                await yield_({
                    "progress": 10,
                    "message": "Pending in queue...",
                })
            elif self.state_isrunning():
                await yield_({
                    "progress": 30,
                    "message": "Cluster job running... waiting to connect",
                })
                return
            else:
                await yield_({
                    "progress": 0,
                    "message": "Unknown status...",
                })
            await gen.sleep(1)
    
    ## PRE-SPAWN Hook
    async def pre_spawn_hook(self, spawner):
        # ensure home directory is created properly
        self.log.info("Pre-Spawn: Env. Bootstraping..")

        os.system(f'sudo -u {self.req_username} true')
        try:
            # attempt to create user workspace, if defined
            path = self.req_homedir
            if self.req_workspace:
                path = os.path.join(path, self.req_workspace)
                uid = pwd.getpwnam(self.req_username).pw_uid
                gid = pwd.getpwnam(self.req_username).pw_gid
                
                # create directory
                os.makedirs(path, 0o755, exist_ok=True)
                while len(path) > len(self.req_homedir):
                    shutil.chown(path, user=uid, group=gid)
                    path = os.path.dirname(path)
                    pass

        except FileExistsError:
            pass
        
        # ensure SLURM user account associations are in-order
        self.log.info("Pre-Spawn: Update SLURM User Associations")

        sacctmgr = f"{os.environ.get('SLURM_PATH','')}/bin/sacctmgr"
        cmd = (
            sacctmgr,  '-i',  'add', 'user', f'{self.req_username}', 
            f'account={self.req_account}',
            f'partition={self.req_partition}',
            f'cluster={self.req_cluster}'
        )
        
        proc = await asyncio.create_subprocess_exec(*cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE 
        )

        try:
            out, e = await proc.communicate()
        except:
            proc.kill()
            raise RuntimeError("sacctmgr failed: killed before return")
        else:
            e = e.decode().strip()
            out = out.decode().strip()
            retcode = proc.returncode
            if retcode != 0 and out.find("Nothing new added.") < 0:
                self.log.error("sacctmgr failed: returned exitcode %s" % retcode)
                self.log.error(e)
                raise RuntimeError(e)

        # ensure `self.notebook_dir` is appropriately set
        self.notebook_dir = '.'
        return 

    ## mutal-TLS: Create Certs
    async def create_certs(self):
        """Create and set ownership for the certs to be used for internal ssl

        This method creates certs for use with the singleuser notebook. It
        enables SSL and ensures that the notebook can perform bi-directional
        SSL auth with the hub (verification based on CA).
        """
        from certipy import Certipy

        default_names = ["DNS:localhost", "IP:127.0.0.1"]
        alt_names = []
        alt_names.extend(self.ssl_alt_names)

        if self.ssl_alt_names_include_local:
            alt_names = default_names + alt_names

        self.log.info("Creating certs for %s: %s",
                      self._log_name, ';'.join(alt_names))
        
        common_name = self.user.name or 'service'
        certipy = Certipy(store_dir=self.internal_certs_location)
        notebook_component = 'notebooks-ca'
        notebook_key_pair = \
            certipy.create_signed_pair(
                'user-' + common_name,
                notebook_component,
                alt_names=alt_names,
                overwrite=True,
            )
        
        paths = {
            "keyfile": notebook_key_pair['files']['key'],
            "certfile": notebook_key_pair['files']['cert'],
            "cafile": self.internal_trust_bundles[notebook_component],
        }
        return paths
    
    ## mutal-TLS: Move/Deploy Certs
    async def move_certs(self, paths):
        """Takes cert paths, moves and sets ownership for them
        Arguments:
            paths (dict): a list of paths for key, cert, and CA
        Returns:
            dict: a list (potentially altered) of paths for key, cert,
            and CA
        Stage certificates into a private home directory
        and make them readable by the user.
        """
        import pwd, shutil
        from hashlib import md5

        key = paths['keyfile']
        cert = paths['certfile']
        ca = paths['cafile']

        hash_sn = md5(
            (self.name).encode('utf-8')
        ).hexdigest()

        user = pwd.getpwnam(self.req_username)
        uid = user.pw_uid
        gid = user.pw_gid
        home = user.pw_dir
        self.log.debug(f'uid = {uid}')
        # Create dir for user's certs wherever we're starting
        cfg_dir = f'{home}/.config'
        base_dir = f'{cfg_dir}/hub'
        hub_dir = f'{base_dir}/{self.req_profile}'
        sub_dir = f'{hub_dir}/{hash_sn}'
        out_dir = f'{sub_dir}/pki'
        shutil.rmtree(out_dir, ignore_errors=True)
        os.makedirs(out_dir, 0o700, exist_ok=True)
        
        # Move certs to users dir
        
        key = os.path.join(out_dir, 'key.pem')
        cert = os.path.join(out_dir, 'cert.pem')
        ca = os.path.join(out_dir, 'ca.pem')
        
        shutil.move(paths['keyfile'], key)
        shutil.move(paths['certfile'], cert)
        shutil.copy(paths['cafile'], ca)

        # Set cert ownership to user
        for f in [cfg_dir, base_dir, hub_dir, sub_dir, out_dir, key, cert, ca]:
            shutil.chown(f, user=uid, group=gid)

        return {"keyfile": key, "certfile": cert, "cafile": ca}

    ## SPAWNER: Start
    async def start(self):
        self.log.debug(f'START HOOK: user_options: {self.user_options}')

        ## enforce pre-configured values of critical variables, like
        #
        #   `profile`, `conda_path`, `conda_env`,`account`, `cluster`, `partition`,
        #    `qos`, `username`, `workspace`, `srun`, `options`...
        #
        # by only allowing `self.user_options` to override one of the following
        #
        #   `nprocs`, `memory`, `runtime`, or `gres` 
        #

        options = dict()
        for safe_key in [ 'nproc', 'memory', 'runtime', 'gres' ]:
            if safe_key in self.user_options:
                options[safe_key] = self.user_options[safe_key]

        # replace user_options with clean version
        self.user_options = options
        
        # and persist cleaned version in database 
        self.orm_spawner.user_options = options
        self.db.commit()

        # procced with spawn
        return await super().start()
    pass


# ######################################
# IMPORTANT!!
#  The environment variable SLURM_PATH, must be set in order
#  for spawning and monitoring of server-instances to function

slurm_prefix = os.environ['SLURM_PATH'] # (this will fail if not set)

# ##########################

c.SiteSlurmSpawner.batchspawner_singleuser_cmd = '' # (using custom shim)
c.SiteSlurmSpawner.exec_prefix='' # (was 'sudo -E -u {username} ')

# avoid additional call to `sudo`
c.SiteSlurmSpawner.\
    batch_query_cmd = f"{slurm_prefix}/bin/squeue" + " -u {username} -h -j {job_id} -o '%T %B'"

# TOOD: investigate the need for `sudo` on the 
#  sbatch & scancel calls
c.SiteSlurmSpawner.\
    batch_cancel_cmd = "sudo -E -u {username} " + f"{slurm_prefix}/bin/scancel" + " {job_id}"

c.SiteSlurmSpawner.\
    batch_submit_cmd = "sudo -E -u {username} " + f"{slurm_prefix}/bin/sbatch" + " --parsable"

## import & store job-script template 
job_template = os.environ.get('SPAWNER_SLURM_SCRIPT')
if os.path.exists(job_template):
    c.SiteSlurmSpawner.batch_script = open(job_template, 'r').read()
else:
    c.SiteSlurmSpawner = job_template

## used to communicate the hub-id to the running job.
c.SiteSlurmSpawner.req_profile = hub_id

## check for job parameters
arg_names = [
    'partition', 'account', 'cluster', 'qos', 'reservation',
    'nprocs', 'ntasks', 'memory', 'gres', 
    'runtime', 'workspace'
]

for name in arg_names:
    try: 
        # check to see if we've been passed something in
        #  the environment.
        val = os.environ[f'SPAWNER_SLURM_JOB_{name.upper()}']
        if val and hasattr(SiteSlurmSpawner, f'req_{name}'):
            # if so and we have a place to hold it, 
            #   then, store the value.
            setattr(c.SiteSlurmSpawner, f'req_{name}', val)
            pass
    except KeyError:
        continue


## job-step specific parameters
c.SiteSlurmSpawner.req_srun = 'srun -n1'

for name in ['epilog', 'prolog' ]:
    path = os.environ.get(f'SPAWNER_SLURM_TASK_{name.upper()}')
    if path:
        c.SiteSlurmSpawner.req_srun += f' --task-{name} {path}'
        pass

c.SiteSlurmSpawner.req_options = '--ntasks=1 ' + os.environ.get('SPAWNER_SLURM_JOB_EXTRA', '')

## conda environment parameters
c.SiteSlurmSpawner.req_conda_env = os.environ.get('SPAWNER_SLURM_CONDA_ENV')
c.SiteSlurmSpawner.req_conda_path = os.environ.get('SPAWNER_SLURM_CONDA_PATH')

# set spawner class
c.JupyterHub.spawner_class = SiteSlurmSpawner
