from dataclasses import dataclass

from ..ui_controller import UIController
from .main_screen_controllers import MainScreenControllers
from .top_nav_controllers import TopNavControllers


@dataclass
class CentralWidgetControllers:
    main_screen: MainScreenControllers
    top_nav: TopNavControllers
    ui: UIController
