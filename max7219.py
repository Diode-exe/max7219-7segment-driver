"""module"""
import time
from machine import WDT

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
        '°': 0b01100011,

    }

    def text(self, text):
        """Display text on the seven-segment display."""
        # A simple font map for Seven Segment
        # Bit order: DP, A, B, C, D, E, F, G (1 = segment on)

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
            self.buffer[7 - digit_index] = self.chars.get(char, 0x00)
            digit_index += 1

    def set_num(self, number):
        """Set the display to show a number."""
        self.text(str(number))

    def show(self):
        """Update the display with the current buffer content."""
        for i in range(8):
            self._write(i + 1, self.buffer[i])

    def brightness(self, value):
        """Set display brightness (0 to 15)."""
        if value < 0:
            value = 0
        if value > 15:
            value = 15

        # 0x0A is the Intensity Register
        self._write(0x0C, 0x01) # Ensure Shutdown Register is set to 'Normal'
        self._write(0x0A, value)

    def scroll(self, message, delay=0.2, wdt=None):
        """Scrolls a long string across the display."""
        # Add spaces so the message starts and ends off-screen
        padding = " " * 8
        full_msg = padding + message + padding
        for i in range(len(full_msg) - 7):
            self.text(full_msg[i:i+8])
            self.show()
            if wdt:
                wdt.feed()
            time.sleep(delay)

    def power(self, on):
        """Toggle display power without clearing the buffer."""
        self._write(0x0C, 1 if on else 0)

    def brightness_fade_in(self, delay=0.5, wdt=None):
        """Fade display in."""
        for value in range(0, 15):
            self._write(0x0A, value)
            time.sleep(delay)
            if wdt:
                wdt.feed()
    def brightness_fade_out(self, delay=0.5, wdt=None):
        """Fade display out."""
        for value in range(15, 0, -1):
            self._write(0x0A, value)
            if wdt:
                wdt.feed()
            time.sleep(delay)

    def blink(self, times=3, delay=0.5):
        """Makes the display blink a specified number of times."""
        for each in range(times):
            self._write(0x0C, 0)
            time.sleep(delay)
            self._write(0x0C, 1)
            time.sleep(delay)

    def set_bar(self, length):
        """Set a bar graph on the display with the specified length."""
        self.text("_" * length)
        self.show()

    def rotate_segments(self, target_idx=0, wdt=None):
        """Animate a single digit by writing patterns into the buffer.

        This updates the internal `buffer` and calls `show()` so the
        animation isn't immediately overwritten by other low-level writes.
        By default this animates the rightmost digit (buffer index 0,
        which maps to register 1). The original value is restored.
        """
        patterns = [
            0b01000000, 0b00100000, 0b00010000, 0b00001000,
            0b00000100, 0b00000010,
        ]

        # save and animate
        orig = self.buffer[target_idx]
        for p in patterns:
            self.buffer[target_idx] = p
            self.show()
            if wdt:
                wdt.feed()
            time.sleep(0.15)

        # restore original value
        self.buffer[target_idx] = orig
        self.show()

    def set_char(self, index, char):
        """Sets a specific character at the given buffer index."""
        if not 0 <= index < 8:
            return

        pattern = self.chars.get(char, 0x00)
        # Maintain same right-to-left mapping as `text()`
        self.buffer[7 - index] = pattern
        self.show()

    def bounce(self, message, delay=0.2, wdt=None):
        """Bounce a short message back and forth across the display.

        If `message` is 8 characters or longer, fall back to `scroll()`.
        """
        if len(message) >= 8:
            self.scroll(message, delay=delay, wdt=wdt)
            return

        padding = " " * (8 - len(message))
        full = padding + message + padding
        span = len(full) - 7

        # forward and backward bounce
        for _ in range(1):
            # forward
            for i in range(span):
                self.text(full[i:i+8])
                self.show()
                time.sleep(delay)
                if wdt:
                    wdt.feed()

            # backward (skip endpoints to make a smooth bounce)
            for i in range(span - 2, 0, -1):
                self.text(full[i:i+8])
                self.show()
                time.sleep(delay)
                if wdt:
                    wdt.feed()

    def invert(self, wdt=None):
        """Invert segments. Off will turn on and vice versa"""
        # Flip all bits in each byte so segments invert properly.
        for i, _ in enumerate(self.buffer):
            self.buffer[i] = self.buffer[i] ^ 0xFF
            if wdt:
                wdt.feed()

    def print_buffer(self):
        """print buffer to console"""
        # Print as hex bytes for easier debugging (left-to-right display order)
        print([hex(b) for b in self.buffer])

    def test_pattern(self):
        """Display a test pattern of all eights with decimal points."""
        self.text("8.8.8.8.8.8.8.8.")

    def marquee(self, message, delay=0.2, wdt=None):
        """Like scroll(), but a marquee instead. Will go around 3 times per call"""
        if not message:
            return

        # Create a padded string and duplicate it so an 8-char slice
        # can wrap seamlessly from end->start.
        for _ in range(3):
            pad = " " * 6
            s = message + pad
            doubled = s + s
            i = 0
            self.text(doubled[i:i+8])
            self.show()
            if wdt:
                wdt.feed()
            time.sleep(delay)
            i = (i + 1) % len(s)

    def demo(self):
        """Demo mode"""
        wdt = WDT()

        self.text("DEMOMODE")
        self.show()
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)


        self.bounce(message="Bounce")
        self.show()
        self.bounce(message="Bounce")
        self.show()
        wdt.feed()
        self.bounce(message="Bounce")
        wdt.feed()

        self.show()
        self.scroll(message="Scroll", wdt=wdt)
        self.show()
        self.scroll(message="Scroll", wdt=wdt)
        self.show()
        self.scroll(message="Scroll", wdt=wdt)
        self.show()

        self.text("Fade out")
        wdt.feed()
        self.show()
        self.brightness_fade_out(wdt=wdt)
        self.show()
        self.clear()
        self.show()
        self.text("Fade in")
        wdt.feed()
        self.show()
        self.brightness_fade_in(wdt=wdt)
        wdt.feed()
        self.show()

        # self.marquee(message="Marquee", wdt=wdt)
        # wdt.feed()
        # self.show()
        # self.marquee(message="Marquee", wdt=wdt)
        # wdt.feed()
        # self.show()
        # self.marquee(message="Marquee", wdt=wdt)
        self.clear()
        self.show()

        self.text("BarGraph")
        self.show()
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        self.clear()
        self.show()
        i = 0
        for i in range(10):
            self.set_bar(length=i)
            self.show()
            time.sleep(0.5)
            if wdt:
                wdt.feed()
            i += 1
        wdt.feed()
        self.show()
        time.sleep(1)
        self.clear()

        self.text("Rotate")
        self.show()
        wdt.feed()
        time.sleep(1)
        self.text("Segments")
        self.show()
        wdt.feed()
        time.sleep(1)

        self.clear()
        self.show()
        wdt.feed()
        self.rotate_segments(wdt=wdt)
        self.rotate_segments(wdt=wdt)
        self.rotate_segments(wdt=wdt)
        self.clear()
        self.show()
        time.sleep(1)

        self.text("invert")
        self.show()
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)
        self.invert(wdt=wdt)
        wdt.feed()
        self.show()
        time.sleep(1)
        self.invert(wdt=wdt)
        self.clear()
        wdt.feed()
        self.show()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        self.text("Test pattern")
        wdt.feed()
        self.show()
        time.sleep(1)
        wdt.feed()
        time.sleep(1)
        wdt.feed()
        self.test_pattern()
        wdt.feed()
        self.show()

