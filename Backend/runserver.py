
from os import environ
import sys

from disaster_relief_app import create_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)