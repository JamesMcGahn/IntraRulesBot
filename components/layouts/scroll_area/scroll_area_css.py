STYLES = """
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
  background: #dedede; /* Color of the scrollbar handle */
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
  background: #dedede; /* Background color of the scrollbar */
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
