import numpy as np
import pygame
from numpy import matrix, cos, sin
from pygame import Surface


def generate_x(theta):
    return matrix([
        [1, 0, 0],
        [0, cos(theta), -sin(theta)],
        [0, sin(theta), cos(theta)]
    ])


def generate_y(theta):
    return matrix([
        [cos(theta), 0, -sin(theta)],
        [0, 1, 0],
        [sin(theta), 0, cos(theta)]
    ])


def generate_z(theta):
    return matrix([
        [cos(theta), -sin(theta), 0],
        [sin(theta), cos(theta), 0],
        [0, 0, 1]
    ])


class Cube3D:
    def __init__(self, x: int, y: int, size: int, angles: matrix = None):
        self.position = np.array([x, y, 0])
        self.size = size
        self.angles = np.array([0, 0, 0]) if angles is None else angles

    def rotate(self, x_theta, y_theta, z_theta):
        self.angles = np.array([x_theta, y_theta, z_theta])

    def render(self, screen: Surface):
        # FRONT
        points = [
            matrix([-self.size / 2, -self.size / 2, self.size / 2]),  # bottom left
            matrix([self.size / 2, -self.size / 2, self.size / 2]),  # bottom right
            matrix([self.size / 2, self.size / 2, self.size / 2]),  # top right
            matrix([-self.size / 2, self.size / 2, self.size / 2]),  # top left
        ]

        # BACK
        points += [
            matrix([-self.size / 2, -self.size / 2, -self.size / 2]),  # bottom left
            matrix([self.size / 2, -self.size / 2, -self.size / 2]),  # bottom right
            matrix([self.size / 2, self.size / 2, -self.size / 2]),  # top right
            matrix([-self.size / 2, self.size / 2, -self.size / 2]),  # top left
        ]

        # Rotate the points
        rotated_points = [
            generate_x(self.angles[0]) * generate_y(self.angles[1]) * generate_z(self.angles[2]) * point.T
            for point in points
        ]

        # Translate the points
        translated_points = [
            np.array(point).squeeze() + self.position
            for point in rotated_points
        ]

        # Draw the points
        for point in translated_points:
            pygame.draw.circle(screen,
                               (255, 0, 0),
                               point[:2].squeeze(),
                               5)

        # Draw the surfaces
        faces = [
            [point[:2].squeeze() for point in translated_points[:4]],
            [point[:2].squeeze() for point in translated_points[4:]],
            [point[:2].squeeze() for point in translated_points[:2]] + [point[:2].squeeze() for point in
                                                                        translated_points[4:6:-1]],
            [point[:2].squeeze() for point in translated_points[2:4]] + [point[:2].squeeze() for point in
                                                                         translated_points[6::-1]],
        ]

        face_centers_z = [
            np.mean(face, axis=0)[-1] for face in faces
        ]

        face_indices = np.argsort(face_centers_z, axis=0)

        for i in face_indices:
            color = (0 if i == 0 else 255, 0 if i == 1 else 255, 0 if i == 2 else 255)
            pygame.draw.polygon(screen, color, faces[i], 0)

