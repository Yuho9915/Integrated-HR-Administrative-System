from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from openpyxl.utils.exceptions import InvalidFileException

from app.repositories.factory import get_repository
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.services.excel_service import ExcelAttendanceService
from app.utils.responses import ok

router = APIRouter(prefix='/attendance', tags=['attendance'])
ai_service = AIService()
excel_service = ExcelAttendanceService()


def _employee_index(repository) -> dict[str, dict]:
    items = repository.list('employees')
    result = {}
    for item in items:
        employee_no = str(item.get('employee_no') or item.get('employeeNo') or '').strip()
        if employee_no:
            result[employee_no] = item
    return result


def _validate_records_with_employees(records: list[dict], employee_map: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    valid_records = []
    errors = []
    for record in records:
        employee_no = str(record.get('employeeNo') or '').strip()
        employee = employee_map.get(employee_no)
        if not employee:
            errors.append({
                'row': record.get('_row', ''),
                'employeeNo': employee_no,
                'name': record.get('name', ''),
                'department': record.get('department', ''),
                'message': '员工工号不存在，无法关联员工档案',
            })
            continue
        record['name'] = record.get('name') or employee.get('name', '')
        record['department'] = employee.get('department') or record.get('department', '')
        valid_records.append(record)
    return valid_records, errors


def _infer_department(employee_no: str = '', department: str = '') -> str:
    department = str(department or '').strip()
    if department:
        return department
    employee_no = str(employee_no or '').strip().upper()
    if employee_no.startswith('HR'):
        return '综合管理部'
    if employee_no.startswith('OPS'):
        return '运营中心'
    if employee_no.startswith('DEV'):
        return '产品技术部'
    if employee_no.startswith('MKT'):
        return '市场部'
    if employee_no.startswith('SAL'):
        return '销售部'
    if employee_no.startswith('FIN'):
        return '财务部'
    return '未分组'


def _attendance_summary_snapshot(rows: list[dict], department: str = '') -> tuple[list[dict], dict]:
    scoped_rows = [row for row in rows if not department or _infer_department(row.get('employeeNo', ''), row.get('department', '')) == department]
    department_map: dict[str, dict] = {}
    for row in scoped_rows:
        dept = _infer_department(row.get('employeeNo', ''), row.get('department', ''))
        bucket = department_map.setdefault(dept, {
            'department': dept,
            'total': 0.0,
            'lateTimes': 0,
            'earlyTimes': 0,
            'leaveHours': 0.0,
            'absenteeismDays': 0.0,
            'abnormalEmployees': set(),
        })
        should_attendance = float(row.get('shouldAttendance') or 1)
        bucket['total'] += should_attendance
        if row.get('status') != '正常':
            bucket['abnormalEmployees'].add(row.get('employeeNo') or row.get('name') or f"{dept}-{bucket['total']}")
        if '迟到' in str(row.get('status') or ''):
            bucket['lateTimes'] += 1
        if '早退' in str(row.get('status') or ''):
            bucket['earlyTimes'] += 1
        bucket['leaveHours'] += float(row.get('leaveHours') or 0)
        bucket['absenteeismDays'] += float(row.get('absenteeismDays') or (1 if '旷工' in str(row.get('status') or '') else 0))
    department_rows = []
    for item in department_map.values():
        attendance_rate = f"{(((item['total'] - item['absenteeismDays']) / item['total']) * 100):.1f}%" if item['total'] else '0.0%'
        department_rows.append({
            'department': item['department'],
            'attendanceRate': attendance_rate,
            'abnormalCount': len(item['abnormalEmployees']),
            'lateTimes': item['lateTimes'],
            'earlyTimes': item['earlyTimes'],
            'leaveHours': round(item['leaveHours'], 2),
            'absenteeismDays': round(item['absenteeismDays'], 2),
        })
    department_rows.sort(key=lambda item: item['department'])
    summary = {
        'recordCount': len(scoped_rows),
        'departmentCount': len(department_rows),
        'lateTimes': sum(item['lateTimes'] for item in department_rows),
        'earlyTimes': sum(item['earlyTimes'] for item in department_rows),
        'leaveHours': round(sum(item['leaveHours'] for item in department_rows), 2),
        'absenteeismDays': round(sum(item['absenteeismDays'] for item in department_rows), 2),
        'analysis': '整体考勤情况基本稳定，建议重点关注异常人数较高及旷工波动明显的部门。' if department_rows else '当前筛选条件下暂无考勤数据。',
    }
    return department_rows, summary


@router.get('/overview')
async def get_attendance_overview(user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    rows = repository.list('attendance')
    department_rows, department_summary = _attendance_summary_snapshot(rows)
    return ok({
        'records': rows,
        'overview': department_rows,
        'departments': department_rows,
        'summary': {
            'imported_records': len(rows),
            'abnormal_records': len([item for item in rows if item.get('status') != '正常']),
            'leave_requests': len(repository.list('leaves')),
            'overtime_hours': round(sum(float(item.get('workHours', 0)) - 8 for item in rows if float(item.get('workHours', 0)) > 8), 2),
            **department_summary,
        },
        'ai': {
            'summary': '考勤总览接口已切换为快速返回模式，AI 汇总请通过单独报表接口生成。',
        },
    })


@router.post('/ai/generate-summary-report')
async def generate_attendance_summary_report(payload: dict, user=Depends(require_roles('hr'))):
    repository = get_repository()
    rows = repository.list('attendance')
    department = str(payload.get('department') or '').strip()
    year = str(payload.get('year') or '').strip()
    month = str(payload.get('month') or '').strip().zfill(2) if payload.get('month') else ''
    target_prefix = f'{year}-{month}' if year and month else str(payload.get('monthValue') or '').strip()
    scoped_rows = [row for row in rows if (not target_prefix or str(row.get('month') or row.get('date') or '').startswith(target_prefix))]
    department_rows, summary = _attendance_summary_snapshot(scoped_rows, department)
    try:
        result = await ai_service.generate_attendance_summary_report({
            'department': department or '全部部门',
            'year': year,
            'month': month,
            'departmentRows': department_rows,
            'summary': summary,
        })
        repository.upsert('attendance_ai_reports', {
            'type': 'summary-report',
            'filters': {'department': department, 'year': year, 'month': month, 'monthValue': target_prefix},
            'report': result,
            'summary': summary,
        })
        return ok(result, 'AI 考勤汇总报表生成完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 考勤汇总报表生成失败: {exc}') from exc


@router.post('/import/parse')
async def parse_attendance_file(file: UploadFile = File(...), month: str = '', user=Depends(require_roles('hr'))):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail='请上传考勤文件')
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='仅支持 .xlsx 文件')
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='上传文件为空')
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='文件大小不能超过 20MB')
    try:
        repository = get_repository()
        parsed = excel_service.parse(content, month)
        employee_map = _employee_index(repository)
        valid_records, relation_errors = _validate_records_with_employees(parsed['records'], employee_map)
        parsed['records'] = valid_records
        parsed['errors'] = [*parsed['errors'], *relation_errors]
        parsed['success_count'] = len(valid_records)
        parsed['error_count'] = len(parsed['errors'])
        parsed['total_count'] = parsed['success_count'] + parsed['error_count']
        return ok({
            'fileName': file.filename,
            'fileSize': len(content),
            'month': month,
            'parsed': parsed,
        }, '考勤文件解析完成')
    except InvalidFileException as exc:
        raise HTTPException(status_code=400, detail='Excel 文件格式异常') from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'考勤文件解析失败: {exc}') from exc


@router.post('/import')
async def import_attendance(file: UploadFile = File(...), month: str = '', user=Depends(require_roles('hr'))):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail='请上传考勤文件')
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='仅支持 .xlsx 文件')
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='上传文件为空')
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='文件大小不能超过 20MB')
    try:
        repository = get_repository()
        parsed = excel_service.parse(content, month)
        employee_map = _employee_index(repository)
        valid_records, relation_errors = _validate_records_with_employees(parsed['records'], employee_map)
        parsed['records'] = valid_records
        parsed['errors'] = [*parsed['errors'], *relation_errors]
        parsed['success_count'] = len(valid_records)
        parsed['error_count'] = len(parsed['errors'])
        parsed['total_count'] = parsed['success_count'] + parsed['error_count']
        stored_records = []
        for record in valid_records:
            clean_record = {key: value for key, value in record.items() if key != '_row'}
            stored_records.append(repository.upsert('attendance', clean_record))
        document = repository.upsert('attendance_imports', {
            'fileName': file.filename,
            'fileSize': len(content),
            'month': month,
            'status': '已导入',
            'matchedFields': parsed['matched_fields'],
            'errors': parsed['errors'],
            'importedCount': len(stored_records),
            'successCount': parsed['success_count'],
            'errorCount': parsed['error_count'],
        })
        ai_result = await ai_service.attendance_summary(stored_records)
        return ok({'import': document, 'records': stored_records, 'ai': ai_result}, '考勤文件解析并入库完成')
    except InvalidFileException as exc:
        raise HTTPException(status_code=400, detail='Excel 文件格式异常') from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'考勤文件导入失败: {exc}') from exc
