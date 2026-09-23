"""A learner's walk through the whole application, with sensors on.

Opt in with ``-m walk``. Nothing in here touches the real learner store: the
shared ``isolated_home`` fixture from ``tests/conftest.py`` points
``OPERATORS_CONSOLE_HOME`` at a throwaway directory for every test.
"""
