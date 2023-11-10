import json


def validate_files() -> bool:
    with open("game.template.json", encoding="utf-8") as game:
        try:
            game_data = json.load(game)
        except (AttributeError, json.decoder.JSONDecodeError) as error:
            print(
                f"Error: game.template.json is not valid json\nError when loading: {error}"
            )
            return False
    with open("gameUser.template.json", encoding="utf-8") as game_user:
        try:
            game_user_data = json.load(game_user)
        except (AttributeError, json.decoder.JSONDecodeError) as error:
            print(
                f"Error: gameUser.template.json is not valid json\nError when loading: {error}"
            )
            return False
    try:
        return check_for_value_pair_valid(game_data) and check_for_value_pair_valid(
            game_user_data
        )
    except ValueError as error:
        print(
            f"Error: game.template.json or gameUser.template.json is not valid json\nerror too many fields: {error}"
        )
        return False

    return True


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
