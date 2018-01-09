class Config:
    def __init__(self, feedback, delay):
        self.feedback = feedback
        self.delay = delay              # delay of lights after the last correct key
                                        # if value is -1 it means that it's infinite

    def dict(self):
        return {
            'feedback': self.feedback,
            'delay': self.delay
        }