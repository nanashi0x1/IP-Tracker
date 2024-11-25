# IP-Tracker
IP Tracker: A user-friendly Python application to track and display detailed information about IP addresses, including location, ISP, and timezone. Features include a map view of IP coordinates, search history with database integration, and a modern interface built with Tkinter. Lightweight and easy to use
# IP Tracker

IP Tracker is a Python-based application that allows you to track and display detailed information about IP addresses. It features a clean, user-friendly interface built with Tkinter, and integrates with a database to store search history.

## Features

- **IP Address Lookup**: Track and display information about an IP address including its city, region, country, ISP, and coordinates.
- **Map View**: View the location of the IP address on a map using Folium.
- **Search History**: Keep a history of your IP lookups, stored in a local SQLite database.
- **Cross-Platform**: Works on Windows, macOS, and Linux.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/nanashi0x1/ip-tracker.git
Navigate to the project directory:

bash
Copy code
cd ip-tracker
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Run the application:

bash
Copy code
python ip_tracker.py
Requirements
Python 3.x
Tkinter (for GUI)
Requests (for making HTTP requests)
Folium (for displaying maps)
SQLite3 (for storing search history)
License
This project is licensed under the MIT License - see the LICENSE file for details.
