from enum import Enum

from ocp_resources.resource import NamespacedResource
from oadp_constants.resources import ApiGroups
from oadp_utils.wait import wait_for
from oadp_utils.phase import check_phase


class BackupStorageLocation(NamespacedResource):
    api_group = ApiGroups.VELERO_API_GROUP.value

    class BackupStorageLocationAccessMode(Enum):
        BackupStorageLocationAccessModeReadOnly = 'ReadOnly'
        BackupStorageLocationAccessModeReadWrite = 'ReadWrite'

    class BackupStorageLocationPhase(Enum):
        Available = 'Available'
        Unavailable = 'Unavailable'

    def available(self):
        return check_phase(self, self.BackupStorageLocationPhase.Available.value)

    def unavailable(self):
        return check_phase(self, self.BackupStorageLocationPhase.Unavailable.value)

    def wait_for_bsl_status_available(self, wait_timeout=200, sleep=5):
        return wait_for(
            self.available,
            description=f"{self.kind} phase to become available, {self.name}",
            sleep=sleep,
            wait_timeout=wait_timeout
        )

    def wait_for_bsl_status_unavailable(self, wait_timeout=200, sleep=5):
        return wait_for(
            self.unavailable,
            description=f"{self.kind} phase to become unavailable, {self.name}",
            sleep=sleep,
            wait_timeout=wait_timeout
        )
