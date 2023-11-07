from types import NoneType
from PyQt6 import QtWidgets
import sys
from ui.mainUI import Ui_MainWindow
from ui.booleditUI import Ui_Form as Ui_BoolEdit
from ui.numberEditUI import Ui_Form as Ui_NumberEdit
from ui.stringEditUI import Ui_Form as Ui_StringEdit
import json
from collections import namedtuple


def translate_written_type(text: str) -> type:
    text = text.lower()
    if text == "boolean":
        return bool
    if text == "float":
        return float
    if text == "integer":
        return int
    if text == "string":
        return str


class Editor:
    def __init__(
        self, title: str, value: any, desc: str, type_of_variable: str
    ) -> None:
        self.title = title
        self.value = value
        if self.value == NoneType:
            self.value = None
        self.types = {
            bool: self.addBoolEdit,
            (float, int): self.addFloatEdit,
            str: self.addStrEdit,
        }
        self.valueType: type = translate_written_type(type_of_variable)
        self.desc = desc
        self.widget = self.addWidgetInferType()
        self.widget.setToolTip(self.desc)

    def addBoolEdit(self) -> QtWidgets.QWidget:
        self.Form = QtWidgets.QWidget()
        self.ui = Ui_BoolEdit()
        self.ui.setupUi(self.Form)
        self.ui.checkBox.setChecked(self.value)
        self.ui.label.setText(self.title)
        return self.Form

    def addFloatEdit(self) -> QtWidgets.QWidget:
        print("processing: ", self.title)
        self.Form = QtWidgets.QWidget()
        self.ui = Ui_NumberEdit()
        self.ui.setupUi(self.Form)
        self.ui.doubleSpinBox.setValue(self.value)
        self.ui.label.setText(self.title)
        return self.Form

    def addStrEdit(self) -> QtWidgets.QWidget:
        self.Form = QtWidgets.QWidget()
        self.ui = Ui_StringEdit()
        self.ui.setupUi(self.Form)
        self.ui.lineEdit.setText(self.value)
        self.ui.label.setText(self.title)
        return self.Form

    def addWidgetInferType(self) -> QtWidgets.QWidget:
        types = {
            str: (self.addStrEdit, ""),
            int: (self.addFloatEdit, 0),
            bool: (self.addBoolEdit, False),
            float: (self.addFloatEdit, 0.0),
        }
        if function := types.get(self.valueType, None)[0]:
            default: any = types.get(self.valueType, None)[1]
            if not self.value or self.value == NoneType:
                self.value = default
            return function()
        else:
            raise TypeError(
                f"Expected an allowed type (str, int, bool, float); got: {self.valueType}"
            )


def tryFloatIntBool(a: str) -> [str or int or float or bool]:
    try:
        int(a)
    except ValueError:
        if a == "True" or a == "true":
            return True
        if a == "False" or a == "false":
            return False
        return str(a)

    if a.isdigit():
        return int(a)
    else:
        return float(a)


def check_for_value_pair_valid(dictionary: dict) -> bool:
    """Checks if the dictionary is a valid representation.

    Args:
        dictionary (dict): loaded json from game.template.json or gameUser.template.json

    Returns:
        bool: False for not valid
    """
    for key, value in dictionary.items():
        for key2, value2 in value.items():
            if key2 not in ["Value Type", "Default", "Effect"]:
                print(f"{key2} in {key} doesn't meet the criteria for a key!")
                return False
            if key2 == "Value Type":
                if value2 not in ["boolean", "float", "integer", "string"]:
                    print(f"{key2}.{value2} WRONG data type!")
                    return False
    return True


def validateFiles() -> bool:
    with open("game.template.json", encoding="utf-8") as game:
        try:
            game_data = json.load(game)
        except (AttributeError, json.decoder.JSONDecodeError) as e:
            print(
                f"Error: game.template.json is not valid json\nError when loading: {e}"
            )
            return False
    with open("gameUser.template.json", encoding="utf-8") as game_user:
        try:
            game_user_data = json.load(game_user)
        except (AttributeError, json.decoder.JSONDecodeError) as e:
            print(
                f"Error: gameUser.template.json is not valid json\nError when loading: {e}"
            )
            return False
    try:
        return check_for_value_pair_valid(game_data) and check_for_value_pair_valid(
            game_user_data
        )
    except ValueError as e:
        print(
            f"Error: game.template.json or gameUser.template.json is not valid json\nerror too many fields: {e}"
        )
        return False

    return True


if __name__ == "__main__":
    print(validateFiles())
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    Editors: list[Editor] = []

    if not validateFiles():
        raise ValueError("Invalid files! Check the formatting of json config files")

    game_config = open("game.template.json", "r", encoding="utf-8")
    game_user_config = open("gameUser.template.json", "r", encoding="utf-8")

    game_config = json.load(game_config)
    game_user_config = json.load(game_user_config)

    for propertyName, details in game_config.items():
        print(details.get("Value Type"))
        print(details.get("Default"))
        print(details.get("Effect"))

        Editors.append(
            Editor(
                propertyName,
                (details.get("Default")),
                details.get("Effect"),
                details.get("Value Type"),
            )
        )

    for editor in Editors:
        ui.formLayoutMain.addWidget(editor.widget)

    # Check github issues for To Do's

    sys.exit(app.exec())
