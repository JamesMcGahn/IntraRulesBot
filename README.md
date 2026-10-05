# IntraRulesBot

## File Structure

````bash

├── base
│   ├── enums
│   ├── errors
│   ├── events
├── color_palete.md
├── context
├── controllers
│   ├── controller_factory.py
│   ├── models
│   ├── profiles
│   ├── queues
│   ├── rule_sets
│   ├── rules
│   ├── settings_controller.py
│   └── ui_controller.py
├── schemas
│   ├── conditions_schema.py
│   ├── enums
│   ├── examples
│   ├── main_schema.py
│   ├── queue_schema.py
│   ├── registry
│   │   └── schema_registry.py
│   ├── rules_schema.py
│   └── trigger_action_based_schema.py
├── services
│   ├── api
│   │   └── queues
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
│   │   ├── models
│   │   ├── v10
│   │   └── v11
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
│   ├── network
│   │   ├── base_api.py
│   │   ├── enums
│   │   ├── models
│   │   ├── network_client.py
│   │   └── network_throttle.py
│   ├── profiles
│   │   ├── defaults
│   │   ├── models
│   │   ├── profile_builder.py
│   │   ├── profile_registry.py
│   │   └── profile_serializer.py
│   ├── queue_runner
│   │   ├── enums
│   │   ├── executors
│   │   ├── models
│   │   ├── queue_result_handler.py
│   │   ├── queue_runner_service.py
│   │   └── queue_runner_worker.py
│   ├── queues
│   │   ├── enums
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
├── utils
├── uv.lock
├── views
│   ├── base
│   │   ├── enums
│   │   └── field_registry.py
│   ├── components
│   │   ├── boxes
│   │   ├── buttons
│   │   ├── dialogs
│   │   ├── helpers
│   │   ├── layouts
│   │   ├── rules
│   │   └── toasts
│   ├── layout
│   │   ├── central_widget
│   │   ├── main_screen
│   │   └── navbars
│   ├── main_window.py
│   └── pages
│       ├── bookmarks
│       ├── logs
│       ├── queues
│       ├── rules
│       └── settings
├── main.py
├── pyproject.toml
├── pysidedeploy_mac.spec
├── pysidedeploy_windows.spec
├── __version__.py
├── app_styles_css.py
└── README.md

## Installation

### Requirements

- Python 3.12+

```bash
uv sync
````

## Getting Started

### 1. Install uv

Install `uv` if it is not already installed.

**macOS:**

```bash
brew install uv
```

**Windows:**

```powershell
winget install --id=astral-sh.uv -e
```

Verify the installation:

```bash
uv --version
```

### 2. Clone the repository

### 3. Install Python and project dependencies

Run:

```bash
uv sync
```

### 4. Run the application

```bash
uv run python main.py
```

## Virtual Environment

Activating the virtual environment manually is optional. Commands can normally be run directly with `uv run`.

If manual activation is desired:

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

Once activated, normal Python commands can be used:

```bash
python main.py
```

## How To Deploy

The application will deploy based on the settings in the pysidedeploy.spec file. The spec file is configured for Windows Applications but will also work on Mac.
In the spec file, update the paths to exec_directory, icon and python_path. Then run the below in console.

**macOS:**

```bash
uv run pyside6-deploy -c pysidedeploy_mac.spec
```

**Windows:**

```bash
uv run pyside6-deploy -c pysidedeploy_windows.spec
```

## Supported Use Cases:

### ACD Queue Input

Both V10 & V11 are supported.

- Add, Delete & Verify Queues from Excel File
- excel files must have queue_number & queue_name in heading
  - optional action_type header with commands of ADD, DELETE, VERIFY_EXISTS, & VERIFY_NOT_EXISTS

### Rules

**Note: V11 is not yet supported for Rules**

#### Triggers:

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
  - WFM
    - Segment Occurrence

#### Condition:

- ACD:
  - Statistic

#### Actions:

- Communications
  - Email

## How To Add Rule Use Case

- [ ] Update/Add schema in ./schemas
- [ ] Add scope detailed dataclass in .rules/models/
- [ ] Update scope detail enum in .rules/enums/
- [ ] Update Builder in services/rules/rule_builder
- [ ] Update Serialization in views/rules/rule_factory
- [ ] Update Browser Profile DC in services/profiles/rules DC
- [ ] Update Browser Profile implementation with selectors
- [ ] Add detailed executor in ./services/rule_runner/executors/{scope}
- [ ] Update scope executor in ./services/rule_runner/executors/{scope}
