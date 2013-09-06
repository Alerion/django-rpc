.. _index:

Django RPC documentation
========================

Django RPC for jQuery. Allows execute some server-side class methods with Javascript in your browser.

Also you can submit forms with `jQuery Form Plugin <http://malsup.com/jquery/form/>`_.

It also supports a call batching. Django RPC batches together calls which are received within
a configurable time frame and sends them in a single request.

You can easy move you current views to RPC methods and use Django RPC instead of mess of AJAX requests.

Inspired by Ext.Direct from ExtJs.


Support
-------

You can ask a question or report a bug on `project Github repo <https://github.com/Alerion/Django-RPC/issues>`_.


Requirements
------------

Django RPC requires the following:

* Python (2.6.5+, 2.7)
* Django (1.4, 1.5, 1.6)


Contents
--------

.. toctree::
    :maxdepth: 2

    installation
    example
    tutorial/index
    api/index
