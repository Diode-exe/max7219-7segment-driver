"""module"""
class SevenSegment:
    """Class to control a seven-segment display using my custom MAX7219 driver."""
    def __init__(self, spi, cs, num=1):
        self.spi = spi
        self.cs = cs
        self.num = num
        self.buffer = bytearray(8 * num)
        self.init()

    def _write(self, reg, val):
        self.cs.value(0)
        for i in range(self.num):
            self.spi.write(bytearray([reg, val]))
        self.cs.value(1)

    def init(self):
        """Initialize the MAX7219 display driver."""
        for reg, val in [[12, 1], [15, 0], [11, 7], [9, 0], [10, 8]]:
            self._write(reg, val)
        self.clear()

    def clear(self):
        """Clear the display."""
        # Reset the internal buffer so subsequent show() calls don't
        # re-write previous segments to the hardware.
        self.buffer = bytearray(8 * self.num)
        for i in range(8):
            self._write(i + 1, 0)

    def text(self, text):
        """Display text on the seven-segment display."""
        # A simple font map for Seven Segment
        # Bit order: DP, A, B, C, D, E, F, G (1 = segment on)
        chars = {
            '0': 0b01111110, '1': 0b00110000, '2': 0b01101101, '3': 0b01111001,
            '4': 0b00110011, '5': 0b01011011, '6': 0b01011111, '7': 0b01110000,
            '8': 0b01111111, '9': 0b01111011, 'A': 0b01110111, 'B': 0b01111111,
            'C': 0b01001110, 'D': 0b01111100, 'E': 0b01001111, 'F': 0b01000111,
            'G': 0b01011110, 'H': 0b00110111, 'I': 0b00110000, 'J': 0b00111100,
            'K': 0b00101111, 'L': 0b00001110, 'M': 0b01010100, 'N': 0b00010101,
            'O': 0b01111110, 'P': 0b01100111, 'Q': 0b01101011, 'R': 0b01100110,
            'S': 0b01011011, 'T': 0b01110000, 'U': 0b00111110, 'V': 0b00100111,
            'W': 0b00111111, 'X': 0b00010011, 'Y': 0b00110011, 'Z': 0b01101101,
            ' ': 0b00000000, '-': 0b00000001, 'z': 0b01101101,
            'a': 0b01111101, 'b': 0b00011111, 'c': 0b00001101, 'd': 0b00111101,
            'e': 0b01101111, 'f': 0b01000111, 'g': 0b01111011, 'h': 0b00010111,
            'i': 0b00010000, 'j': 0b00111000, 'k': 0b01010111, 'l': 0b00000110,
            'n': 0b00010101, 'm': 0b00010100, 'o': 0b00011101, 'p': 0b01100111,
            'q': 0b01110011, 'r': 0b00000101, 's': 0b01011011, 't': 0b00001111,
            'u': 0b00011100, 'v': 0b00100011, 'w': 0b00101010, 'x': 0b00100101,
            'y': 0b00111011, '.': 0b10000000, '{': 0b01000110, '|': 0b00110000,
            '}': 0b01110000, '~': 0b00000001, '[': 0b00111001, '\\': 0b01100100,
            ']': 0b00001111, '^': 0b00100011, '_': 0b00001000, '`': 0b00000010,
            ':': 0b00001001, ';': 0b00001101, '<': 0b01100001, '=': 0b01001000,
            '>': 0b01000011, '?': 0b11010011, '@': 0b01011111, '!': 0b10000110,
            '"': 0b00100010, '#': 0b01111110, '$': 0b01101101, '%': 0b11010010,
            '&': 0b01000110, "'": 0b00100000, '(': 0b00101001, ')': 0b00001011,
            '*': 0b00100001, '+': 0b01110000, ',': 0b00010000, '/': 0b01010010,
        }

        digit_index = 0
        for char in text:
            if char == '.':
                # Decimal points share the digit, so just flip its DP bit
                if digit_index:
                    self.buffer[7 - (digit_index - 1)] |= 0x80
                continue

            if digit_index >= 8:
                break

            # Fill buffer from right to left (standard for these modules)
            self.buffer[7 - digit_index] = chars.get(char, 0x00)
            digit_index += 1

    def show(self):
        """Update the display with the current buffer content."""
        for i in range(8):
            self._write(i + 1, self.buffer[i])

    def brightness(self, value):
        """Set display brightness (0 to 15)."""
        # Ensure the value stays within the hardware limits
        if value < 0:
            value = 0
        if value > 15:
            value = 15

        # 0x0A is the Intensity Register
        self._write(0x0C, 0x01) # Ensure Shutdown Register is set to 'Normal'
        self._write(0x0A, value)
