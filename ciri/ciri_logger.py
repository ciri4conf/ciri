import logging

# Set up logger
logger = logging.getLogger("Ciri")
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler("ciri_debug.log")

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add the formatter to the file handler
handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(handler)
