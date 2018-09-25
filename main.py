import datetime

whitelist = [2019240, 2019291]
ids = {2019240: "Arthur DiLeo Jr.", 2019291: "Nicholas Fierro"}

timedIn = list()
timedOut = list()
timedOut.extend(whitelist)

print("out " + str(timedOut))
print("in " + str(timedIn))

while True:
    id = input("Enter ID: ")
    id = int(id)
    if id in whitelist:
        if id in timedOut:
            timedOut.remove(id)
            timedIn.append(id)
            print("checked in %s at %s" % (ids[id], datetime.datetime.now()))
        elif id in timedIn:
            timedIn.remove(id)
            timedOut.append(id)
            print("checked out %s at %s" % (ids[id], datetime.datetime.now()))