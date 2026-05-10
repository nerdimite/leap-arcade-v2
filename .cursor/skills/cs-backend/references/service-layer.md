# Service Layer

## BaseService

Every service extends `BaseService`, receiving `UserContext` and `ContextManager`:

```python
class BaseService(ABC):
    def __init__(self, context: UserContext, context_manager: ContextManager):
        self.context = context
        self.context_manager = context_manager
        self.logger = get_app_context().logger
        self._guard: Optional[AccessControlGuard] = None

    @property
    def guard(self) -> AccessControlGuard:
        if self._guard is None:
            policy_provider = self.context_manager.get_policy_provider()
            self._guard = AccessControlGuard(self.context, policy_provider)
        return self._guard

    @property
    def user_id(self) -> str:
        return self.context.id

    @property
    def org_id(self) -> str:
        return self.context.org.id

    @property
    def user_email(self) -> Optional[str]:
        return self.context.user.email
```

## Service Implementation Pattern

```python
class ScheduleService(BaseService):
    def __init__(self, context: UserContext, context_manager: ContextManager):
        super().__init__(context, context_manager)
        self.schedule_dao = ScheduleDAO(context, context_manager, guard=self.guard)
        self.slot_dao = SlotDAO(context, context_manager, guard=self.guard)

    async def create_schedule(self, request: CreateScheduleRequest) -> ScheduleInternal:
        # 1. Validate input
        if request.start_time >= request.end_time:
            raise InvalidTimeRangeException()

        # 2. ABAC: authorize create
        self.guard.authorize_create("schedules", {"org_id": self.org_id})

        # 3. Build domain type
        schedule_data = ScheduleCreate(
            org_id=self.org_id,
            practitioner_id=request.practitioner_id,
            start_time=request.start_time,
            end_time=request.end_time,
        )

        # 4. Delegate to DAO
        schedule = await self.schedule_dao.create_schedule(schedule_data)

        self.logger.info("schedule_created", schedule_id=schedule.id)
        return schedule
```

## Key Patterns

### DAO Initialization
- Create DAOs in `__init__`, passing `self.guard`
- Guard is shared across all DAOs in a service — same user context

### ABAC Authorization
- **CREATE**: Call `self.guard.authorize_create(resource_name, payload_dict)` explicitly
- **READ/LIST/UPDATE/DELETE**: Handled automatically by DAO's `_apply_abac_filters()`

### Request → Domain Type Conversion
- Routes pass request schemas (user-facing, no `org_id`)
- Service converts to domain types (adds `org_id`, generates IDs)
- DAO receives domain types and handles persistence

### Error Handling
- Validate business rules, raise domain exceptions
- DAO returns `None` for not-found → service raises `NotFoundException`
- ABAC denials raise `PermissionError` → caught by global handler

## Domain Exceptions

Each domain has its own exception file:

```python
class ScheduleNotFoundException(BaseServiceException):
    def __init__(self, schedule_id: str):
        super().__init__(
            error_code=ErrorCodes.SCHEDULE_NOT_FOUND,
            message=ErrorMessages.SCHEDULE_NOT_FOUND,
            http_status=ErrorHttpStatus.SCHEDULE_NOT_FOUND,
            details={"schedule_id": schedule_id},
        )

class InvalidTimeRangeException(BaseServiceException):
    def __init__(self):
        super().__init__(
            error_code=ErrorCodes.INVALID_TIME_RANGE,
            message=ErrorMessages.INVALID_TIME_RANGE,
            http_status=ErrorHttpStatus.INVALID_TIME_RANGE,
        )
```

All exceptions:
1. Extend `BaseServiceException`
2. Reference codes from `config/errors.py`
3. Accept resource identifiers for the `details` dict
4. Are caught by the global `BaseServiceException` handler

## Service Composition

For complex operations spanning multiple domains, a service can use other services or DAOs:

```python
class BookingService(BaseService):
    def __init__(self, context, context_manager):
        super().__init__(context, context_manager)
        self.slot_dao = SlotDAO(context, context_manager, guard=self.guard)
        self.appointment_dao = AppointmentDAO(context, context_manager, guard=self.guard)
        self.metadata_dao = MetadataDAO(context, context_manager, guard=self.guard)

    async def book(self, request):
        # 1. Reserve slots
        # 2. Create appointment
        # 3. Link metadata
        # 4. Rollback on failure
```

Keep orchestration in the service; DAOs stay single-responsibility.
