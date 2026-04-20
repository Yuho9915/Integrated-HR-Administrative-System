from datetime import datetime

from app.performance.mappers import (
    actor_profile,
    employee_lookup,
    grade_from_score,
    hydrate_performance_record,
    normalize_text,
    to_number,
)
from app.performance.permissions import (
    ai_can_auto_score,
    ai_can_diagnose,
    ai_can_generate_report,
    ai_can_review_appeal,
    ensure_record_scope,
    forbidden,
    scope_rows,
)
from app.performance.queries import build_report_snapshot, filter_rows, performance_history


def log_ai_action(repository, action: str, user: dict, payload: dict, result: dict) -> None:
    repository.upsert('ai_logs', {
        'module': 'performance',
        'action': action,
        'operator': user.get('username', ''),
        'role': user.get('role', ''),
        'payload': payload,
        'result': result,
        'loggedAt': datetime.utcnow().isoformat(),
    })


async def check_performance_payload(payload, repository, ai_service):
    normalized = []
    employee_map = employee_lookup(repository)
    for item in payload.records:
        row = hydrate_performance_record(item, employee_map)
        score = to_number(row.get('totalScore') or row.get('score'))
        grade = row.get('grade') or grade_from_score(score)
        normalized.append({**row, 'grade': grade, 'score': score})
        if row.get('employeeNo'):
            repository.upsert('performance', {**row, 'grade': grade, 'score': score, 'period': payload.cycle})
    return await ai_service.performance_check(normalized)


async def auto_score(payload: dict, user: dict, repository, ai_service):
    ai_can_auto_score(user)
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    target_row = None
    if payload.get('employeeNo'):
        target_row = hydrate_performance_record(payload, employee_map)
        ensure_record_scope(target_row, user, actor)
    result = await ai_service.auto_score_performance(payload)
    log_ai_action(repository, 'auto-score', user, payload, result)
    return result


async def generate_comment(payload: dict, user: dict, repository, ai_service):
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    comment_type = normalize_text(payload.get('commentType')) or 'self'
    target_employee_no = normalize_text(payload.get('employeeNo'))
    target_row = hydrate_performance_record(payload, employee_map) if target_employee_no else None

    if user.get('role') == 'employee':
        if comment_type != 'self' or target_employee_no != actor.get('employeeNo'):
            raise forbidden('员工仅可生成本人自评')
    elif user.get('role') == 'manager':
        if comment_type != 'manager':
            raise forbidden('部门经理仅可生成本部门下属上级评语')
        ensure_record_scope(target_row, user, actor, '部门经理仅可生成本部门下属上级评语')
    else:
        raise forbidden('当前角色无权限生成AI绩效评语')

    result = await ai_service.generate_performance_comment(payload)
    log_ai_action(repository, 'generate-comment', user, payload, result)
    return result


async def diagnose(payload: dict, user: dict, repository, ai_service):
    ai_can_diagnose(user)
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    current = None
    if payload.get('recordId'):
        current_record = repository.get('performance', payload['recordId'])
        if current_record:
            current = hydrate_performance_record(current_record, employee_map)
    ensure_record_scope(current, user, actor)
    current_payload = payload.get('current') or {}
    employee_no = normalize_text(payload.get('employeeNo') or current_payload.get('employeeNo') or actor.get('employeeNo'))
    history = performance_history(repository, employee_no, current_payload.get('id')) if employee_no else []
    if user.get('role') == 'manager':
        history = scope_rows(history, user, actor)
    result = await ai_service.diagnose_performance({**payload, 'current': current_payload, 'history': history})
    repository.upsert('performance_ai_reports', {'employeeNo': employee_no, 'recordId': current_payload.get('id', ''), 'type': 'diagnose', 'report': result})
    log_ai_action(repository, 'diagnose', user, payload, result)
    return result


async def generate_report(payload: dict, user: dict, repository, ai_service):
    ai_can_generate_report(user)
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    filters = payload or {}
    rows = [hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    rows = filter_rows(scope_rows(rows, user, actor), filters.get('keyword', ''), filters.get('department', ''), filters.get('position', ''), filters.get('cycleType', ''), filters.get('assessmentYear'), filters.get('assessmentMonth'), filters.get('status', ''))
    snapshot = build_report_snapshot(rows)
    result = await ai_service.generate_performance_report({**filters, 'records': rows, 'snapshot': snapshot})
    repository.upsert('performance_ai_reports', {'type': 'summary-report', 'filters': filters, 'report': result, 'snapshot': snapshot, 'scopeRole': user.get('role')})
    log_ai_action(repository, 'generate-report', user, filters, result)
    return result


async def review_appeal(payload: dict, user: dict, repository, ai_service):
    ai_can_review_appeal(user)
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    current = None
    if payload.get('recordId'):
        record = repository.get('performance', payload['recordId'])
        if record:
            current = hydrate_performance_record(record, employee_map)
    ensure_record_scope(current, user, actor)
    current_payload = current or {}
    employee_no = normalize_text(payload.get('employeeNo') or current_payload.get('employeeNo'))
    history = performance_history(repository, employee_no, current_payload.get('id')) if employee_no else []
    if user.get('role') == 'manager':
        history = scope_rows(history, user, actor)
    result = await ai_service.review_performance_appeal({**payload, 'current': current_payload, 'history': history})
    repository.upsert('performance_ai_reports', {'employeeNo': employee_no, 'recordId': current_payload.get('id', ''), 'type': 'appeal-review', 'report': result})
    log_ai_action(repository, 'appeal-review', user, payload, result)
    return result
