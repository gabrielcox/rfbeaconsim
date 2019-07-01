#
# Plot rf collision possibilities
#

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label, glyphs

import random

class blipGrapher:
    #p = 0
    bWidth = 0.3
    bHeight = 0.3
    xs=[]
    ys=[]
    names=[]
    def __init__(self,bWidth):
        self.p = figure(output_backend="webgl", plot_width=1800, plot_height=1000)
        self.bWidth = bWidth
        # output to static HTML file
        output_file("line.html")

    def plotBlip(self,x,y,name):
        #self.p.rect(x, y, width=self.bWidth, height=self.bHeight, color="navy", alpha=0.5)
        self.xs.append(x)
        self.ys.append(y)
        self.names.append(name)

    def plotHilight(self,x,y):
        self.p.circle(x, y, radius=self.bWidth*10, color="red", alpha=0.5)

    def render(self):
        dataSource = ColumnDataSource(data=dict(sample=self.ys, time=self.xs, names=self.names))
        labels = LabelSet(x='time', y='sample', text='names', level='glyph',
              x_offset=5, y_offset=5, source=dataSource, render_mode='canvas', text_font_size='8pt')
        #self.p.scatter(x='time',y='sample', size=self.bWidth, source=dataSource)
        rectGlyph = glyphs.Rect(x='time',y='sample', width=self.bWidth, height=self.bHeight)
        self.p.add_glyph(dataSource,rectGlyph)
        self.p.add_layout(labels)
        show(self.p)

class blipData:
    txCount = 10        # how many transmitters
    blipFreq = 200      # in ms - how often blips are sent
    totalTime = 1000    # in ms - total period time to sample
    blipDuration = 0.3  # in ms - duration of individual blip
    blipJitter = 2      # in ms - amount of randomness added to each interval time
    slaTime = 1000      # in ms - required SLA to get a good message
    sampleCount = 10    # number of simulations to run (* totalTime)
    totCollisions = 0   # total collisions
    totSlaFailures = 0  # total SLA failures
    collCount = []      # collision count (per sample time)
    slaFailures = []    # slaFailures count (per sample time)
    blips = []          # blip data (2D array)
    intervals = int(totalTime/blipFreq) # Number of Intervals per TotalTime

    def __init__(self):
        # self.blips = [[0 for y in range(self.txCount)] for x in range(self.sampleCount)]
        self.bGraph = blipGrapher(self.blipDuration)
    
    def isIntersect(self,loc1, loc2, width):
        if loc1 is loc2:
            return False
        elif loc1 == loc2:
            return True
        elif loc1 < loc2:
            if loc1 + (width/2) >= loc2 - (width/2):
                return True
            else:
                return False
        else:  # loc1 > loc2
            if loc2 + (width/2) >= loc1 - (width/2):
                return True
            else:
                return False

    def isCollision(self,sample, xloc, width):
        for loc1 in self.blips[sample]:
            if self.isIntersect(loc1, xloc, width):
                return True
            else:
                continue
        return False

    def generateSamples(self,showVisualization=False):
        self.slaFailures=[]
        for y in range(self.sampleCount):
            print("%2d" % y, end='')
            self.collCount.append(0)
            txColCount = []
            for i in range(self.intervals):
                self.blips.append([])
                for x in range(self.txCount):
                    self.blips[i].append(0)
                    offset = 0
                    if i > 0:
                        # if there's a previous datum, add interval time + jitter
                        offset = self.blips[i-1][x] + self.blipFreq + random.randint(-1*self.blipJitter,self.blipJitter)
                    else:
                        # initial blip in series random number from 1/100th of in 1/100 of ms.                
                        offset = random.randint(0, self.blipFreq * 100) / 100
                        txColCount.append(0)

                    #print("y=%d, x=%d, xloc=%f" % (y, x, xloc))
                    self.blips[i][x] =offset
                    hasCollision = self.isCollision(i, self.blips[i][x], self.blipDuration)
                    if hasCollision:
                        txColCount[x] = txColCount[x] + 1
                        if txColCount[x] >= self.intervals:
                            self.slaFailures[y] = self.slaFailures[y] + 1
                            self.totSlaFailures = self.totSlaFailures + 1
                        self.collCount[y] = self.collCount[y] + 1
                        self.totCollisions = self.totCollisions + 1
                        if showVisualization:
                            self.bGraph.plotHilight(self.blips[i][x],y)
                        print("c", end='')
                    else:
                        print(".", end='')
                    if showVisualization:
                        self.bGraph.plotBlip(self.blips[i][x],y,x)
                    # p.text(x = 1010, y = y, text = "Col:%d" % collCount[y])
                print("|", end='')
            print ("")

showVisualization = True
bdata = blipData()
bdata.generateSamples(showVisualization)
# show the results
print("Ran %d samples" % bdata.sampleCount)
print("Total Collisions: %d" % bdata.totCollisions)
print("Total SLA Misses: %d" % bdata.totSlaFailures)

if showVisualization:
    print("Launching Visualization...")
    bdata.bGraph.render()