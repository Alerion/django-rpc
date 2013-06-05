.. _tutorial-part-3:

Part 3: Javascript API
======================


Method calling
--------------

You can call method without callback:

.. code-block:: javascript

    MainApi.hello(1, 2, 3);

With success callback:

.. code-block:: javascript

    MainApi.hello(1, 2, 3, function(){
        console.log('success', arguments);
    }

Or with success and failure callbacks:

.. code-block:: javascript

    MainApi.hello(1, 2, 3, function(){
        console.log('success', arguments);
    }, function(){
        console.log('error', arguments);
    })


Events
------

All responses are handled as events. You can subscribe to exceptions:

.. code-block:: javascript

    jQuery.Rpc.on('exception', function(event){
        alert('Error during RPC request: '+event.message);
    });

or to all events:

.. code-block:: javascript

    jQuery.Rpc.on('event', function(event){
        console.log(event);
    });


jquery.util.js
--------------

Contains different useful utilities used by jQuery.Rpc.
