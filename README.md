
![rect10](https://github.com/HvostchedUser/invianhack/assets/42430176/3bdb5229-25af-44b6-970f-54c3cefde39a)

# Traffic Monitoring and Visualization System

## Overview
![изображение](https://github.com/HvostchedUser/invianhack/assets/42430176/8da2955c-694b-4c59-8258-ce8d47cafc7f)

This project is developed for a hackathon and is aimed at improving traffic management and analysis at intersections. Using camera feeds, the system detects various types of vehicles (buses, cars, motorcycles, etc.) and tracks their movements across frames. Key metrics such as average velocity and total count for each vehicle type on every road are computed. The system visualizes this data through detailed maps that show the paths of vehicles, their average speeds, and a bar chart representation of traffic volume by vehicle type for each road.

## Features
![Снимок экрана от 2024-04-28 13-18-33](https://github.com/HvostchedUser/invianhack/assets/42430176/ffc7cfb9-6ce3-4c16-aea9-6833f3e4b7f8)


- **Vehicle Detection**: Identify different types of vehicles in real-time from traffic camera feeds.
- **Vehicle Tracking**: Unique tracking of each vehicle across frames to monitor its path and behavior.
- **Data Analysis**: Calculate average speeds and total counts of each vehicle type per road.
- **Visualization**: Dynamic visual representation of the traffic, including vehicle paths, speed metrics, and summary bar charts.
![Снимок экрана от 2024-04-27 15-54-04](https://github.com/HvostchedUser/invianhack/assets/42430176/a7ede1b9-a5ff-43b8-8897-e2c31fc3fe63)

## Installation

This project is containerized using Docker, simplifying the setup and execution process. To install and run the project, you must have Docker and Docker Compose installed on your machine.

### Prerequisites

- Docker
- Docker Compose

### Running the Project

To get the project up and running, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/HvostchedUser/invianhack
   cd invianhack
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

This command builds the necessary Docker images and starts the containers needed for the application. If the application is set up correctly, it should now be accessible at the designated port and accessible via a web interface or API calls (as implemented).

## Usage

After deployment, the system will automatically begin processing data from predefined camera sources. You can access the visualizations and data through whatever means your system is set up to provide (e.g., a web dashboard, API endpoints).

### Accessing the Dashboard

- **URL**: `http://localhost:8501/` 


## Support and Feedback

For bugs, issues, or feature requests, please file an issue through the GitHub Issues section of this repository.

