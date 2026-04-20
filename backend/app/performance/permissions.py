from fastapi import HTTPException


def forbidden(detail: str = '当前角色无访问权限') -> HTTPException:
    return HTTPException(status_code=403, detail=detail)


def scope_rows(rows: list[dict], user: dict, actor: dict) -> list[dict]:
    if user['role'] == 'employee':
        return [row for row in rows if row.get('employeeNo') == actor.get('employeeNo')]
    if user['role'] == 'manager':
        return [row for row in rows if row.get('department') == actor.get('department')]
    return rows


def ensure_record_scope(row: dict | None, user: dict, actor: dict, detail: str = '当前角色无访问权限') -> None:
    if row and not scope_rows([row], user, actor):
        raise forbidden(detail)


def ensure_roles(user: dict, roles: tuple[str, ...], detail: str) -> None:
    if user.get('role') not in roles:
        raise forbidden(detail)


def ai_can_auto_score(user: dict) -> None:
    ensure_roles(user, ('manager', 'hr'), '仅部门经理与HR可使用AI智能评分')


def ai_can_diagnose(user: dict) -> None:
    ensure_roles(user, ('manager', 'hr'), '当前角色无权限使用AI绩效异常诊断')


def ai_can_generate_report(user: dict) -> None:
    ensure_roles(user, ('manager', 'hr'), '当前角色无权限生成AI绩效汇总报表')


def ai_can_review_appeal(user: dict) -> None:
    ensure_roles(user, ('manager', 'hr'), '当前角色无权限使用AI申诉审核')
