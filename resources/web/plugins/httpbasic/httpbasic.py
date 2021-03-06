import os

from qgis.server import *
from qgis.core import QgsMessageLog
import base64


class HTTPBasicFilter(QgsServerFilter):

    def _checkAuth(self):
        # NOAUTH for wget / GET retrieving
        if 'NOAUTH' in self.serverInterface().requestHandler().parameterMap():
            return True
        auth = self.serverInterface().getEnv('HTTP_AUTHORIZATION')
        if not auth:
            auth = self.serverInterface().requestHandler().requestHeader('HTTP_AUTHORIZATION')
        if auth:
            username, password = base64.b64decode(auth[6:]).split(b':')
            if (username.decode('utf-8') == os.environ.get('QGIS_SERVER_USERNAME', 'username') and
                    password.decode('utf-8') == os.environ.get('QGIS_SERVER_PASSWORD', 'password')):
                return True
        return False

    def requestReady(self):
        handler = self.serverInterface().requestHandler()
        auth = self.serverInterface().getEnv('HTTP_AUTHORIZATION')
        
        if self._checkAuth():
            return

        handler.setParameter('SERVICE', 'ACCESS_DENIED')

    def responseComplete(self):
        handler = self.serverInterface().requestHandler()
        auth = self.serverInterface().getEnv('HTTP_AUTHORIZATION')
        if self._checkAuth():
            return
        # No auth ...
        handler.clear()
        handler.setResponseHeader('Status', '401 Authorization required')
        handler.setResponseHeader('WWW-Authenticate', 'Basic realm="QGIS Server"')
        handler.appendBody(b'<h1>Authorization required</h1>')



class HTTPBasic:

    def __init__(self, serverIface):
        # Save reference to the QGIS server interface
        serverIface.registerFilter( HTTPBasicFilter(serverIface), 10 )
    
