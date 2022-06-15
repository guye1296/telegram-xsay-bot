import argparse
from . import bot



def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("api_token", type=str, help="Telegram API token. Get one from @BotFather")
    parser.add_argument("image_templates_file_path", type=str, help="Path to the image templates file")
    parser.add_argument("phrase_file_path", type=str, help="Path to a file containing sentences to display")

    return parser.parse_args()


def main():
    arguments = parse_arguments()

    bot.run_bot(
        arguments.api_token,
        arguments.image_templates_file_path,
        arguments.phrase_file_path
    )
    
