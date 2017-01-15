#!/usr/bin/env python
import sys
import itertools
import numpy as np


class Rect(object):
    def __init__(self, x, y, width, height, data=None, rotated=False):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data = data
        self.rotated = rotated

    def copy(self, ):
        return Rect(self.x, self.y, self.width, self.height, self.data, self.rotated)

    def rotate(self, ):
        self.width, self.height = self.height, self.width
        self.rotated = not self.rotated

    def __str__(self, ):
        return "width:{} height:{} x:{} y:{} rot:{} dat:{}".format(
            self.width, self.height,
            self.x, self.y, self.rotated, 
            self.data, )

def disjoint(rectA, rectB):
    if ((rectA.x + rectA.width <= rectB.x) or
        (rectB.x + rectB.width <= rectA.x) or
        (rectA.y + rectA.height <= rectB.y) or
        (rectB.y + rectB.height <= rectA.y)):
        return True
    else:
        return False

    
def isContainedIn(rectA, rectB):
    return ((rectA.x >= rectB.x) and
            (rectA.y >= rectB.y) and
            (rectA.x + rectA.width <= rectB.x + rectB.width) and
            (rectA.y + rectA.height <= rectB.y + rectB.height))


class RectPack(object):

    def __init__(self, width, height):
        super().__init__()
        self.binWidth = width
        self.binHeight = height
        self.packedRectList = []
        self.freeRectList = [Rect(x=0, y=0, width=width, height=height)]
        self.occupancyHistory = []

    def pack(self, rectList, reorder=True):
        if reorder:
            workingRectList = list(sorted(rectList, key= lambda rect: -rect.width * rect.height))
        else:
            workingRectList = rectList    
        for rect in workingRectList:
            self.insert(rect)
            self.occupancyHistory.append(self.occupancy())
    
    def insert(self, rect):
        newNode = self.findPositionForNewNodeBestShortSideFit(rect)
        if newNode.height == 0:
            return newNode
        numRectanglesToProcess = len(self.freeRectList)
        idx = 0
        while idx < numRectanglesToProcess:
            if (self.splitFreeNode(self.freeRectList[idx], newNode)):
                del self.freeRectList[idx]
                idx -= 1
                numRectanglesToProcess -= 1
            idx += 1
        self.pruneFreeList()
        self.packedRectList.append(newNode)
        return newNode

    def isBetterFit(self, bestShortSideFit, bestLongSideFit, shortSideFit, longSideFit):
        if bestShortSideFit is None:
            return True
        if shortSideFit < bestShortSideFit:
            return True
        if shortSideFit == bestShortSideFit:
            if bestLongSideFit is None:
                return True
            if longSideFit < bestLongSideFit:
                return True
        return False

    def findPositionForNewNodeBestShortSideFit(self, rect):
        width, height = rect.width, rect.height
        #bestNode = Rect(0, 0, 0, 0) # rect.copy()
        bestNode = rect.copy()
        bestShortSideFit = None
        bestLongSideFit = None
        for freeRect in self.freeRectList:
            # Try to place the rectangle in upright (non-flipped) orientation.
            if (freeRect.width >= width and freeRect.height >= height):
                leftoverHoriz = abs(freeRect.width - width)
                leftoverVert = abs(freeRect.height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)
                if self.isBetterFit(bestShortSideFit, bestLongSideFit, shortSideFit, longSideFit):
                    bestNode.x = freeRect.x
                    bestNode.y = freeRect.y
                    bestNode.width = width
                    bestNode.height = height
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit
            if (freeRect.width >= height and freeRect.height >= width):
                flippedLeftoverHoriz = abs(freeRect.width - height)
                flippedLeftoverVert = abs(freeRect.height - width)
                flippedShortSideFit = min(flippedLeftoverHoriz, flippedLeftoverVert)
                flippedLongSideFit = max(flippedLeftoverHoriz, flippedLeftoverVert)
                if self.isBetterFit(bestShortSideFit, bestLongSideFit, flippedShortSideFit, flippedLongSideFit):
                    bestNode.width = width
                    bestNode.height = height
                    bestNode.rotate()
                    # bestNode.width = height
                    # bestNode.height = width
                    #print(bestNode)
                    bestNode.x = freeRect.x
                    bestNode.y = freeRect.y
                    bestShortSideFit = flippedShortSideFit
                    bestLongSideFit = flippedLongSideFit
        return bestNode

    def pruneFreeList(self):
        i = 0
        while (i < len(self.freeRectList)):
            j = i + 1
            while (j < len(self.freeRectList)):
                if isContainedIn(self.freeRectList[i], self.freeRectList[j], ):
                    del self.freeRectList[i]
                    i -= 1
                    break
                if isContainedIn(self.freeRectList[j], self.freeRectList[i], ):
                    del self.freeRectList[j]
                    j -= 1
                j += 1
            i += 1

    def splitFreeNode(self, freeNode, usedNode):
        #  Test with SAT if the rectangles even intersect.
        if (usedNode.x >= freeNode.x + freeNode.width or usedNode.x + usedNode.width <= freeNode.x or
            usedNode.y >= freeNode.y + freeNode.height or usedNode.y + usedNode.height <= freeNode.y):
            return False
        if (usedNode.x < freeNode.x + freeNode.width and usedNode.x + usedNode.width > freeNode.x):
            #  New node at the top side of the used node.
            if (usedNode.y > freeNode.y and usedNode.y < freeNode.y + freeNode.height):
                newNode = Rect(freeNode.x, freeNode.y, freeNode.width, freeNode.height, )
                newNode.height = usedNode.y - newNode.y
                self.freeRectList.append(newNode)
            #  New node at the bottom side of the used node.
            if (usedNode.y + usedNode.height < freeNode.y + freeNode.height):
                newNode = Rect(freeNode.x, freeNode.y, freeNode.width, freeNode.height, )
                newNode.y = usedNode.y + usedNode.height
                newNode.height = freeNode.y + freeNode.height - (usedNode.y + usedNode.height)
                self.freeRectList.append(newNode)
        if (usedNode.y < freeNode.y + freeNode.height and usedNode.y + usedNode.height > freeNode.y):
            #  New node at the left side of the used node.
            if (usedNode.x > freeNode.x and usedNode.x < freeNode.x + freeNode.width):
                newNode = Rect(freeNode.x, freeNode.y, freeNode.width, freeNode.height, )
                newNode.width = usedNode.x - newNode.x
                self.freeRectList.append(newNode)
            #  New node at the right side of the used node.
            if (usedNode.x + usedNode.width < freeNode.x + freeNode.width):
                newNode = Rect(freeNode.x, freeNode.y, freeNode.width, freeNode.height, )
                newNode.x = usedNode.x + usedNode.width
                newNode.width = freeNode.x + freeNode.width - (usedNode.x + usedNode.width)
                self.freeRectList.append(newNode)
        return True;


    def occupancy(self):
        usedSurfaceArea = 0
        for usedRect in self.packedRectList:
            usedSurfaceArea += usedRect.width * usedRect.height
        return usedSurfaceArea / (self.binWidth * self.binHeight)

def pairwiseIter(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a = iter(iterable)
    return zip(a, a)

def main(argv):
    if ((len(argv) < 5) or (len(argv) % 2 != 1)):
        print("Usage: python -m rect_pack.rect_pack binWidth binHeight w_0 h_0 w_1 h_1 w_2 h_2 ... w_n h_n\n")
        print("       where binWidth and binHeight define the size of the bin.\n")
        print("       w_i is the width of the i'th rectangle to pack, and h_i the height.\n")
        print("Example: python -m rect_pack.rect_pack 256 256 30 20 50 20 10 80 90 20\n")
    argNums = [float(arg) for arg in argv[1:]]
    binSize = argNums[0:2]
    print("Initializing bin to size {}x{}".format(*binSize))
    rectBin = RectPack(*binSize)
    widthByHeights = [(rectWidth, rectHeight,) for rectWidth, rectHeight in pairwiseIter(argNums[2:])]
    # widthByHeights = list(sorted(widthByHeights, key= lambda wByH: -wByH[0] * wByH[1]))
    # inRects = [Rect(0, 0, width, height) for width, height in widthByHeights]
    inRects = [Rect(0, 0, width, height, data="{},{},{}".format(num, width, height)) for num, (width, height) in enumerate(widthByHeights)]
    rectBin.pack(inRects)
    failedCount = 0
    for num, (packedRect, occupancy) in enumerate(zip(rectBin.packedRectList, rectBin.occupancyHistory)):
        rectWidth, rectHeight = packedRect.width, packedRect.height
        print("# {} Packing rectangle of size {}x{}: ".format(num, rectWidth, rectHeight), end="")
        # Test success or failure.
        if packedRect.height > 0:
            print("Packed to (x,y)=({},{}), (w,h)=({},{}). Free space left: {:.2f}%".format(
                packedRect.x, packedRect.y, packedRect.width, packedRect.height,
                100.0 - occupancy*100.0))
        else:
            print("Failed! Could not find a proper position to pack this rectangle into. Skipping this one.")
            failedCount += 1
    if not failedCount:
        print("Done. All rectangles packed.")
    else:
        print("Done. {} rectangles failed packing.".format(failedCount))
        

    ## let's plot it
    import pylab as pl
    import matplotlib.colorbar as cbar
    colors = pl.cm.jet(np.asarray(range(len(widthByHeights))) / len(widthByHeights))
    ax = pl.subplot(111)
    for packedRect in rectBin.packedRectList:
        # Test success or failure.
        if packedRect.height > 0:
            import random
            color = pl.cm.jet(random.random())
            rectPatch = pl.Rectangle(
                (packedRect.x, packedRect.y), packedRect.width, packedRect.height,
                # linewidth=0,
                # color=color)
                facecolor=color)
            ax.add_patch(rectPatch)
    cax, _ = cbar.make_axes(ax) 
    cb2 = cbar.ColorbarBase(cax, cmap=pl.cm.jet) 

    # for packedRect in rectBin.packedRectList:
    #     print(packedRect)
        
    ax.set_xlim(0, binSize[0])
    ax.set_ylim(0, binSize[1])
    pl.show()        
    ###
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
