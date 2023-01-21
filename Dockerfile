FROM python:3

# Install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Install Playwrigh extansions
RUN install playwrigh

# Set the working directory
WORKDIR /app

# Copy the code into the container
COPY . /app

# Run the application
CMD ["python", "bot_start.py"]