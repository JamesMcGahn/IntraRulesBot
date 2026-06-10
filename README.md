# IntraRulesBot

## File Structure

```bash
├── __version__.py
├── app_styles_css.py
├── base
│   ├── enums
│   ├── errors
│   ├── events
├── color_palete.md
├── context
│   └── context.py
├── controllers
│   ├── controller_factory.py
│   ├── models
│   ├── queues
│   │   ├── enums
│   │   ├── models
│   │   ├── queues_controller.py
│   │   ├── queues_run_monitor_controller.py
│   │   └── queues_validation_coordinator.py
│   ├── rule_sets
│   │   └── rule_sets_controller.py
│   ├── rules
│   │   ├── enums
│   │   ├── models
│   │   ├── rules_controller.py
│   │   ├── rules_run_monitor_controller.py
│   │   └── rules_validation_coordinator.py
│   ├── settings_controller.py
│   └── ui_controller.py
├── main.py
├── Pipfile
├── Pipfile.lock
├── pysidedeploy_mac.spec
├── pysidedeploy_windows.spec
├── README.md
├── requirements.txt
├── schemas
│   ├── enums
│   ├── examples
│   │   ├── actions
│   │   ├── conditions
│   │   └── triggers
│   ├── main_schema.py
│   ├── queue_schema.py
│   ├── registry
│   │   └── schema_registry.py
│   ├── rules_schema.py
│   └── trigger_action_based.py
├── services
│   ├── auth
│   │   ├── auth_service.py
│   │   ├── base_auth_service.py
│   │   ├── enums
│   │   ├── models
│   │   └── session
│   ├── base
│   │   ├── enums
│   │   └── models
│   ├── browser
│   │   ├── adapters
│   │   ├── browser_session_factory.py
│   │   ├── models
│   │   ├── play_wright_session_manager.py
│   │   └── ports
│   ├── files
│   │   ├── json_file_service.py
│   │   ├── models
│   │   └── spreadsheet_file_service.py
│   ├── intra
│   │   ├── intra_auth_service.py
│   │   ├── intra_provider_session.py
│   │   ├── login_worker.py
│   │   └── models
│   ├── lifecycle
│   │   ├── models
│   │   ├── protocols
│   │   ├── shut_down_coordinator.py
│   │   └── start_up_coordinator.py
│   ├── logger
│   │   ├── adapters
│   │   ├── log_worker.py
│   │   └── logger.py
│   ├── monitor
│   │   ├── models
│   │   ├── queue_monitor
│   │   └── rule_monitor
│   ├── profiles
│   │   ├── defaults
│   │   ├── models
│   │   ├── profile_registry.py
│   │   └── rules
│   ├── queue_runner
│   │   ├── enums
│   │   ├── executors
│   │   ├── models
│   │   ├── queue_runner_service.py
│   │   └── queue_runner_worker.py
│   ├── queues
│   │   ├── models
│   │   └── queue_builder.py
│   ├── rule_runner
│   │   ├── enums
│   │   ├── executors
│   │   ├── interfaces
│   │   ├── models
│   │   ├── rule_runner_service.py
│   │   └── rule_runner_worker.py
│   ├── rule_sets
│   │   ├── default_rule_set_provider.py
│   │   ├── default_rule_sets
│   │   ├── models
│   │   ├── rule_set_builder.py
│   │   ├── rule_set_registry.py
│   │   ├── rule_set_serializer.py
│   │   └── rule_set_storage.py
│   ├── rules
│   │   ├── enums
│   │   ├── models
│   │   ├── rule_builder.py
│   │   ├── rule_serializer.py
│   │   ├── rule_storage.py
│   │   └── rules_registry.py
│   ├── settings
│   │   ├── enums
│   │   ├── events
│   │   ├── models
│   │   ├── providers
│   │   ├── secure_settings.py
│   │   ├── settings_repository.py
│   │   ├── settings_service.py
│   │   ├── settings.py
│   │   └── validators
│   └── validation
│       ├── base_validator.py
│       ├── enums
│       ├── interfaces
│       ├── models
│       ├── schema_validator.py
│       ├── settings_validator.py
│       └── validation_service.py
├── todos.md
├── utils
│   └── files
│       └── path_manager.py
└── views
    ├── base
    │   ├── enums
    │   └── field_registry.py
    ├── components
    │   ├── boxes
    │   ├── buttons
    │   ├── dialogs
    │   ├── helpers
    │   ├── layouts
    │   ├── rules
    │   └── toasts
    ├── layout
    │   ├── central_widget
    │   ├── main_screen
    │   └── navbars
    ├── main_window.py
    └── pages
        ├── bookmarks
        ├── queues
        ├── rules
        └── settings
```

## Installation

### Requirements

- Python 3.12+

```bash
pipenv install
```

or

```bash
pip install -r requirements.txt
```

### How to Run

Windows

```bash
python main.py
```

Mac

```bash
python3 main.py
```

## How To Deploy

The application will deploy based on the settings in the pysidedeploy.spec file. The spec file is configured for Windows Applications but will also work on Mac.
In the spec file, update the paths to exec_directory, icon and python_path. Then run the below in console.

```bash
pyside6-deploy
```

## Supported Use Cases:

### ACD Queue Input

- Add Queues from Excel File

### Triggers:

- Frequency Based
- Action Triggers:
  - ACD
    - Agent Changed State Trigger
    - Agent Logged In
    - Agent Logged Out
    - Time in State
  - Intradiem
    - Users
    - Quick Action Clicked

### Condition:

- ACD:
  - Statistic

### Actions:

- Communications
  - Email

## How To Add Rule Use Case

- update schema
- add scope detailed dataclass
- update detail enum
- update services/rules/rule_builder
- update views/rules/rule_factory
- update services/profiles/rules dc
- update the profile implementation with selectors
- add detailed executor
- update scope executor
