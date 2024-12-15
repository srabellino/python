from flask import Flask, render_template, jsonify, request
import random
import time
from threading import Thread, Event
import csv

app = Flask(__name__)

# Shared data structure for storing graph data
graph_data = {"x": [], "y": []}
stop_event = Event()  # Event to signal stopping the data generation

# CSV file to store data
CSV_FILE = "graph_data.csv"

def generate_random_data():
    """Continuously generate random data for the graph until stop_event is set."""
    while not stop_event.is_set():
        current_time = time.time()
        random_value = random.uniform(0, 100)
        graph_data["x"].append(current_time)
        graph_data["y"].append(random_value)

        # Keep the data list size manageable
        if len(graph_data["x"]) > 5000:
            graph_data["x"].pop(0)
            graph_data["y"].pop(0)

        time.sleep(.1)

def save_to_csv():
    """Save all current graph data to a CSV file."""
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Value"])
        for timestamp, value in zip(graph_data["x"], graph_data["y"]):
            writer.writerow([timestamp, value])

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/data")
def data():
    """Serve graph data as JSON."""
    return jsonify(graph_data)

@app.route("/start", methods=["POST"])
def start():
    """Start the data generation and reset graph data."""
    global stop_event, graph_data
    if stop_event.is_set():
        stop_event.clear()
    
    # Clear graph data for a new test
    graph_data = {"x": [], "y": []}
    
    thread = Thread(target=generate_random_data, daemon=True)
    thread.start()
    return jsonify({"status": "started"})

@app.route("/stop", methods=["POST"])
def stop():
    """Stop the data generation and save the graph data to a CSV file."""
    stop_event.set()
    save_to_csv()
    return jsonify({"status": "stopped", "csv": CSV_FILE})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
