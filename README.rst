=========================
Shiva, Deployer of Worlds
=========================

As we deploy our Python web apps more frequently, the process of deploying must
become more robust. This is especially important when deploys are unsupervised.
However, robustness is neither short nor trivial to get right; we butt up
against the limitations of simple, linear shell scripts developed ad hoc for
each project. Shiva The Deployer is a factoring up of the common parts of
deployment scripts so projects can concentrate on their unique needs rather
than continnually reinventing (or skimping on) infrastructure.

Shiva provides a light inversion-of-control framework for deployment of Python
web projects. It implements the standard but tricky-to-get-thoroughly-correct
top-level logic of deployment so all you have to do is, essentially, fill out a
form, by writing a ``Deployment`` subclass. In addition, it ships with many
deployment building blocks to save you the hassle of continually rewriting them.

Features include...

* Automatic deploy-time re-homing of the deploy script into its own virtualenv
  (complete with dependencies, if you need them), while keeping the project's
  own dependencies separate
* Time-travel bootstrapping: each version of your project is deployed with the
  version of the deploy script from it, not one from a previous version.
* Integration with Jenkins, to encourage more hands-free continuous deployment
* A simple, readable way to run shell commands, so you get close to the
  simplicity of shell scripts but with Python's better flow control
* Locking (to prevent concurrent deploys, for example)

We'll add lots more, as we observe patterns.


Status
======

We're just getting started. DXR deploys continuously with the progenitor of
Shiva, and we're working on implementations for a few more apps as we speak.
Help is welcome; we've got tickets!


Version History
===============

1.0
  * No such release yet!
