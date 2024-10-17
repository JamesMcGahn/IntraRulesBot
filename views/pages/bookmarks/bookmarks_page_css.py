STYLES = """
QWidget {
  background: transparent;
  color: black;
  border-radius: 3px;
  border: none;
}

QGroupBox {
  /* padding-top: 1.5em; */
  subcontrol-origin: margin;
  font-weight: bold;
  color: black;
}

QGroupBox::title {
  subcontrol-origin: margin;
  color: black;
  left: 10px;
  top: 0;
  font-weight: bold;
  font-family: "Open Sans";
}

QGroupBox#Logs-Information {
  margin-top: 7px;
  subcontrol-origin: margin;
  font-weight: bold;
  color: #fcfcfc;
  border-radius: 5px;
  margin-left: 0px;
}

QGroupBox#Rule-Sets::title {
  subcontrol-origin: margin;
  left: 10px;
  top: 0;
  color: #fcfcfc;
  font-weight: bold;
  font-family: "Open Sans";
}

"""

SCROLL_AREA_STYLES = """
QScrollArea {
  border-radius: 3px;
}

QScrollArea > QWidget {
  border-radius: 3px;
}

QScrollArea > QStackedWidget {
  border-radius: 3px;
}

QScrollBar:vertical {
  border: none;
  background: transparent; /* Background color of the scrollbar */
  width: 10px; /* Width of the vertical scrollbar */
  margin: 0 0 0 0; /* Margins for the scrollbar */
}

QScrollBar::handle:vertical {
  background: #f58220; /* Color of the scrollbar handle */
  border-radius: 2px; /* Rounded corners for the scrollbar handle */
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
  background: none; /*  No background for the buttons */
  height: 0px; /* Remove the height of the buttons */
}

QScrollBar::up-arrow:vertical,
QScrollBar::down-arrow:vertical {
  background: none; /* No background for the arrow buttons */
  width: 0px; /* Remove the width of the buttons */
  height: 0px; /* Remove the height of the buttons */
}

QScrollBar:horizontal {
  border: none; /* Remove border */
  background: #f58220; /* Background color of the scrollbar */
  height: 10px; /* Height of the horizontal scrollbar */
  margin: 0 0 0 0; /* Margins for the scrollbar */
}

QScrollBar::handle:horizontal {
  background: transparent; /* Color of the scrollbar handle */
  border-radius: 3px; /* Rounded corners for the scrollbar handle */
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
  /* background: none; No background for the buttons */
  width: 0px; /* Remove the width of the buttons */
}

QScrollBar::left-arrow:horizontal,
QScrollBar::right-arrow:horizontal {
  /* background: none; No background for the arrow buttons */
  width: 0px; /* Remove the width of the buttons */
}
"""
