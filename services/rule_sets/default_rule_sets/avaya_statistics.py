AVAYA_STATS_ONLY = {
    "rule_set_name": "Avaya ACD - Stats Only",
    "description": "Avaya Stats SIT Rules",
    "default": True,
    "rules": [
        {
            "rule_name": "ZZ_SIT__avaya_agents_available_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents Available - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_available_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_available_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_available_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents Available - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_available_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_available_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_acw_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents in After Call Work - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_acw_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_acw_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_acw_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents in After Call Work - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_acw_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_acw_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_in_call_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents in Call - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_in_call_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_in_call_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_in_call_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents in Call - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_in_call_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_in_call_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_calls_in_queue_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Calls in Queue - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_calls_in_queue_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_calls_in_queue_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_calls_in_queue_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Calls in Queue - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_calls_in_queue_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_calls_in_queue_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_expt_wait_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Expected Wait Time (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_expt_wait_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_expt_wait_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_expt_wait_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Expected Wait Time (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_expt_wait_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_expt_wait_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_agents_staffed_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents Staffed - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_agents_staffed_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_agents_staffed_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_agents_staffed_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Agents Staffed - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_agents_staffed_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_agents_staffed_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_avg_speed_answer_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Average Speed of Answer (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_avg_speed_answer_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_avg_speed_answer_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_avg_speed_answer_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Average Speed of Answer (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_avg_speed_answer_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_avg_speed_answer_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_longest_call_wait_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Longest Call Waiting (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_longest_call_wait_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_longest_call_wait_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_longest_call_wait_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Longest Call Waiting (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_longest_call_wait_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_longest_call_wait_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_avg_time_to_abandon_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Average Time to Abandon (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_avg_time_to_abandon_ABOVE",
                        "email_body": "ZZ_SIT__avaya_agents_avg_time_to_abandon_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_agents_avg_time_to_abandon_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Average Time to Abandon (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_agents_avg_time_to_abandon_BELOW",
                        "email_body": "ZZ_SIT__avaya_agents_avg_time_to_abandon_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_calls_in_queue_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Calls in Queue - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_calls_in_queue_ABOVE",
                        "email_body": "ZZ_SIT__avaya_calls_in_queue_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_calls_in_queue_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Calls in Queue - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_calls_in_queue_BELOW",
                        "email_body": "ZZ_SIT__avaya_calls_in_queue_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_acd_calls_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Number of Calls - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_acd_calls_ABOVE",
                        "email_body": "ZZ_SIT__avaya_acd_calls_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_acd_calls_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Number of Calls - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_acd_calls_BELOW",
                        "email_body": "ZZ_SIT__avaya_acd_calls_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_sla_percent_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Service Level Percent - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_sla_percent_ABOVE",
                        "email_body": "ZZ_SIT__avaya_sla_percent_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_sla_percent_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Service Level Percent - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_sla_percent_BELOW",
                        "email_body": "ZZ_SIT__avaya_sla_percent_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_avg_handle_talk_time_ABOVE",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Average Handling Time (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 0,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_avg_handle_talk_time_ABOVE",
                        "email_body": "ZZ_SIT__avaya_avg_handle_talk_time_ABOVE",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "ZZ_SIT__avaya_avg_handle_talk_time_BELOW",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 1},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "gias_pbx_2",
                    "provider_condition": "Average Handling Time (seconds) - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Less Than",
                        "equality_threshold": 9999,
                        "queues_source": "users",
                    },
                }
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "ZZ_SIT__avaya_avg_handle_talk_time_BELOW",
                        "email_body": "ZZ_SIT__avaya_avg_handle_talk_time_BELOW",
                        "email_address": "example@example.com",
                    },
                }
            ],
        },
    ],
}
