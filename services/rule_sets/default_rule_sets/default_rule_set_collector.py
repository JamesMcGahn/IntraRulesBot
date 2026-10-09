from .avaya_statistics import AVAYA_STATS_ONLY
from .genesys_cloud_statistics import GENESYS_STATS_ONLY
from .genesys_cloud_acd_state_tis import GEN_CLOUD_ACD_TIS


def default_rule_set_collector() -> list[dict]:
    rule_set_list = [AVAYA_STATS_ONLY, GENESYS_STATS_ONLY, GEN_CLOUD_ACD_TIS]
    return rule_set_list
