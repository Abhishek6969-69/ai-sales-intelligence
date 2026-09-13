import re

with open("frontend/src/App.css", "r") as f:
    css = f.read()

# Increase all font-size: Xpx by 3
def increase_font_size(match):
    size = int(match.group(1))
    new_size = size + 3
    return f"font-size: {new_size}px"

css = re.sub(r'font-size:\s*(\d+)px', increase_font_size, css)

# Fix max-width
css = css.replace("max-width: 1420px", "max-width: 100%")

# Fix sidebar width
css = css.replace("width: 248px; flex: 0 0 248px;", "width: 280px; flex: 0 0 280px;")

# Increase some paddings
css = css.replace("padding: 10px 15px;", "padding: 12px 20px;") # buttons
css = css.replace("padding: 9px 13px;", "padding: 10px 16px;") # compact buttons
css = css.replace("height: 76px", "height: 84px") # topbar

with open("frontend/src/App.css", "w") as f:
    f.write(css)

print("Upscaled App.css")
