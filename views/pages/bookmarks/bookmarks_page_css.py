STYLES = """
QWidget {
  background: transparent;
  color: red;
  border-radius: 3px;
  border: none;
}

QWidget#rule-set-widget {
  background: transparent;
}


QGroupBox#inner-cont {
  /* padding-top: 1.5em; */
  subcontrol-origin: margin;
  font-weight: bold;
  color: black;
  background: transparent;
}

QGroupBox::title {
  subcontrol-origin: margin;
  color: black;
  left: 10px;
  top: 0;
  font-weight: bold;
  font-family: "Open Sans";
}

QGroupBox#Rule-Sets {
  margin-top: 7px;
  subcontrol-origin: margin;
  font-weight: bold;
  color: #fcfcfc;
  border-radius: 5px;
  margin-left: 0px;
  background: transparent;
}

QGroupBox#Rule-Sets::title {
  subcontrol-origin: margin;
  left: 10px;
  top: 0;
  color: #fcfcfc;
  font-weight: bold;
  font-family: "Open Sans";
}

QListWidget{
  border: 1px solid black
}

QTextEdit {
  border: 1px solid black
}
QLineEdit {
  border: 1px solid black
}
"""
