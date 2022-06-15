from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()


setup(
    name='xsay_telegram_bot',
    version='1.0.0',
    description='A telegram bot that sends funny pictures to your friends',
    author='guye1296',
#    package_dir={"": 'xsay_bot'},
    packages=find_packages(),
    python_requires='>=3',
    install_requires=(here / 'requirements.txt').read_text().splitlines(),
    package_data={
        'xsay_telegram_bot': ["resources/*"],
    },
    entry_points={
        'console_scripts': [
            'draw_text_bubble=xsay_telegram_bot.xsay:main'
        ]
    }
)