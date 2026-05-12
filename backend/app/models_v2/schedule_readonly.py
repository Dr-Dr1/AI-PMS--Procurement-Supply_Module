# Re-exports for backward compatibility with any imports using ReadOnly aliases.
# Full model definitions live in schedule.py / structure.py / baseline.py.

from app.models_v2.schedule import (         # noqa: F401
    ScheduleV2Import       as ScheduleV2ImportReadOnly,
    ScheduleV2Project      as ScheduleV2ProjectReadOnly,
    ScheduleV2Activity     as ScheduleV2ActivityReadOnly,
    ScheduleV2WBS          as ScheduleV2WBSReadOnly,
    ScheduleV2Calendar     as ScheduleV2CalendarReadOnly,
    ScheduleV2Resource     as ScheduleV2ResourceReadOnly,
    ScheduleV2Relationship as ScheduleV2RelationshipReadOnly,
    ScheduleV2ResourceAssignment as ScheduleV2ResourceAssignmentReadOnly,
    ScheduleV2Dependency   as ScheduleV2DependencyReadOnly,
)
from app.models_v2.structure import (        # noqa: F401
    ScheduleV2Corridor as ScheduleV2CorridorReadOnly,
    ScheduleV2Package  as ScheduleV2PackageReadOnly,
)
from app.models_v2.baseline import (         # noqa: F401
    ScheduleV2Baseline             as ScheduleV2BaselineReadOnly,
    ScheduleV2BaselineHistory      as ScheduleV2BaselineHistoryReadOnly,
    ScheduleV2EVMSnapshot          as ScheduleV2EVMSnapshotReadOnly,
    ScheduleV2ActivityBaselineLink as ScheduleV2ActivityBaselineLinkReadOnly,
)
