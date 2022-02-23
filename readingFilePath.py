
## Assignment 4
##Course no: CRP 556
##Submitted by: Fatema Nourin
##Python Version: 3.7.10
##Problem about: Printing file path based on file content

##...........................................


import sys, os


baseDir = r'C:\Users\fatem\Box\Fall2021\crp 556\assignments (1)\assignments\Assignment_4\Assignment4'

for root, directories, files in os.walk(baseDir):
    for fi in files:
        if '.txt' in fi:
            f = open(os.path.join(root, fi), 'r')
            content = f.read()
            if 'decoy' not in content:
                print(content)
                print('root is: ' + root)
                print('file is: ' + fi)
                print('files in root is now ' + str(files))
                print('full path is: ' + os.path.join(root, fi))
                print("")
            f.close()

##This was a very fun Assignment! Took me a while to understand the question
