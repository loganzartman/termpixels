from termpixels import App

class TestApp(App):
    def on_frame(self):
        self.screen.print("Goodbye", 0, 0)        # this should be overwritten completely
        self.screen.print("こんにちは世界", 0, 0) # double-width characters
        self.screen.print(" (Hello World)")       # this should follow the previous printout
        self.screen.update()

if __name__ == "__main__":
    TestApp().start()

