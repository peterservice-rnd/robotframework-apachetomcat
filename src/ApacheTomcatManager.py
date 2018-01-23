# -*- coding: utf-8 -*-

from robot.api import logger
from robot.utils import ConnectionCache
import requests


class RequestConnection(object):
    """This class contains settings to connect to Apache Tomcat server via HTTP."""
    def __init__(self, host, port, username, password, timeout):
        """Initialisation.

        *Args:*\n
        _host_ - server host name;\n
        _port_ - port number;\n
        _username_ - user name;\n
        _password_ - user password;\n
        _timeout_ - connection timeout;\n

        """
        self.host = host
        self.port = port
        self.url = 'http://{host}:{port}/manager/text'.format(host=host, port=port)
        self.auth = (username, password)
        self.timeout = timeout

    def close(self):
        """Close connection."""
        pass


class ApacheTomcatManager(object):
    """
    Library to manage Apache Tomcat server.


    Implemented on the basis of:
    - [ http://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html | Manager App HOW-TO ]
    - [ https://github.com/kotfu/tomcat-manager | tomcat-manager ]

    == Dependencies ==
    | robot framework | http://robotframework.org |
    | requests | https://pypi.python.org/pypi/requests |

    == Example ==
    | *Settings* | *Value* |
    | Library    |       ApacheTomcatManager |
    | Library     |      Collections |

    | *Test Cases* | *Action* | *Argument* | *Argument* | *Argument* | *Argument* | *Argument* |
    | Simple |
    |    | Connect To Tomcat | my_host_name | 8080 | tomcat | tomcat | alias=tmc |
    |    | ${info}= | Serverinfo |
    |    | Log Dictionary | ${info} |
    |    | Close All Tomcat Connections |

    == Additional Information ==
    To use this library you need to set up setting for Apache Tomcat user. Add a user with roles:
    - manager-gui,
    - manager-script,
    - manager-jmx,
    - manager-status,
    to file tomcat-users.xml on Apache Tomcat server.

    Example:
    | <tomcat-users>
    | <user username="tomcat" password="tomcat" roles="manager-jmx,manager-status,manager-script,admin,manager-gui,admin-gui,manager-script,admin"/>
    | </tomcat-users>
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        """ Initialization. """
        self._connection = None
        self.headers = {}
        self._cache = ConnectionCache()

    def connect_to_tomcat(
            self, host, port, username='tomcat', password='tomcat', timeout=15, alias=None):
        """Connect to Apache Tomcat server.

        *Args:*\n
        _host_ - server host name;\n
        _port_ - port name;\n
        _username_ - user name;\n
        _password_ - user password;\n
        _timeout_ - connection timeout;\n
        _alias_ - connection alias;\n

        *Returns:*\n
        The current connection index.

        *Example:*\n
        | Connect To Tomcat | my_host_name | 8080 | tomcat | tomcat | alias=tmc1 |
        """
        port = int(port)
        timeout = int(timeout)
        self.headers["Content-Type"] = "text/plain"

        logger.debug('Connecting using : host=%s, port=%d, username=%s, password=%s, timeout=%d, alias=%s ' % (
            host, port, username, password, timeout, alias))

        self._connection = RequestConnection(host, port, username, password, timeout)
        return self._cache.register(self._connection, alias)

    def switch_tomcat_connection(self, index_or_alias):
        """Switch between active Apache Tomcat connections, using their index or alias.

        Alias is set in keyword [#Connect To Tomcat|Connect To Tomcat], which also returns the index of connection.

        *Args:*\n
        _index_or_alias_ - connection index or alias;

        *Returns:*\n
        The index of previous connection.

        *Example:*\n
        | Connect To Tomcat | my_host_name_1 | 8080 | tomcat | tomcat | alias=rmq1 |
        | Connect To Tomcat | my_host_name_2 | 8080 | tomcat | tomcat | alias=rmq2 |
        | Switch Tomcat Connection | rmq1 |
        | ${info1}= | Serverinfo |
        | Switch Tomcat Connection | rmq2 |
        | ${info2}= | Serverinfo |
        | Close All Tomcat Connections |
        """
        old_index = self._cache.current_index
        self._connection = self._cache.switch(index_or_alias)
        return old_index

    def disconnect_from_tomcat(self):
        """Close the current connection with Apache Tomcat.

        *Example:*\n
        | Connect To Tomcat | my_host_name | 8080 | tomcat | tomcat | alias=rmq1 |
        | Disconnect From Tomcat |
        """
        logger.debug(
            'Close connection with : host=%s, port=%d  ' %
            (self._connection.host, self._connection.port))
        self._connection.close()

    def close_all_tomcat_connections(self):
        """Close all connections with Apache Tomcat.

        This keyword is used to close all connections only in case if there are several open connections.
        Do not use keywords [#Disconnect From Tomcat|Disconnect From Tomcat] and [#Close All Tomcat Connections|Close All Tomcat Connections]
        together.

        After this keyword is executed, the index, returned by [#Connect To Tomcat|Connect To Tomcat], starts at 1.

        *Example:*\n
        | Connect To Tomcat | my_host_name_1 | 8080 | tomcat | tomcat | alias=rmq1 |
        | Close All Tomcat Connections |
        """
        self._connection = self._cache.close_all()

    def list(self):
        """Get list of installed applications.

        *Returns:*\n
        List of installed web applications of following format:
        | application path | running status | number of sessions | application name |

        *Raises:*\n
        raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
        | ${list}=  |  List |
        | Log List  |  ${list} |
        =>
        | /dcs-workbench1 | running | 0 | dcs-workbench1 |
        | /manager | running | 1 | manager |
        | / | running | 0 | ROOT |
        | /docs | running | 0 | docs |
        | /dcs-workbench | running | 0 | dcs-workbench |
        | /dcs | running | 0 | dcs |
        | /host-manager | running | 0 | host-manager |
        """
        apps = []
        url = self._connection.url + '/list'
        logger.debug('Prepared request with method GET to ' + url)
        response = requests.get(url, auth=self._connection.auth,
                                headers=self.headers,
                                timeout=self._connection.timeout)
        response.raise_for_status()
        resp_list = response.text.split('\n')
        for lines in resp_list[1:-1]:
            apps.append(lines.split(':'))
        return apps

    def application_status(self, path):
        """Get the web application running status.

        *Args:*\n
        _path_ - path to the web application;

        *Returns:*\n
        The web application running status: running, stopping.

        *Raises:*\n
        raise Exception в том случае, если web-приложение не загружено на Apache Tomcat.

        *Example:*\n
        | ${status}=  |  Application Status  |  /dcs-workbench |
        =>
        running
        """
        app_list = self.list()
        for app_name, status, _, _ in app_list:
            if app_name == path:
                return status
        raise Exception(
            'Application with path "' +
            path +
            '" not found on Apache Tomcat')

    def serverinfo(self):
        """Get information about server.

        *Returns:*\n
        Information of Apache Tomcat server in dictionary format.

        *Raises:*\n
        raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
        | ${info}=  |  Serverinfo  |
        | Log Dictionary  |  ${info} |
        =>
        | JVM Vendor: Oracle Corporation
        | JVM Version: 1.7.0_40-b43
        | OS Architecture: amd64
        | OS Name: Linux
        | OS Version: 2.6.32-279.el6.x86_64
        | Tomcat Version: Apache Tomcat/7.0.22
        """
        serverinfo = {}
        url = self._connection.url + '/serverinfo'
        logger.debug('Prepared request with method GET to ' + url)
        response = requests.get(url, auth=self._connection.auth,
                                headers=self.headers,
                                timeout=self._connection.timeout)
        response.raise_for_status()
        resp_list = response.text.split('\n')

        for lines in resp_list[1:-1]:
            key, value = lines.rstrip().split(":", 1)
            serverinfo[key] = value.lstrip()
        return serverinfo

    def application_stop(self, path):
        """Stop the running web application.

        *Args:*\n
        _path_ - path to web application;

        *Raises:*\n
        raise Exception in case the web application could not be stopped.

        *Example:*\n
        |  Application Stop  |  /dcs-workbench |
        """
        url = self._connection.url + '/stop?path=%s' % requests.utils.quote(path)
        logger.debug('Prepared request with method GET to ' + url)
        response = requests.get(url, auth=self._connection.auth,
                                headers=self.headers,
                                timeout=self._connection.timeout)
        logger.debug('Response: %s' % response.text)
        if response.text != 'OK - Stopped application at context path ' + \
                path + '\n':
            raise Exception('Application  is not stopped:\n' + response.text)

    def application_start(self, path):
        """Start web application.

        *Args:*\n
        _path_ - path to web application;

        *Raises:*\n
        raise Exception in case the web application could not be stopped.

        *Example:*\n
        |  Application Start  |  /dcs-workbench |
        """
        url = self._connection.url + '/start?path=%s' % requests.utils.quote(path)
        logger.debug('Prepared request with method GET to ' + url)
        response = requests.get(url, auth=self._connection.auth,
                                headers=self.headers,
                                timeout=self._connection.timeout)
        logger.debug('Response: %s' % response.text)
        if response.text != 'OK - Started application at context path ' + \
                path + '\n':
            raise Exception('Application  is not started:\n' + response.text)

    def application_reload(self, path):
        """Reload web application.

        *Args:*\n
        _path_ - path to web application;

        *Raises:*\n
        raise Exception in case the web application could not be stopped.

        *Example:*\n
        |  Application Reload  |  /dcs-workbench |
        """
        url = self._connection.url + '/reload?path=%s' % requests.utils.quote(path)
        logger.debug('Prepared request with method GET to ' + url)
        response = requests.get(url, auth=self._connection.auth,
                                headers=self.headers,
                                timeout=self._connection.timeout)
        logger.debug('Response: %s' % response.text)
        if response.text != 'OK - Reloaded application at context path ' + \
                path + '\n':
            raise Exception('Application  is not started:\n' + response.text)
