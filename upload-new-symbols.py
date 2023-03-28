import os, subprocess

output = subprocess.check_output("git status", shell=True)

for line in output.split("\n"):
    line = line.strip()
    if line.endswith(".debug"):
        file_path = line

        command = "~/maze/az/bin/s3 upload %s %s" % (file_path, file_path)
        print os.system(command), command

        command = "git add %s" % (file_path)
        print os.system(command), command
