import os

for name in os.listdir("symbols"):
    command = "~/maze/az/bin/s3 upload symbols/%s symbols/%s" % (name, name)
    print command
    os.system(command)
