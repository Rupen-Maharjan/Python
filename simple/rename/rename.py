import os

# Step 1: Go to clutter directory
clutter_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clutter")
org_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "org")

os.makedirs(org_dir, exist_ok=True)  # make org folder if not exists
os.chdir(clutter_dir)

print("Clutter directory:", os.getcwd())

# Step 2: Rename & move function
def rename_and_move(ext, file, num):
    name, file_ext = os.path.splitext(file)
    if file_ext == ext:
        new_name = f"{num}{ext}"
        src = os.path.join(clutter_dir, file)
        dst = os.path.join(org_dir, new_name)

        print(f"{file} ---> {new_name}")
        os.rename(src, dst)
        return True   # renamed successfully
    return False      # skip this file

# Step 3: Get user extension
user_ext = "." + input("Extension without dot: ").strip()

# Step 4: Loop through files
files = os.listdir(".")
count = 1
for file in files:
    if rename_and_move(user_ext, file, count):
        count += 1   # only increment if a file was renamed
