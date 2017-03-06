XMLRPC Server Usage
*******************

Once the service is up and running the XMLRPC server does the following operations:

* continuosly listens to requests coming from XMLRPC client
* polls the DB schema and acts the scheduled event agains selected GPIO pins

RPC functions available for RPC client
======================================

.. py:currentmodule:: servergpio
.. autoclass:: ServerFuncts
   :members:
 
