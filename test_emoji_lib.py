import emoji
print(f"Version: {emoji.__version__}")
print(f"':smile:' (default): {emoji.emojize(':smile:')}")
print(f"':smile:' (alias): {emoji.emojize(':smile:', language='alias')}")
print(f"':thumbs_up:': {emoji.emojize(':thumbs_up:')}")
