Robot Framework Apache Tomcat Manager
=====================================

Robot Framework library to manage Apache Tomcat server

|Build Status|

Short Description
-----------------

`Robot Framework`_ library for managing Apache Tomcat Server.

This library is Implemented on the basis of: - `Manager App HOW-TO`_ -
`tomcat-manager`_

Installation
------------

Install the library from PyPI using pip:

::

    pip install robotframework-apachetomcat

Settings for Apache Tomcat Server
---------------------------------

To use this library you need to add a user with the following roles to
``tomcat-users.xml`` file on Apache Tomcat server: - manager-gui -
manager-script - manager-jmx - manager-status.

::

    <tomcat-users>
        <user username="tomcat" password="tomcat" roles="manager-jmx,manager-status,manager-script,admin,manager-gui,admin-gui,manager-script,admin"/>
    </tomcat-users>

Documentation
-------------

See keyword documentation for ApacheTomcatManager library on `GitHub`_.

Example
-------

An example of using ApacheTomcatManager library in Robot Framework test
case:

.. code:: robotframework

    *** Settings ***
    Library    ApacheTomcatManager
    Library    Collections

    *** Test Cases ***
    Simple Test
        Connect To Tomcat    my_host_name    8080    tomcat    tomcat    alias=tmc
        ${info}=    Serverinfo
        Log Dictionary    ${info}
        Close All Tomcat Connections

License
-------

Apache License 2.0

.. _Robot Framework: http://www.robotframework.org
.. _Manager App HOW-TO: http://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html
.. _tomcat-manager: https://github.com/kotfu/tomcat-manager
.. _GitHub: https://github.com/peterservice-rnd/robotframework-apachetomcat/tree/master/docs

.. |Build Status| image:: https://travis-ci.org/peterservice-rnd/robotframework-apachetomcat.svg?branch=master
   :target: https://travis-ci.org/peterservice-rnd/robotframework-apachetomcat
