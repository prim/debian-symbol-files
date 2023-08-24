import os

for name in os.listdir("symbols"):
    if "e15ec" not in name:
        continue
    command = "~/maze/az2/bin/s3 upload symbols/%s symbols/%s" % (name, name)
    print command
    os.system(command)
