import os
import random
import string

# Step 1: Go to clutter directory
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clutter"))


# Step 2: File extensions to choose from
extensions = [".txt", ".pdf", ".jpg", ".png", ".docx"]

# Step 3: Generate random filenames
def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Step 4: Create files
for _ in range(20):  # create 10 files
    name = random_name()
    ext = random.choice(extensions)
    filename = name + ext

    with open(filename, "w") as f:
        f.write("This is a random file: " + filename)

    print(f"Created: {filename}")
