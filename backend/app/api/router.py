from fastapi import APIRouter

from app.api.routes import (
    administration,
    ai,
    approvals,
    attendance,
    auth,
    dashboard,
    employees,
    leaves,
    payroll,
    performance,
    reports,
)

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(employees.router)
api_router.include_router(attendance.router)
api_router.include_router(leaves.router)
api_router.include_router(performance.router)
api_router.include_router(payroll.router)
api_router.include_router(approvals.router)
api_router.include_router(administration.router)
api_router.include_router(reports.router)
api_router.include_router(ai.router)
