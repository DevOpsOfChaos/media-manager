from __future__ import annotations

NAV_HISTORY_SCHEMA_VERSION = "1.0"


def build_navigation_history(current_page_id: str = "dashboard", *, back_stack: list[str] | None = None, forward_stack: list[str] | None = None) -> dict[str, object]:
    back = list(back_stack or [])
    forward = list(forward_stack or [])
    current = str(current_page_id or "dashboard")
    return {
        "schema_version": NAV_HISTORY_SCHEMA_VERSION,
        "kind": "navigation_history",
        "current_page_id": current,
        "back_stack": back,
        "forward_stack": forward,
        "can_go_back": bool(back),
        "can_go_forward": bool(forward),
    }


def push_navigation(history: dict[str, object], page_id: str) -> dict[str, object]:
    target = str(page_id or "").strip() or "dashboard"
    current = str(history.get("current_page_id") or "dashboard")
    if target == current:
        return build_navigation_history(current, back_stack=list(history.get("back_stack", [])), forward_stack=list(history.get("forward_stack", [])))
    back = list(history.get("back_stack", []))
    back.append(current)
    return build_navigation_history(target, back_stack=back[-50:], forward_stack=[])


def go_back(history: dict[str, object]) -> dict[str, object]:
    back = list(history.get("back_stack", []))
    forward = list(history.get("forward_stack", []))
    current = str(history.get("current_page_id") or "dashboard")
    if not back:
        return build_navigation_history(current, back_stack=back, forward_stack=forward)
    previous = back.pop()
    forward.append(current)
    return build_navigation_history(previous, back_stack=back, forward_stack=forward)


def go_forward(history: dict[str, object]) -> dict[str, object]:
    back = list(history.get("back_stack", []))
    forward = list(history.get("forward_stack", []))
    current = str(history.get("current_page_id") or "dashboard")
    if not forward:
        return build_navigation_history(current, back_stack=back, forward_stack=forward)
    next_page = forward.pop()
    back.append(current)
    return build_navigation_history(next_page, back_stack=back, forward_stack=forward)


__all__ = ["NAV_HISTORY_SCHEMA_VERSION", "build_navigation_history", "push_navigation", "go_back", "go_forward"]
