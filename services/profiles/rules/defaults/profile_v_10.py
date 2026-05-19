from ....rule_runner.models.rule_path_profile import RulePathProfile
from ..models import (
    RuleFormSelectors,
    RuleExecutorSelectors,
    TriggerSelectors,
    TriggerCommonSelectors,
    TriggerStateChangedSelectors,
    ConditionSelectors,
    ConditionCommonSelectors,
    ConditionStatsSelectors,
    ActionCommonSelectors,
    ActionSelectors,
    ActionEmailSelectors,
)


from base.enums import INTRAVERSION
from ....rules.enums import (
    ACTIONTRIGGERDETAILTYPE,
    CONDITIONDETAILTYPE,
    ACTIONDETAILTYPE,
)

v_10 = RulePathProfile(
    version=INTRAVERSION.V10,
    selectors=RuleExecutorSelectors(
        rule_form=RuleFormSelectors(
            page_path="ManagerConsole/Delivery/Rules.aspx",
            add_rule_button="#ctl00_ActionBarContent_rbAction_Add",
            rule_name_input='[id*="overlayRuleProgressArea_tbRuleName"]',
            rule_category_frame='iframe[name="RadWindowAddEditRuleSettings"]',
            add_rule_category_button='[id*="ctl00_overlayContent_divRuleSummaryHeader"] a[href*="RuleSettings"]',
            rule_category_dropdown_arrow='[id*="ddRuleCategory_Arrow"]',
            rule_category_dropdown_list='//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            submit_button='[id*="overlayButtons_rbSubmit_input"]',
            rule_modal_frame='iframe[name="RadWindowAddEditRule"]',
            next_page_button='[id*="overlayButtons_rbContinue_input"]',
            tutorial_checkbox='[id*="overlayButtonsLeft_cbDontAskLead"]',
            success_marker="#ctl00_ActionBarContent_rbAction_Add",
        ),
        triggers=TriggerSelectors(
            common=TriggerCommonSelectors(
                frequency_dropdown_arrow='[id*="overlayContent_triggerParameters_frequencyComboBox_Arrow"]',
                frequency_dropdown_list='//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
                add_event_trigger_button='[id*="overlayContent_lblAddEventSetFrequency"]',
                provider_category_items='//*[contains(@id, "overlayContent_selectTrigger_radMenuCategory")]/ul/li',
                provider_instance_items='//*[contains(@id, "overlayContent_selectTrigger_radMenuProviderInstance")]/ul/li',
                provider_condition_items='//*[contains(@id, "overlayContent_selectTrigger_radMenuItem")]/ul/li',
            ),
            details={
                ACTIONTRIGGERDETAILTYPE.STATE_CHANGED: TriggerStateChangedSelectors(
                    state_dropdown_arrow='[id*="overlayContent_triggerParameters_agentStateSelectValue_Arrow"]',
                    state_dropdown_items='//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_DropDown")]/div/ul/li',
                    aux_input='[id*="overlayContent_triggerParameters_agentStateAuxCodeValue"]',
                    add_state_button='//*[contains(@id, "overlayContent_triggerParameters_divParameters")]/div[1]/div[1]/div[3]/img',
                    equal_to_radio='[id*="overlayContent_triggerParameters_ctl16_0"]',
                    not_equal_to_radio='[id*="overlayContent_triggerParameters_ctl16_1"]',
                    user_list_arrow='[id*="user_filter_static_id_Arrow"]',
                    user_list_items='//*[contains(@id, "user_filter_static_id_DropDown")]/div/ul/li',
                )
            },
        ),
        conditions=ConditionSelectors(
            common=ConditionCommonSelectors(
                provider_category_items='//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
                provider_instance_items='//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
                provider_condition_items='//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
                add_condition_button='[id*="overlayContent_lblAddCondition"]',
            ),
            details={
                CONDITIONDETAILTYPE.STATS: ConditionStatsSelectors(
                    equality_operator_dropdown_arrow='[id*="overlayContent_conditionParameters_ddExposedDataOperator_Arrow"]',
                    equality_operator_dropdown_items='//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_DropDown")]/div/ul/li',
                    equality_threshold_input='[id*="overlayContent_conditionParameters_tbExposedDataValue"]',
                    queue_source_radio='[id*="overlayContent_conditionParameters_ctl16_1"]',
                    queue_dropdown_arrow='[id*="overlayContent_conditionParameters_ctl22_Arrow"]',
                    queue_dropdown_items='//*[contains(@id, "overlayContent_conditionParameters_ctl22_DropDown")]/div/ul/li',
                )
            },
        ),
        actions=ActionSelectors(
            common=ActionCommonSelectors(
                provider_category_items='//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
                provider_instance_items='//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuProviderInstance")]/ul/li',
                provider_condition_items='//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuItem")]/ul/li',
                add_action_button='[id*="overlayContent_lblAddAction"]',
            ),
            details={
                ACTIONDETAILTYPE.EMAIL: ActionEmailSelectors(
                    email_settings_button='[id*="overlayContent_actionParameters_lblSettings"]',
                    email_subject='[id*="overlayContent_actionParameters_ctl05"]',
                    email_message="""[id*="overlayContent_actionParameters_ctl12"],[id*="overlayContent_actionParameters_ctl13"]""",
                    user_settings_button='[id*="overlayButtons_rbContinue_input"]',
                    email_individual_radio='[id*="overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1"]',
                    email_address="""textarea[id*="overlayContent_actionParameters_ctl65"],textarea[id*="overlayContent_actionParameters_ctl61"]""",
                )
            },
        ),
    ),
)
