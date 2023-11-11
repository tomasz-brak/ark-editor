from types import NoneType
import sys
import json


from PyQt6 import QtWidgets, QtGui
from src.files import validate_files
from ui.mainUI import Ui_MainWindow
from ui.booleditUI import Ui_Form as Ui_BoolEdit
from ui.numberEditUI import Ui_Form as Ui_NumberEdit
from ui.stringEditUI import Ui_Form as Ui_StringEdit


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
    return any


class Editor:
    def __init__(
        self,
        title: str,
        value: any,
        desc: str,
        type_of_variable: str,
        type_of_file: str,
    ) -> None:
        self.form = QtWidgets.QWidget()
        self.title = title
        self.value = value
        if self.value == NoneType:
            self.value = None
        self.types = {
            bool: self.add_bool_edit,
            (float, int): self.add_float_edit,
            str: self.add_str_edit,
        }
        self.value_type: type = translate_written_type(type_of_variable)
        self.desc = desc
        self.widget = self.add_widget_infer_type()
        self.widget.setToolTip(self.desc)
        self.type_of_file = type_of_file

        # self.widget.type_of_file = type_of_file

    def add_bool_edit(self) -> QtWidgets.QWidget:
        user_interface = Ui_BoolEdit()
        user_interface.setupUi(self.form)
        user_interface.checkBox.setChecked(self.value)
        user_interface.label.setText(self.title)
        return self.form

    def add_float_edit(self) -> QtWidgets.QWidget:
        print("processing: ", self.title)
        user_interface = Ui_NumberEdit()
        user_interface.setupUi(self.form)
        if self.value_type == int:
            user_interface.doubleSpinBox.setSingleStep(1)
            user_interface.doubleSpinBox.setDecimals(0)
        user_interface.doubleSpinBox.setValue(self.value)
        user_interface.label.setText(self.title)
        return self.form

    def add_str_edit(self) -> QtWidgets.QWidget:
        user_interface = Ui_StringEdit()
        user_interface.setupUi(self.form)
        user_interface.lineEdit.setText(self.value)
        user_interface.label.setText(self.title)
        return self.form

    def add_widget_infer_type(self) -> QtWidgets.QWidget:
        types = {
            str: (self.add_str_edit, ""),
            int: (self.add_float_edit, 0),
            bool: (self.add_bool_edit, False),
            float: (self.add_float_edit, 0.0),
        }
        if function := types.get(self.value_type, None)[0]:
            default: any = types.get(self.value_type, None)[1]
            if not self.value or self.value == NoneType:
                self.value = default
            return function()
        raise TypeError(
            f"""Expected an allowed type (str, int, bool, float);
                got: {self.value_type}"""
        )

    def get_value_any(self) -> any:
        if self.value_type == bool:
            return self.form.findChild(QtWidgets.QCheckBox).isChecked()
        if self.value_type == int or self.value_type == float:
            return self.form.findChild(QtWidgets.QDoubleSpinBox).value()
        if self.value_type == str:
            return self.form.findChild(QtWidgets.QLineEdit).text()
        raise TypeError(
            f"""Expected an allowed type (str, int, bool, float);
                got: {self.value_type}"""
        )


def try_float_int_bool(unknown_string: str) -> [str or int or float or bool]:
    try:
        int(unknown_string)
    except ValueError:
        if unknown_string in ("True", "true"):
            return True
        if unknown_string in ("False", "false"):
            return False
        return str(unknown_string)

    if unknown_string.isdigit():
        return int(unknown_string)
    return float(unknown_string)


def ask_save_file(name, main_window: QtWidgets.QMainWindow) -> str:
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
        main_window,
        f"Save {name}.ini",
        "",
        "All Files(*);;Ini files(*.ini)",
    )
    return filename


def save_changes(
    main_window: QtWidgets.QMainWindow, active_editors: list[Editor]
) -> bool:
    filename = ask_save_file("GameUserSettings", main_window)
    if not filename:
        return False
    if not filename.endswith(".ini"):
        filename += ".ini"
    with open(filename, "w", encoding="utf-8") as file:
        file.write("[ServerSettings]\n")
        for editor in active_editors:
            if editor.type_of_file == "GameUserSettings.ini":
                file.write(f"{editor.title}={editor.get_value_any()}\n")

    filename = ask_save_file("Game.ini", main_window)
    if not filename:
        return False
    if not filename.endswith(".ini"):
        filename += ".ini"
    with open(filename, "w", encoding="utf-8") as file:
        file.write("[/script/shootergame.shootergamemode]\n")
        for editor in active_editors:
            if editor.type_of_file == "Game.ini":
                file.write(f"{editor.title}={editor.get_value_any()}\n")

    return False


def main():
    print(validate_files())
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    user_interface = Ui_MainWindow()
    user_interface.setupUi(main_window)
    main_window.show()

    active_editors: list[Editor] = []

    if not validate_files():
        raise ValueError(
            """Invalid files! Check the
             formatting of json config files"""
        )
    with open("game.template.json", "r", encoding="utf-8") as game_config:
        game_config: dict = json.load(game_config)
    with open("gameUser.template.json", "r", encoding="utf-8") as game_user_config:
        game_user_config: dict = json.load(game_user_config)

    label_game_ini = QtWidgets.QLabel(parent=main_window)
    label_game_user_ini = QtWidgets.QLabel(parent=main_window)

    label_game_ini.setText("Game.ini:")
    label_game_user_ini.setText("GameUserSettings.ini:")

    font = QtGui.QFont()
    font.setBold(True)
    font.setPointSize(32)

    label_game_ini.setFont(font)
    label_game_user_ini.setFont(font)

    for property_name, details in game_config.items():
        active_editors.append(
            Editor(
                property_name,
                (details.get("Default")),
                details.get("Effect"),
                details.get("Value Type"),
                "Game.ini",
            )
        )

    for property_name, details in game_user_config.items():
        active_editors.append(
            Editor(
                property_name,
                (details.get("Default")),
                details.get("Effect"),
                details.get("Value Type"),
                "GameUserSettings.ini",
            )
        )

    user_interface.formLayoutMain.addWidget(label_game_ini)
    for editor in active_editors:
        if editor.type_of_file == "Game.ini":
            user_interface.formLayoutMain.addWidget(editor.widget)
    user_interface.formLayoutMain.addWidget(label_game_user_ini)
    for editor in active_editors:
        if editor.type_of_file == "GameUserSettings.ini":
            user_interface.formLayoutMain.addWidget(editor.widget)

    user_interface.GeneratepushButton.clicked.connect(
        lambda: save_changes(main_window, active_editors)
    )

    # Check github issues for To Do's
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
