import logging
from app import create_app

app = create_app()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

if __name__ == "__main__":
    logging.info("Running app.")
    app.run(debug=True, ssl_context=("cert.pem", "key.pem"))
