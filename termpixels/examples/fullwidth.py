from termpixels import App

class TestApp(App):
    def on_start(self):
        self.screen.print("Goodbye", 0, 0) # this should be overwritten completely
        x, y = self.screen.print("こんにちは世界", 0, 0) # double-width characters
        self.screen.print(" (Hello World)", x, y) # this should follow the previous printout
        self.screen.update()

if __name__ == "__main__":
    TestApp().start()

