import logging

from ocp_resources.resource import NamespacedResource
from src.oadp_constants.resources import ApiGroups

from src.oadp_constants.oadp.datamover.volume_snapshot_restore import VolumeSnapshotRestorePhase
from src.oadp_resources.volsync.replication_destination import ReplicationDestination

logger = logging.getLogger(__name__)


class VolumeSnapshotRestore(NamespacedResource):
    api_group = ApiGroups.DATAMOVER_OADP_API_GROUP.value

    def replication_destination_completed(self):
        try:
            conditions = self.status.conditions

        except AttributeError as e:
            return False

        return len(conditions) > 1 and \
            conditions[0].type == "Reconciled" and \
            conditions[0].type.status and \
            conditions[1].type == "Synchronizing" and \
            not conditions[1].status

    def done(self):
        """
        Check is VSR process is done
        @return: True if the VSR process is not running; False otherwise
        """
        return self.instance.status and self.instance.status.phase != \
            VolumeSnapshotRestorePhase.SnapMoverRestorePhaseInProgress.value

    @classmethod
    def get_by_restore_name(cls, restore_name):
        """
        Returns a list of VSRs by restore name
        @param restore_name: the restore name to get the VSR/s by
        @return: returns a list of VSR/s by restore name restore_name; empty list otherwise
        """
        return list(cls.get(label_selector=f"velero.io/restore-name={restore_name}"))

    @classmethod
    def get_by_source_pvc(cls, src_pvc_name: str, vsr_list: list = None):
        """
        Returns a list of VSRs by source PVC
        @param src_pvc_name: PVC name which the VSR/s point to
        @param vsr_list: the list of VSR/s to filter based on the PVC name; in case not provided, it will be retrieved
        @return: a list of VSRs by source PVC; empty list otherwise
        """
        if not vsr_list:
            vsr_list = list(cls.get())
        vsr_filtered_list = list(filter(
            lambda x: x.instance.spec.volumeSnapshotMoverBackupRef.sourcePVCData.name == src_pvc_name, vsr_list))

        return vsr_filtered_list

    def get_replication_destination(self):
        replication_destination_list = ReplicationDestination.get()
        rep_ds_list = [rd for rd in replication_destination_list if
                       rd.labels.get("datamover.oadp.openshift.io/vsr") == self.name]
        if len(rep_ds_list) > 1:
            logger.error(f"There are more than one ReplicationDestination for VSR {self.name}")
            return None
        if len(rep_ds_list) == 0:
            logger.error(f"ReplicationDestination was not created for VSR {self.name}")
            return None

        return rep_ds_list[0]
