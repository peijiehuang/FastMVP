import base64
import io
import random
import string

from PIL import Image, ImageDraw, ImageFont

from app.core.security import generate_uuid


def generate_captcha() -> tuple[str, str, str]:
    """Generate a captcha image.

    Returns:
        (uuid, code, base64_image)
    """
    captcha_uuid = generate_uuid()
    code = "".join(random.choices(string.digits + string.ascii_lowercase, k=4))

    width, height = 160, 60
    image = Image.new("RGB", (width, height), _random_color(200, 255))
    draw = ImageDraw.Draw(image)

    # Draw captcha characters
    for i, char in enumerate(code):
        x = 10 + i * 35 + random.randint(-5, 5)
        y = random.randint(5, 15)
        color = _random_color(50, 150)
        try:
            font = ImageFont.truetype("arial.ttf", random.randint(28, 36))
        except (IOError, OSError):
            font = ImageFont.load_default()
        draw.text((x, y), char, fill=color, font=font)

    # Draw noise lines
    for _ in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=_random_color(100, 200), width=1)

    # Draw noise dots
    for _ in range(100):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        draw.point((x, y), fill=_random_color(50, 200))

    # Convert to base64
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return captcha_uuid, code, b64


def _random_color(start: int, end: int) -> tuple[int, int, int]:
    return (
        random.randint(start, end),
        random.randint(start, end),
        random.randint(start, end),
    )
