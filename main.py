import time

whitelist = [2019240]

timedIn = list()
timedOut = list()
timedOut.extend(whitelist)

print("out " + str(timedOut))
print("in " + str(timedIn))

while True:
    id = input("Enter ID: ")
    id = int(id)
    if id in whitelist and id in timedOut:
        timedOut.remove(id)
        timedIn.append(id)
        print("out " + str(timedOut))
        print("in "+ str(timedIn))
        # print("IN: " + str(id))
    elif id in whitelist and id in timedIn:
        timedIn.remove(id)
        timedOut.append(id)
        print("out " + str(timedOut))
        print("in "+ str(timedIn))