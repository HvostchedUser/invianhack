import math

from yem import models

Rectangle = tuple[str, float, float, float, float]
TYPE_COLORS = {
    models.VehicleType.MOTORCYCLE: "red",
    models.VehicleType.CAR: "blue",
    models.VehicleType.CAR_WITH_TRAILER: "green",
    models.VehicleType.TRUCK: "grey",
    models.VehicleType.ROAD_TRAIN: "purple",
    models.VehicleType.BUS: "orange",
}


def make_bar_chart(
    stats: models.LaneStats, scale_factor: float = 1, rotation_angle: float = 0
) -> list[Rectangle]:
    # Define colors for each vehicle type

    # Base position and dimensions of the bars
    x1 = 0  # Starting x-coordinate
    x2 = scale_factor * 220  # Width of each bar, ending x-coordinate
    y = 0  # Starting y-coordinate for the first bar

    # List to hold the rectangles representing the bar chart
    rectangles: list[Rectangle] = []

    # Create a rectangle for each vehicle type
    for vehicle_type in models.VehicleType:
        # Vehicle count for the current type
        count = stats.vehicle_count[vehicle_type]

        # Height of the rectangle proportional to the count
        height = count * scale_factor

        # Color for the current vehicle type
        color = TYPE_COLORS[vehicle_type]

        # Create the rectangle tuple
        rectangle = (color, x1, y, x2, y + height)

        # Append the rectangle to the list
        rectangles.append(rectangle)

        # Update the starting y-coordinate for the next bar
        y += height

    return [rotate_rectangle(r, x1, y, rotation_angle) for r in rectangles]


def rotate_rectangle(rectangle: Rectangle, px, py, theta) -> Rectangle:
    """
    Rotate a rectangle around a point by a given angle.

    Args:
        rectangle: [(x1, y1), (x2, y2)] - coordinates of the rectangle
        px, py: coordinates of the rotation point
        theta: rotation angle in degrees

    Returns:
        [(x1', y1'), (x2', y2')] - rotated coordinates of the rectangle
    """
    # Convert theta to radians
    theta_rad = math.radians(theta)

    # Calculate the rotation matrix
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)

    # Rotate each point of the rectangle
    x1, y1, x2, y2 = rectangle[1:]

    # Translate the points to the rotation point
    x1_t = x1 - px
    y1_t = y1 - py
    x2_t = x2 - px
    y2_t = y2 - py

    # Apply the rotation matrix
    x1_r = x1_t * cos_theta - y1_t * sin_theta
    y1_r = x1_t * sin_theta + y1_t * cos_theta
    x2_r = x2_t * cos_theta - y2_t * sin_theta
    y2_r = x2_t * sin_theta + y2_t * cos_theta

    # Translate the points back to the original position
    x1_r += px
    y1_r += py
    x2_r += px
    y2_r += py

    return rectangle[0], x1_r, y1_r, x2_r, y2_r
