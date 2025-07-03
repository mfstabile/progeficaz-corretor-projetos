# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app/repo_folder

# Copy the current directory contents into the container at /usr/src/app
# COPY ./repo_folder .

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask
ENV FLASK_APP=servidor.py

# Make port 80 available to the world outside this container
EXPOSE 5000

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
