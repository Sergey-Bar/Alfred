"""Top-level conftest that re-exports shared fixtures.

Keep this file minimal so tests can import a canonical fixture set from
`tests.fixtures.shared_fixtures`. Adapter conftests may still override
fixtures where necessary.
"""

from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
