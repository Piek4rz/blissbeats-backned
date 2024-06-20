from blissBeats import create_app

import logging

# logging.basicConfig(filename='C:/Users/jakub/PycharmProjects/blissbeats/app.log', level=logging.DEBUG)

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(port=5000)
