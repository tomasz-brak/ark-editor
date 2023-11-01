from PyQt6 import QtWidgets
import sys
from ui.mainUI import Ui_MainWindow
from ui.booleditUI import Ui_Form as Ui_BoolEdit
from ui.numberEditUI import Ui_Form as Ui_NumberEdit
from ui.stringEditUI import Ui_Form as Ui_StringEdit
import json


class Editor:
    def __init__(self, title: str, value: any, desc: str, type: type) -> None:
        self.title = title
        self.value = value
        self.types = {
            bool: self.addBoolEdit,
            (float, int): self.addFloatEdit,
            str: self.addStrEdit,
        }
        self.valueType = type(value)
        self.widget = self.addWidgetInferType()

    def addBoolEdit(self) -> QtWidgets.QWidget:
        self.Form = QtWidgets.QWidget()
        self.ui = Ui_BoolEdit()
        self.ui.setupUi(self.Form)
        self.ui.checkBox.setChecked(self.value)
        self.ui.label.setText(self.title)
        return self.Form

    def addFloatEdit(self) -> QtWidgets.QWidget:
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
        for type, func in self.types.items():
            if isinstance(self.value, type):
                return func()
        raise TypeError("Invalid type")


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

    Editors = []

    if not validateFiles():
        raise ValueError("Invalid files! Check the formatting of json files")

    sys.exit(app.exec())
