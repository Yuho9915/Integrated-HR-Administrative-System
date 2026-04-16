from pydantic import BaseModel, Field, field_validator


class ApiResponse(BaseModel):
    success: bool = True
    message: str = 'ok'
    data: dict | list | None = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2)
    password: str = Field(..., min_length=1)
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyPasswordRequest(BaseModel):
    password: str = Field(..., min_length=1)


class AIChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    system_context: str | None = None


class AIChatResponse(BaseModel):
    content: str
    model: str


class DecisionRequest(BaseModel):
    decision: str
    comment: str | None = None


class BatchDecisionRequest(BaseModel):
    ids: list[str]
    decision: str
    comment: str | None = None


class EmployeePayload(BaseModel):
    employee_no: str
    name: str
    department: str
    position: str
    role: str
    salary_base: float
    performance_base: float
    hire_date: str
    resignation_date: str = ''
    status: str
    id_card_no: str
    phone: str
    email: str
    probation_end_date: str
    emergency_contact: str
    emergency_contact_phone: str
    political_status: str = ''
    gender: str = ''
    birth_date: str = ''
    registered_address: str = ''
    current_address: str = ''
    ethnicity: str = ''
    education: str = ''
    graduate_school: str = ''
    major: str = ''
    contract_type: str = ''
    contract_sign_date: str = ''
    contract_end_date: str = ''
    social_security_base: float = 0
    housing_fund_base: float = 0
    bank_account: str = ''
    bank_name: str = ''
    job_level: str = ''
    report_to: str = ''
    work_location: str = ''
    photo_attachment: dict = {}
    id_card_attachments: list[dict] = []
    education_certificate_attachments: list[dict] = []
    labor_contract_attachments: list[dict] = []
    medical_report_attachments: list[dict] = []

    @field_validator('salary_base')
    @classmethod
    def validate_salary_base(cls, value: float) -> float:
        if value <= 0:
            raise ValueError('基本工资不能为0')
        return value

    @field_validator('role')
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in {'employee', 'manager', 'hr', 'boss'}:
            raise ValueError('角色不合法')
        return value

    @field_validator('bank_account')
    @classmethod
    def validate_bank_account(cls, value: str) -> str:
        value = (value or '').strip()
        if not value:
            return value
        if not value.isdigit() or not 12 <= len(value) <= 19:
            raise ValueError('银行卡号需为12到19位数字')
        return value


class DepartmentPayload(BaseModel):
    name: str = Field(..., min_length=1)


class PositionPayload(BaseModel):
    department: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class LeavePayload(BaseModel):
    employee_no: str
    leave_type: str
    start_at: str
    end_at: str
    days: float
    reason: str


class SupplementPayload(BaseModel):
    employee_no: str
    date: str
    time: str
    reason: str
    cycle: str
    records: list[dict]


class PayrollCalculatePayload(BaseModel):
    month: str


class PerformanceCheckPayload(BaseModel):
    cycle: str = Field(..., min_length=1)
    records: list[dict] = Field(default_factory=list)


class AssetPayload(BaseModel):
    asset: str
    type: str
    owner: str
    status: str


class OfficeSupplyRequestPayload(BaseModel):
    employee_no: str
    item_name: str
    quantity: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1)
    needed_by: str = ''


class AssetRequestPayload(BaseModel):
    employee_no: str
    request_type: str
    asset_code: str = ''
    asset_name: str
    quantity: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1)
    needed_by: str = ''


class GeneralRequestPayload(BaseModel):
    employee_no: str
    request_type: str
    title: str = ''
    resource_code: str = ''
    resource_name: str = ''
    quantity: int = Field(default=1, ge=1)
    start_at: str = ''
    end_at: str = ''
    days: float = 0
    needed_by: str = ''
    reason: str = Field(..., min_length=1)
    meta: dict = Field(default_factory=dict)


class ResumeParsePayload(BaseModel):
    content: str = Field(..., min_length=10)


class IdCardParsePayload(BaseModel):
    attachments: list[dict] = Field(default_factory=list)
