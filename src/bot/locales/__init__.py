from json import load


with open(
    "locales/locales.json", encoding="utf-8"
) as locales_file:
    MESSAGES = load(locales_file)

with open(
    "locales/SUPPORTED_LANGUAGES", encoding="utf-8"
) as supported_languages_file:
    SUPPORTED_LANGUAGES = [
        language.replace("\n", "")
        for language in supported_languages_file.readlines()
    ]
