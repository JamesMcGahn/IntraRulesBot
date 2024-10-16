# IntraRulesBot

## File Structure

```bash
├── base
├── components
│   ├── boxes
│   ├── buttons
│   ├── dialogs
│   ├── helpers
│   ├── layouts
│   └── toasts
├── managers
├── models
├── resources
│   ├── fonts
│   ├── images
│   └── system_icons
├── rulerunner
│   ├── actions
│   ├── conditions
│   ├── login
│   ├── triggers
│   └── utils
├── schemas
├── services
│   ├── event_filter
│   ├── logger
│   ├── settings
│   └── validator
├── translators
│   └── generate_rule_object
├── utils
│   └── files
└── views
    ├── layout
    └── pages
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
