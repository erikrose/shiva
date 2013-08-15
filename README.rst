==================
Shiva The Deployer
==================

As we deploy our Python web apps more frequently, the process of deploying must
become more robust. This is especially important when deploys are unsupervised.
However, robustness is neither short nor trivial to get right; we butt up
against the limitations of simple, linear shell scripts developed ad hoc for
each project. Shiva The Deployer is a factoring up of the common parts of
deployment scripts so projects can concentrate on their unique needs rather
than continnually reinventing (or skimping on) infrastructure.

Shiva provides a light inversion-of-control framework for deployment of Python
web projects. It implements the fairly standard top-level logic of deployment
so all you have to do is, essentially, fill out a form--by writing a
``Deployment`` subclass.

To relieve you of rewriting them, Shiva also provides several useful
primitives:

* Locking (to prevent concurrent deploys, for example)
* A simple, readable way to run shell commands
* A way to bootstrap the deploy script using a virtualenv, even if it has
  dependencies, while keeping the deploy script's dependencies separate from
  the project's own
* More to come, as we observe patterns


Status
======

We're just getting started. DXR deploys continuously with the progenitor of
Shiva, and we're working on implementations for a few more apps as we speak.
Help is welcome; we've got tickets!


Version History
===============

1.0
  * No such release yet!
