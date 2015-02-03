from __future__ import unicode_literals

from djangorpc.responses import Error, Msg, RpcResponse, RpcHttpResponse
from djangorpc.router import RpcRouter

__all__ = ('Error', 'Msg', 'RpcResponse', 'RpcRouter', 'RpcHttpResponse')

__version__ = '0.4'
VERSION = __version__

__description__ = 'Django RPC for jQuery'
