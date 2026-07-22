from PySide6.QtCore import QObject, Signal, QThread

from base import QSingleton
from controllers import (
    RulesController,
    RuleSetsController,
    RulesRunMonitorController,
    RulesValidationCoordinator,
    SettingsController,
    UIController,
    QueuesController,
    QueuesValidationCoordinator,
    QueuesRunMonitorController,
)
from schemas.registry import SchemaRegistry
from services.auth.auth_service import AuthService
from services.auth.enums import PROVIDERS
from services.auth.session import SessionRegistry, SessionStore
from services.browser import BrowserSessionFactory
from services.lifecycle import ShutdownCoordinator, StartUpCoordinator
from services.logger import Logger
from services.logger.adapters import LogAdapter
from services.profiles import ProfileRegistry
from services.monitor.rule_monitor import RunMonitorStore
from services.monitor.queue_monitor import QueueMonitorStore
from services.rule_runner import RuleRunnerService
from services.rule_sets import (
    RuleSetBuilder,
    RuleSetRegistry,
    RuleSetSerializer,
    DefaultRuleSetProvider,
)
from services.files import JSONFileService, SpreadsheetFileService
from services.rules import RuleBuilder, RuleRegistry, RuleSerializer, RuleStore
from services.settings import (
    AppSettings,
    SecureCredentials,
    SettingsRepository,
    SettingsService,
)
from services.queues import QueueBuilder
from services.queue_runner import QueueRunnerService
from services.settings.enums import SETTINGSCATEGORIES
from services.settings.providers import (
    SettingsRuleRunnerConfigProvider,
    SettingsQueueRunnerConfigProvider,
)
from services.validation import ValidationService
from services.lifecycle.models import StartUpContainer


class AppContext(QObject, metaclass=QSingleton):
    app_shut_down_confirmed = Signal()
    setting_updated = Signal(object)
    send_logs = Signal(str, str, bool)
    start_up_completed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.preparing_for_shutdown = False
        self.logger = Logger()

        self.send_logs.connect(self.logger.insert)
        self.log_adapter = LogAdapter(self.logger)
        self.shut_down_coord = ShutdownCoordinator("APP", self.log_adapter)
        self.settings = AppSettings()
        self.secure_settings = SecureCredentials(self.log_adapter)
        self.settings_repo = SettingsRepository(self.settings, self.secure_settings)
        self.settings_manager = SettingsService(
            self.log_adapter, repo=self.settings_repo
        )

        log_settings = self.settings_manager.get_category(SETTINGSCATEGORIES.LOG)
        self.logger.load_settings(log_settings)
        self.logger.start_up()

        self.json_file_service = JSONFileService(self.log_adapter)
        self.spread_sheet_file_service = SpreadsheetFileService(self.log_adapter)

        self.session_store = SessionStore(self.json_file_service, self.log_adapter)
        self.session_registry = SessionRegistry(self.session_store, self.log_adapter)
        self.prolife_registry = ProfileRegistry()
        self.auth_service = AuthService(
            self.session_registry, self.prolife_registry, self.log_adapter
        )

        self.schema_registry = SchemaRegistry()

        self.rules_registry = RuleRegistry(self.log_adapter)
        self.rule_store = RuleStore()
        self.rule_builder = RuleBuilder(self.log_adapter)
        self.rule_serializer = RuleSerializer()

        self.rule_set_registry = RuleSetRegistry(self.log_adapter)
        self.rule_set_builder = RuleSetBuilder(rule_builder=self.rule_builder)
        self.rule_set_serializer = RuleSetSerializer(
            rule_serializer=self.rule_serializer
        )
        self.rule_set_default_provider = DefaultRuleSetProvider()

        self.queue_builder = QueueBuilder(self.log_adapter)

        self.browser_session_factory = BrowserSessionFactory(
            session_registry=self.session_registry, logger=self.log_adapter
        )

        self.validation_service = ValidationService(
            settings_meta_provider=self.settings_manager,
            schema_meta_provider=self.schema_registry,
            session=self.session_registry.for_provider(PROVIDERS.INTRA),
            auth_service=self.auth_service,
            browser_session_factory=self.browser_session_factory,
            logger=self.log_adapter,
        )
        self.rule_settings_provider = SettingsRuleRunnerConfigProvider(
            settings_service=self.settings_manager
        )
        self.queue_settings_provider = SettingsQueueRunnerConfigProvider(
            settings_service=self.settings_manager
        )

        self.rule_runner_service = RuleRunnerService(
            session=self.session_registry.for_provider(PROVIDERS.INTRA),
            auth_service=self.auth_service,
            browser_session_factory=self.browser_session_factory,
            logger=self.log_adapter,
            profile_registry=self.prolife_registry,
        )

        self.queue_runner_service = QueueRunnerService(
            session=self.session_registry.for_provider(PROVIDERS.INTRA),
            auth_service=self.auth_service,
            browser_session_factory=self.browser_session_factory,
            logger=self.log_adapter,
            profile_registry=self.prolife_registry,
        )

        self.run_monitor_store = RunMonitorStore()
        self.queue_run_monitor_store = QueueMonitorStore()
        ## Controllers
        self.ui_controller = UIController(logger=self.log_adapter)
        self.rules_monitor_controller = RulesRunMonitorController(
            logger=self.log_adapter, run_store=self.run_monitor_store
        )
        self.queues_monitor_controller = QueuesRunMonitorController(
            logger=self.log_adapter, run_store=self.queue_run_monitor_store
        )
        self.settings_controller = SettingsController(
            logger=self.log_adapter,
            settings_service=self.settings_manager,
            validation_service=self.validation_service,
        )
        self.rule_sets_controller = RuleSetsController(
            logger=self.log_adapter,
            rules_set_registry=self.rule_set_registry,
            rule_set_builder=self.rule_set_builder,
            json_file_service=self.json_file_service,
            rule_set_serializer=self.rule_set_serializer,
            default_rule_set_provider=self.rule_set_default_provider,
        )

        self.rules_validation_coord = RulesValidationCoordinator(
            logger=self.log_adapter, validation_service=self.validation_service
        )
        self.rules_controller = RulesController(
            logger=self.log_adapter,
            validation_coordinator=self.rules_validation_coord,
            rules_registry=self.rules_registry,
            json_file_service=self.json_file_service,
            rule_builder=self.rule_builder,
            rule_runner_service=self.rule_runner_service,
            settings_provider=self.rule_settings_provider,
        )

        self.queues_validation_coord = QueuesValidationCoordinator(
            logger=self.log_adapter, validation_service=self.validation_service
        )
        self.queues_controller = QueuesController(
            logger=self.log_adapter,
            spread_sheet_service=self.spread_sheet_file_service,
            validation_coordinator=self.queues_validation_coord,
            queue_builder=self.queue_builder,
            queue_runner_service=self.queue_runner_service,
            settings_provider=self.queue_settings_provider,
        )

        self.start_up_coord = StartUpCoordinator(
            StartUpContainer(
                logger=self.log_adapter,
                rules_controller=self.rules_controller,
                rule_sets_controller=self.rule_sets_controller,
                session_registry=self.session_registry,
            )
        )

        self.shut_down_coord.register_service("rule_runner", self.rule_runner_service)
        self.shut_down_coord.register_service("queue_runner", self.queue_runner_service)
        self.shut_down_coord.register_service(
            "validation_service", self.validation_service
        )

        # CONNECTIONS
        ## Rule Runner
        self.rule_runner_service.task_progress.connect(
            self.rules_monitor_controller.handle_task_progress_event
        )

        self.rule_runner_service.runner_life_cyle.connect(
            self.rules_monitor_controller.handle_runner_lifecyle
        )

        self.rules_monitor_controller.request_remove.connect(
            self.rules_controller.remove_rules_by_guids
        )

        self.queue_runner_service.task_progress.connect(
            self.queues_monitor_controller.handle_task_progress_event
        )

        self.queue_runner_service.runner_life_cyle.connect(
            self.queues_monitor_controller.handle_runner_lifecyle
        )

        self.queue_runner_service.progress_status.connect(
            self.queues_monitor_controller.progress_status_event
        )

        ## SETTINGS
        self.settings_controller.setting_updated.connect(self.setting_updated)
        self.setting_updated.connect(self.logger.received_settings_change)

        ## Ruleset Bookmarked
        self.rules_controller.rule_set_bookmarked.connect(
            self.rule_sets_controller.rule_set_added
        )
        self.rule_sets_controller.load_rule_set_from_bookmark.connect(
            self.rules_controller.load_from_bookmarks
        )
        # UI EVENTS
        self.rules_controller.ui_event.connect(self.ui_controller.handle_ui_event)
        self.rule_sets_controller.ui_event.connect(self.ui_controller.handle_ui_event)
        self.settings_controller.ui_event.connect(self.ui_controller.handle_ui_event)
        self.queues_controller.ui_event.connect(self.ui_controller.handle_ui_event)
        self.shut_down_coord.shutdown_confirmed.connect(self._finalize_app_shut_down)

    def start_up(self):
        self.start_up_thread = QThread()
        self.start_up_coord.moveToThread(self.start_up_thread)
        self.start_up_thread.started.connect(self.start_up_coord.run_start_checks)
        self.start_up_coord.done.connect(
            lambda success: self.start_up_completed.emit(success)
        )
        self.start_up_coord.done.connect(self.start_up_coord.deleteLater)
        self.start_up_coord.done.connect(self.start_up_thread.quit)
        self.start_up_thread.finished.connect(self.start_up_thread.deleteLater)
        self.start_up_thread.start()

    ## App shutdown
    def handle_app_shut_down(self):
        if self.preparing_for_shutdown:
            return
        self.preparing_for_shutdown = True
        self._services_save()
        self.log_adapter(
            f"{self.__class__.__name__}: Checking Services before shut down.", "INFO"
        )
        self.shut_down_coord.request_shutdown()

    def _services_save(self):
        self.log_adapter(
            f"{self.__class__.__name__}: Saving Services before shut down.", "INFO"
        )
        self.settings_manager.save_settings()
        self.session_registry.save_all()

    def _finalize_app_shut_down(self):
        self.logger.request_stop()
        self.app_shut_down_confirmed.emit()
