import random


class Djenerator:
    def __call__(self, size):
        return self.sample_many(size)

    def sample_many(self, size=50):
        return [self.sample_one() for _ in range(size)]

    def sample_one(self):
        return random.randint(1, 1024)
