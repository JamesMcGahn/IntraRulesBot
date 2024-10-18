example_02 = {
    "id": "default",
    "name": "Rule Set Name 2",
    "description": "Rule Set for Rules 2 \n Notes: \n notes for rule set ",
    "rules": [
        {
            "rule_name": "zzjmTest Rule 53",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 5},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "Avaya Test ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                },
                {
                    "provider_category": "ACD",
                    "provider_instance": "Avaya Test ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                },
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "Test Subject",
                        "email_body": "Test body",
                        "email_address": "test@example.com",
                    },
                }
            ],
        },
        {
            "rule_name": "zzjmTest Rule 5",
            "rule_category": "Other - Admin",
            "frequency_based": {"time_interval": 5},
            "conditions": [
                {
                    "provider_category": "ACD",
                    "provider_instance": "Avaya Test ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                },
                {
                    "provider_category": "ACD",
                    "provider_instance": "Avaya Test ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                },
            ],
            "actions": [
                {
                    "provider_category": "Communications",
                    "provider_instance": "Email Provider Instance",
                    "provider_condition": "Send Email",
                    "details": {
                        "action_type": "email",
                        "email_subject": "Test Subject",
                        "email_body": "Test body",
                        "email_address": "test@example.com",
                    },
                }
            ],
        },
    ],
}
