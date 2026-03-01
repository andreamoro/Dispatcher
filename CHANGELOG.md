# Changelog

All notable changes to **multi-args-dispatcher** are documented in this file.

## [0.3.4] - 2026-03-01

### Fixed

- Resolve string annotations using `typing.get_type_hints()` for proper
  `from __future__ import annotations` support.

## [0.3.3] - 2024-01-25

### Added

- List type detection in signature registration.
- `operator`-based comparator map (`MATCH_TYPE_COMPARATORS`) replacing
  version-guarded match/case and if/elif blocks.

### Changed

- Improved generic and positional argument handling in `__get_signature`.
- Updated test files.

## [0.3.2] - 2023-12-03

### Fixed

- `__get_signature` bug when recognising positional arguments.
- Annotation handling: introduced `annotation_name` variable to avoid
  direct `p.annotation.__name__` access, which fails with string annotations.

### Changed

- General code cleanup.
- Renamed project package to `multi-args-dispatcher`.

## [0.3.1rc1] - 2023-02-26

### Added

- Improved control for generics and method matching via `sigExactMatch`.
- Generic filtering logic in `__match_signature` (`'Generics'` / `'Only'` modes).

### Changed

- Updated documentation and release version.
- Revised tests.

## [0.3.0rc1] - 2023-02-26

### Added

- Initial release of the multi-arguments dispatcher.
- Decorator-based API: `@dispatcher` with `@func.register` for variant
  registration.
- Signature introspection via `inspect.signature`.
- Multi-case dispatch with exact, generic, and default-based fallback matching.
- Enum-aware parameter handling.
- Class method support (automatic `self` skipping).
- Packaging via `pyproject.toml` and setuptools.

### Compatibility

- Replaced `match`/`case` (Python 3.10+) with `if`/`elif` chains for
  Python < 3.10 support (applied in 2023-03-22).
