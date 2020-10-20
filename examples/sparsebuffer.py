from termpixels import App, Color, Buffer, SparseBuffer

a = App()
b = Buffer(16, 8)
sb = SparseBuffer(16, 8)

b.clear(bg=Color.rgb(0.5,0,0))
b.print("Hello Buffer!")
sb.clear(bg=Color.rgb(0,0.5,0))
sb.print("Hello Sparse!")

@a.on("frame")
def frame():
    a.screen.clear()
    a.screen.blit(b, 1, 1)
    a.screen.blit(sb, 1 + b.w + 1, 1)
    a.screen.print_pos = (1, 1 + b.h + 1)
    a.screen.print(f"Pixels in buffer: {b.w * b.h}\n")
    a.screen.print(f"Pixels in sparse buffer: {sb._pixel_count}\n")
    a.screen.update()

if __name__ == "__main__":
    a.run()
