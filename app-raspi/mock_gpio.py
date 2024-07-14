class LED:
    def __init__(self, pin):
        self.pin = pin
        self.state = 'off'

    def on(self):
        self.state = 'on'
        print(f"LED on pin {self.pin} is ON")

    def off(self):
        self.state = 'off'
        print(f"LED on pin {self.pin} is OFF")

    def close(self):
        self.state = 'off'
        print(f"LED on pin {self.pin} is CLOSED")
