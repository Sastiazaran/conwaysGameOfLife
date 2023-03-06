## author : @asti

ON = 1
OFF = 0

class patterns:
    def __init__(self, name, pattern):
        self.name = name            ## name of config
        self.pattern = pattern      ## pattern itself

##############################################################################

## still

# block
block = [[ON, ON],
          [ON, ON]]                                                    ##
Block = patterns("block", [block])                                              ##

# beehive                                                                        ##
beehive = [[OFF, ON, ON, OFF],[ON, OFF, OFF, ON],[OFF, ON, ON, OFF]]            #  #
Beehive = patterns("beehive", [beehive])                                         ##

# loaf
loaf = [[OFF,ON,ON,OFF],[ON,OFF,OFF,ON],[OFF,ON,OFF,ON],[OFF,OFF,ON,OFF]]
Loaf = patterns("loaf", [loaf])

# boat
boat = [[ON,ON,OFF],[ON,OFF,ON],[OFF,ON,OFF]]
Boat = patterns("boat", [boat])

# tub
tub = [[OFF,ON,OFF],[ON,OFF,ON],[OFF,ON,OFF]]
Tub = patterns("tub", [tub])

stillList = [Block, Beehive, Loaf, Tub]

##############################################################################

## oscilators

# blinker
blinker = []
blinker.append([[ON],[ON],[ON]])
blinker.append([[ON,ON,ON]])
Blinker = patterns("blinker", blinker)

# toad
toad = []
toad.append([[OFF,OFF,ON,OFF],[ON,OFF,OFF,ON],[ON,OFF,OFF,ON],[OFF,ON,OFF,OFF]])
toad.append([[OFF,ON,ON,ON],[ON,ON,ON,OFF]])
Toad = patterns("toad", toad)

# beacon
beacon = []
beacon.append([[ON,ON,OFF,OFF],[ON,ON,OFF,OFF],[OFF,OFF,ON,ON],[OFF,OFF,ON,ON]])
beacon.append([[ON,ON,OFF,OFF],[ON,OFF,OFF,OFF],[OFF,OFF,OFF,ON],[OFF,OFF,ON,ON]])
Beacon = patterns("beacon", beacon)

##############################################################################

# spaceships

glider = []
glider.append([[OFF,ON,OFF],[OFF,OFF,ON],[ON,ON,ON]])
glider.append([[ON,OFF,ON],[OFF,ON,ON],[OFF,ON,OFF]])
glider.append([[ON,OFF,OFF],[OFF,ON,ON],[ON,ON,ON]])
Glider = patterns("glider", glider)

# light-weight spaceship
lwss = []
lwss.append([[ON,OFF,OFF,ON,OFF],[OFF,OFF,OFF,OFF,ON],[ON,OFF,OFF,OFF,ON],[OFF,ON,ON,ON,ON]])
lwss.append([[OFF,OFF,ON,ON,OFF],[ON,ON,OFF,ON,ON],[ON,ON,ON,ON,OFF],[OFF,ON,ON,OFF,OFF]])
lwss.append([[OFF,ON,ON,ON,ON],[ON,OFF,OFF,OFF,ON],[OFF,OFF,OFF,OFF,ON],[ON,OFF,OFF,ON,OFF]])
lwss.append([[OFF,ON,ON,OFF,OFF],[ON,ON,ON,ON,OFF],[ON,ON,OFF,ON,ON],[OFF,OFF,ON,ON,OFF]])
Lwss = patterns("light-weight spaceship", lwss)

##############################################################################

still = [Block, Beehive, Loaf, Boat, Tub]
oscilators = [Blinker, Toad, Beacon]
spaceships = [Glider, Lwss]

allPatterns = still + oscilators + spaceships

counters = dict()
