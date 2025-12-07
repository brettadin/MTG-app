def resolve_stack_and_check_sbas(engine):
    """Resolve the engine's stack until it's empty, and check SBAs after each resolution.

    This is intended for tests that need deterministic stack resolution order without modifying
    production code or adding test-only flags in the engine.
    """
    # The stack manager is expected to support `is_empty()` and `resolve_top()`.
    # Loop until the stack is empty, resolving each item and checking SBAs.
    while not engine.stack_manager.is_empty():
        engine.stack_manager.resolve_top()
        # Ensure SBAs are checked after each resolution
        try:
            engine.check_state_based_actions()
        except Exception:
            # We can optionally log or re-raise; tests will fail if SBAs misbehave
            raise
