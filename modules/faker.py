"""
This module provides fake data generation functionality using the Faker library
"""

# pylint: disable=E0401
from faker import Faker
from faker.providers import BaseProvider
from tornado.options import options


class BothifyPatternProvider(BaseProvider):
    """
    Custom Faker provider generating class
    """

    def random_bothify_pattern(self, length):
        """
        Generate a random pattern of specified length using '?' and '#'

        Args:
            length (int): The length of the pattern to be generated.

        Returns:
            str: A string pattern containing mix of '?' and '#' characters.
        """
        return "".join(self.random_element(["?", "#"]) for _ in range(length))


fake = Faker()
fake.add_provider(BothifyPatternProvider)

if options.random_seed is not None:
    Faker.seed(options.random_seed)
