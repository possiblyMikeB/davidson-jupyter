"""
Customized html-rendering handlers.
    originally taken from jupyterhub.handlers.pages
"""

import asyncio
import codecs
import copy
import time
import os
from collections import defaultdict
from datetime import datetime
from http.client import responses

from jinja2 import TemplateNotFound
from tornado import gen
from tornado import web
from tornado.httputil import url_concat

from jupyterhub import __version__
from jupyterhub import orm
from jupyterhub.metrics import SERVER_POLL_DURATION_SECONDS
from jupyterhub.metrics import ServerPollStatus
from jupyterhub.utils import admin_only
from jupyterhub.utils import maybe_future
from jupyterhub.utils import url_path_join
from jupyterhub.handlers.base import BaseHandler

class SiteHomeHandler(BaseHandler):
    """
        Render the user's home page.
            with table displaying currently active jobs
    """

    @web.authenticated
    async def get(self):
        user = self.current_user
        if user.running:
            # trigger poll_and_notify event in case of a server that died
            await user.spawner.poll_and_notify()

        # send the user to /spawn if they have no active servers,
        # to establish that this is an explicit spawn request rather
        # than an implicit one, which can be caused by any link to `/user/:name(/:server_name)`
        if user.active:
            url = url_path_join(self.base_url, 'user', user.escaped_name)
        else:
            url = url_path_join(self.hub.base_url, 'spawn', user.escaped_name)


        # XXX: get job list

        self.log.debug("Getting User Job Queue")
        proc = await asyncio.create_subprocess_shell(
                os.environ.get('SLURM_PATH','') + f'/bin/squeue -o "%i,%T,%a,%M,%D,%j" -u {user.name}@davidson.edu',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE )
        try:
            out, e = await proc.communicate()
        except:
            proc.kill()
            raise RuntimeError("squeue call home-page")
        else:
            e = e.decode().strip()
            retcode = proc.returncode
            if retcode != 0:
                self.log.error("subprocess returned exitcode %s" % retcode)
                self.log.error(e)
                raise RuntimeError(e)
        
        user_jobs = [ line.split(',') for line in out.decode().splitlines() ]

        ## render template
        auth_state = await user.get_auth_state()
        html = await self.render_template(
            'home.html',
            user_jobs=user_jobs,
            auth_state=auth_state,
            user=user,
            url=url,
            allow_named_servers=self.allow_named_servers,
            named_server_limit_per_user=self.named_server_limit_per_user,
            url_path_join=url_path_join,
            # can't use user.spawners because the stop method of User pops named servers from user.spawners when they're stopped
            spawners=user.orm_user._orm_spawners,
            default_server=user.spawner,
        )
        self.finish(html)


class SiteAdminHandler(BaseHandler):
    """
        Render the admin page.
            adding in additional user information
    """

    @web.authenticated
    @admin_only
    async def get(self):
        available = {'name', 'admin', 'running', 'last_activity'}
        default_sort = ['admin', 'name']
        mapping = {'running': orm.Spawner.server_id}
        for name in available:
            if name not in mapping:
                mapping[name] = getattr(orm.User, name)

        default_order = {
            'name': 'asc',
            'last_activity': 'desc',
            'admin': 'desc',
            'running': 'desc',
        }

        sorts = self.get_arguments('sort') or default_sort
        orders = self.get_arguments('order')

        for bad in set(sorts).difference(available):
            self.log.warning("ignoring invalid sort: %r", bad)
            sorts.remove(bad)
        for bad in set(orders).difference({'asc', 'desc'}):
            self.log.warning("ignoring invalid order: %r", bad)
            orders.remove(bad)

        # add default sort as secondary
        for s in default_sort:
            if s not in sorts:
                sorts.append(s)
        if len(orders) < len(sorts):
            for col in sorts[len(orders) :]:
                orders.append(default_order[col])
        else:
            orders = orders[: len(sorts)]

        # this could be one incomprehensible nested list comprehension
        # get User columns
        cols = [mapping[c] for c in sorts]
        # get User.col.desc() order objects
        ordered = [getattr(c, o)() for c, o in zip(cols, orders)]

        users = self.db.query(orm.User).outerjoin(orm.Spawner).order_by(*ordered)
        users = [self._user_from_orm(u) for u in users]

        # XXX: need a better way todo this
        for u in users:
            setattr(u, 'attr_cache', await u.get_auth_state())
            
        from itertools import chain

        running = []
        for u in users:
            running.extend(s for s in u.spawners.values() if s.active)

        auth_state = await self.current_user.get_auth_state()
        html = await self.render_template(
            'admin.html',
            current_user=self.current_user,
            auth_state=auth_state,
            admin_access=self.settings.get('admin_access', False),
            users=users,
            running=running,
            sort={s: o for s, o in zip(sorts, orders)},
            allow_named_servers=self.allow_named_servers,
            named_server_limit_per_user=self.named_server_limit_per_user,
            server_version='{} {}'.format(__version__, self.version_hash),
        )
        self.finish(html)

# print(h.default_handlers)
# add in custom handlers for home and admin
#c.JupyterHub.extra_handlers += [
#    (r'/home', SiteHomeHandler),
#    (r'/admin', SiteAdminHandler)
#]
