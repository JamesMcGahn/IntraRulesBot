example_01 = {
    "rule_set_name": "test",
    "description": "Saved Rules From Editor",
    "default": True,
    "rules": [
        {
            "actions": [
                {
                    "details": {
                        "action_type": "email",
                        "email_address": "test@example.com",
                        "email_body": "Test body",
                        "email_subject": "Test Subject",
                    },
                    "provider_category": "Communications",
                    "provider_condition": "Send Email",
                    "provider_instance": "Email Provider Instance",
                }
            ],
            "conditions": [
                {
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                    "provider_category": "ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "provider_instance": "Avaya Test ACD",
                },
                {
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                    "provider_category": "ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "provider_instance": "Avaya Test ACD",
                },
            ],
            "frequency_based": {"time_interval": 5},
            "guid": "d3d4e140-261d-4ad8-854f-a170f180bdba",
            "rule_category": "Other - Admin",
            "rule_name": "zzjmTest Rule 3",
        },
        {
            "actions": [
                {
                    "details": {
                        "action_type": "email",
                        "email_address": "test@example.com",
                        "email_body": "Test body",
                        "email_subject": "Test Subject",
                    },
                    "provider_category": "Communications",
                    "provider_condition": "Send Email",
                    "provider_instance": "Email Provider Instance",
                }
            ],
            "conditions": [
                {
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                    "provider_category": "ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "provider_instance": "Avaya Test ACD",
                },
                {
                    "details": {
                        "condition_type": "stats",
                        "equality_operator": "Greater Than",
                        "equality_threshold": 1,
                        "queues_source": "queues",
                    },
                    "provider_category": "ACD",
                    "provider_condition": "Agents in Other - By Queue",
                    "provider_instance": "Avaya Test ACD",
                },
            ],
            "frequency_based": {"time_interval": 5},
            "guid": "d7970514-9984-41e1-ae25-088f00ffda65",
            "rule_category": "Other - Admin",
            "rule_name": "zzjmTest Rule 5",
        },
    ],
}
