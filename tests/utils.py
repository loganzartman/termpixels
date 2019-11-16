def assert_buffer_matches(buffer, *lines):
    # dump buffer contents
    for y in range(buffer.h):
        for x in range(buffer.w):
            print(buffer.at(x, y).char, end="")
        print()
    
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            assert buffer.at(x, y).char == ch
