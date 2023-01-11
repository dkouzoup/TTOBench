import os
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def importPairs(pairs, xLabel, yLabel) -> pd.DataFrame:
    """
    Convert list of pairs (tuples or lists) into pandas DataFrame.
    """

    if not isinstance(pairs, list):

        raise ValueError("Input must be a list (of tuples or lists)!")

    elementOk = lambda x: (isinstance(x, tuple) or isinstance(x, list)) and len(x) == 2

    if not all([elementOk(p) for p in pairs]):

        raise ValueError("Every element in list should be a tuple or list of dimension 2!")

    index = np.array([p[0] for p in pairs])

    if any(index < 0):

        raise ValueError("Position data cannot be negative!")

    if any(np.diff(index) <= 0):

        raise ValueError("Position data must monotonically increase!")

    df = pd.DataFrame({xLabel:index}).set_index(xLabel)

    df[yLabel] = np.array([p[1] for p in pairs])

    return df


def getUnit(string):
    """
    Extract parenthesized string with unit (assuming square brackets).
    """

    return string[string.find("[")+1:string.find("]")]


def convertUnit(df:pd.DataFrame, unitOut):
    """
    Convert data in pandas DataFrame from m/s to km/h and vice versa.
    """

    if len(df.columns) > 1:

        raise ValueError("Unit converter expects DataFrame with one column!")

    dfLabel = df.columns[0]
    unitIn = getUnit(dfLabel)

    dfOut = df.copy()
    dfOutLabel = dfLabel[:dfLabel.find("[")] + "[{}]".format(unitOut)
    dfOut.rename(columns={dfLabel: dfOutLabel}, inplace=True)

    if unitIn == 'km/h' and unitOut == 'm/s':

        dfOut[dfOutLabel] /= 3.6

    elif unitIn == 'm/s' and unitOut == 'km/h':

        dfOut[dfOutLabel] *= 3.6

    elif unitIn == unitOut:

        pass

    else:

        raise ValueError("Unknown conversion!")

    return dfOut


def checkLimits(df:pd.DataFrame, trackLength):
    """
    Check start and end position.
    """

    if df.index[0] != 0:

        raise ValueError("Error in '{}': First track section must start at 0 m (beginning of track)!".format(df.columns[0]))

    if df.index[-1] > trackLength:

        raise ValueError("Error in '{}': Last track section must start before {} m (end of track)!".format(df.columns[0], trackLength))


def getAltitudeProfile(gradients:pd.DataFrame, length, altitudeStart=0):
    """
    Calculate altitude profile from gradients.
    """

    pos = np.append(gradients.index.values, length)
    alt = np.array([altitudeStart])

    for ii in range(1, len(gradients)+1):

        posStart = gradients.index[ii-1]
        posEnd = gradients.index[ii] if ii < len(gradients) else length
        gradient = gradients.iloc[ii-1][0] if isinstance(gradients, pd.DataFrame) else gradients.iloc[ii-1]
        height = (posEnd - posStart)*(gradient/1e3)
        alt = np.append(alt, alt[-1] + height)

    altitudes = pd.DataFrame({gradients.index.name:pos, 'Altitude [m]':alt}).set_index(gradients.index.name)

    return altitudes


class Track():

    def __init__(self, config=None, path='../../tracks') -> None:
        """
        Constructor of Track objects.
        """

        # create empty track

        self.length = None  # length of track [m]

        self.altitude = 0  # altitude at beginning of track [m]

        self.tUpper = None  # maximum travel time [s] (minimum time + reserve)

        cols = ['Position [m]', 'Gradient [permil]']
        self.gradients = pd.DataFrame(columns=cols).set_index(cols[0])

        cols[1] = 'Speed limit [km/h]'
        self.speedLimits = pd.DataFrame(columns=cols).set_index(cols[0])

        self.title = '00_Untitled'
        self.path = path

        # import json file

        if config is not None:

            self.importJson(config)

            self.checkFields()


    def importJson(self, config):
        """
        Import json data to Track object based on specified configuration file.
        """

        if not isinstance(config, dict):

            raise ValueError("Track configuration should be provided as a dictionary!")

        if 'id' not in config:

            raise ValueError("Track ID must be specified in track configuration!")

        filename = os.path.join(self.path, config['id']+'.json')

        with open(filename) as file:

            data = json.load(file)

        self.length = data['timing points'][-1]
        self.altitude = data['altitude'] if 'altitude' in data else 0
        self.title = data['id']

        if 'time' in config:

            self.tUpper = config['time']

        self.importSpeedLimits(data['speed limits'])
        self.importGradients(data['gradients'])

        numPoints = len(data['timing points'])
        indxFrom = config['from'] if 'from' in config else 0
        indxTo = config['to'] if 'to' in config else numPoints-1

        if not 0 <= indxFrom < numPoints - 1:

            raise ValueError("Index of departure station is out of bounds!")

        if not indxFrom < indxTo < numPoints:

            raise ValueError("Index of destination station is out of bounds!")

        self.crop(data['timing points'][indxFrom], data['timing points'][indxTo])


    # NOTE: currently limited to json file with two timing points
    def exportJson(self, indent=4):
        """
        Export Track object to json file.
        """

        output = {'id':self.title, 'altitude':self.altitude}

        output['timing points'] = [0., round(float(self.length), 1)]

        pos = self.speedLimits.index.values.tolist()
        vel = self.speedLimits.iloc[:,0].values.tolist()
        output['speed limits'] = [[round(float(p), 1), int(v)] for p,v in zip(pos, vel)]

        pos = self.gradients.index.values.tolist()
        grd = self.gradients.iloc[:,0].values.tolist()
        output['gradients'] = [[round(float(p), 1), round(float(g), 1)] for p,g in zip(pos, grd)]

        filename = os.path.join(self.path, self.title + '.json')

        with open(filename, 'w') as file:

            json.dump(output, file, indent=indent)


    def checkLength(self):
        """
        Check track length is assigned properly.
        """

        if self.length is None:

            raise ValueError("Unspecified track length!")

        if self.length < 0 or np.isinf(self.length):

            raise ValueError("Track length must be a strictly positive number, not {}!".format(self.length))


    def checkGradients(self):
        """
        Check gradients are initialized properly.
        """

        checkLimits(self.gradients, self.length)

        if self.gradients.shape[0] == 0:

            raise ValueError("Gradients not set!")


    def checkSpeedLimits(self):
        """
        Check speed limits are initialized properly.
        """

        checkLimits(self.speedLimits, self.length)

        if self.speedLimits.shape[0] == 0:

            raise ValueError("Speed limits not set!")


    def checkFields(self):
        """
        Check track is initialized properly.
        """

        self.checkLength()

        if self.altitude is None or np.isinf(self.altitude):

            raise ValueError("Altitude must be a number, not {}!".format(self.altitude))

        if self.tUpper is not None and (self.tUpper <= 0 or np.isinf(self.tUpper)):

            raise ValueError("Maximum trip time (when specified) must be a strictly positive number, not {}!".format(self.tUpper))

        self.checkGradients()

        self.checkSpeedLimits()


    def importGradients(self, pairs):
        """
        Import user-defined gradients.
        """

        try:

            self.checkLength()

        except ValueError as e:

            raise ValueError("Cannot import gradients due to error: {}".format(str(e)))

        self.gradients = importPairs(pairs, 'Position [m]', 'Gradient [permil]')

        checkLimits(self.gradients, self.length)


    def importSpeedLimits(self, pairs):
        """
        Import user-defined speed limits
        """

        try:

            self.checkLength()

        except ValueError as e:

            raise ValueError("Cannot import speed limits due to error: {}".format(str(e)))

        self.speedLimits = importPairs(pairs, 'Position [m]', 'Speed limit [km/h]')

        checkLimits(self.speedLimits, self.length)


    def reverse(self):
        """
        Switch to opposite direction.
        """

        try:

            self.checkFields()

        except ValueError as e:

            raise ValueError("Track cannot be reversed due to error: {}".format(str(e)))

        def flipData(df):

            newIndex = np.flip(self.length - np.append(df.index[1:], self.length))
            newValues = np.flip(df[df.keys()[0]].values)
            return pd.DataFrame({df.index.name:newIndex, df.keys()[0]:newValues}).set_index(df.index.name)

        self.gradients = -flipData(self.gradients)
        self.speedLimits = flipData(self.speedLimits)

        self.title = self.title + ' (reversed)'

        return self


    def merge(self, unitVelocity='km/h'):
        """
        Return DataFrame with sections of constant gradient and speed limit.
        """

        speedLimits = convertUnit(self.speedLimits, unitOut=unitVelocity)
        out = self.gradients.join(speedLimits, how='outer').fillna(method='ffill')

        return out


    def print(self, unitVelocity='km/h'):
        """
        Basic printing functionality of track data.
        """

        df = self.merge(unitVelocity=unitVelocity)
        print(df)


    def copy(self):
        """
        Copy method.
        """

        newTrack = Track()
        newTrack.title = self.title
        newTrack.length = self.length
        newTrack.altitude = self.altitude
        newTrack.tUpper = self.tUpper

        newTrack.gradients = self.gradients.copy()
        newTrack.speedLimits = self.speedLimits.copy()

        if self != newTrack:

            raise ValueError("Error with copy!")

        return newTrack


    def __eq__(self, other):
        """
        Operator overloading.
        """

        ans = True

        # NOTE: ignoring title
        ans*= self.length == other.length
        ans*= self.altitude == other.altitude
        ans*= self.tUpper == other.tUpper

        ans*= all(self.gradients==other.gradients)
        ans*= all(self.speedLimits==other.speedLimits)

        return bool(ans)


    def plot(self, figSize=[12, 6], unitVelocity='km/h', ax=None, style='-', title=None, filename=None, plotAltitude=True):
        """
        Basic plotting functionality.
        """

        if ax is None:

            _, ax = plt.subplots(1, 1)

        if plotAltitude:

            alt = getAltitudeProfile(self.gradients, self.length, self.altitude)
            alt.rename(columns={'Altitude [m]':'Altitude'}, inplace=True)
            drawStyle = 'default'
            ylabel = 'Altitude [m]'

        else:

            alt = self.gradients
            alt.rename(columns={'gradient [permil]':'Gradient'}, inplace=True)
            drawStyle = 'steps-post'
            ylabel = 'Gradient [permil]'


        alt.plot(color='gray', title=('Visualization of ' + self.title) if title is None else title, grid=True, ylabel=ylabel, xlabel = 'Position [m]', ax=ax, style=style, drawstyle=drawStyle)
        ax.legend(loc='lower left')

        speedLimits = convertUnit(self.speedLimits, unitVelocity)
        speedLimits = pd.concat([speedLimits, pd.DataFrame({speedLimits.index.name:[self.length], speedLimits.keys()[0]:[None]}).set_index(speedLimits.index.name)])
        speedLimits.rename(columns={'speed limit [km/h]':'Speed limit'}, inplace=True)

        ax2 = ax.twinx()
        speedLimits.plot(ax=ax2, color='purple', drawstyle='steps-post', ylabel='Velocity [{}]'.format(unitVelocity), figsize=figSize, style=style).legend(loc='lower left')
        ax2.legend(loc='upper right')

        if filename is not None:

            plt.savefig(filename, bbox_inches='tight')

        return ax


    def crop(self, positionStart=None, positionEnd=None):
        """
        Update positions based on specified timing points.
        """

        positionStart = 0 if positionStart is None else positionStart
        positionEnd = self.length if positionEnd is None else positionEnd

        if (not 0 <= positionStart < self.length) or (not 0 < positionEnd <= self.length) :

            raise ValueError("Given positions must be between limits of track!")

        posStr = 'Position [m]'

        newPos = pd.DataFrame({posStr:[positionStart]}).set_index(posStr)

        def cropDf(dfIn):

            dfOut = newPos.join(dfIn, how='outer').ffill()
            dfOut = dfOut.loc[(dfOut.index >= positionStart)&(dfOut.index <= positionEnd)]
            dfOut[posStr] = dfOut.index - dfOut.index[0]
            dfOut.set_index(posStr, inplace=True)

            return dfOut

        self.length -= positionStart + (self.length - positionEnd)

        self.speedLimits = cropDf(self.speedLimits)
        self.gradients = cropDf(self.gradients)


if __name__ == '__main__':

    # Example code to import a track from a json file

    track1 = Track(config={'id':'CH_Fribourg_Bern'})

    print("\nImported Track:\n")
    track1.print()

    track1.plot()
    plt.show()

    # Example code to export a track as json file

    track2 = Track()
    track2.title = '00_example'
    track2.length = 10000

    track2.importGradients([(0, 0), (8000, 10)])
    track2.importSpeedLimits([(0, 140), (5000, 100)])

    print("\nExported Track:\n")
    track2.print(unitVelocity='m/s')  # optionally change displayed unit of velocity

    track2.exportJson()
