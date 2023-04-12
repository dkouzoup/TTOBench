import os
import json

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

def importPairs(pairs, columnName) -> pd.DataFrame:
    """
    Convert list of pairs (tuples or lists) into pandas DataFrame.
    First element of each pair represents position in meters.
    """

    # check inputs

    if not isinstance(columnName, str):

        raise ValueError("'columnName' must be a string!")

    if not isinstance(pairs, list) or any([not isinstance(d, tuple) and not isinstance(d, list) for d in pairs]):

        raise ValueError("'pairs' must be a list of tuples or lists!")

    if not all([len(d) == 2 for d in pairs]):

        raise ValueError("Each element in 'pairs' must be a list or tuple of length 2!")

    index = np.array([d[0] for d in pairs])

    if any(index < 0):

        raise ValueError("Position data cannot be negative!")

    if any(np.diff(index) <= 0):

        raise ValueError("Position data must monotonically increase!")

    # create dataframe

    indxName = 'Position [m]'
    df = pd.DataFrame({indxName:index, columnName:np.array([p[1] for p in pairs])}).set_index(indxName)

    return df


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

    def __init__(self, config=None) -> None:
        """
        Constructor of Track objects.
        """

        # create empty track

        self.length = None  # length of track [m]

        self.altitude = 0  # altitude at beginning of track [m]

        self.tUpper = None  # maximum travel time [s]

        cols = ['Position [m]', 'Gradient [permil]']
        self.gradients = pd.DataFrame(columns=cols).set_index(cols[0])

        cols[1] = 'Speed limit [km/h]'
        self.speedLimits = pd.DataFrame(columns=cols).set_index(cols[0])

        self.title = '00_Untitled'
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tracks')

        # import json file

        if config is not None:

            self.importJson(config)

            self.checkTrack()


    def importJson(self, config):
        """
        Import json data based on configuration file.
        """

        if not isinstance(config, dict):

            raise ValueError("Track configuration should be provided as a dictionary!")

        if 'id' not in config:

            raise ValueError("Track ID must be specified in track configuration!")

        filename = os.path.join(self.path, config['id']+'.json')

        with open(filename) as file:

            data = json.load(file)

        self.length = data['stops'][-1]
        self.altitude = data['altitude'] if 'altitude' in data else 0
        self.title = data['id']

        if 'time' in config:

            self.tUpper = config['time']

        self.importSpeedLimits(data['speed limits'])
        self.importGradients(data['gradients'])

        numPoints = len(data['stops'])
        indxFrom = config['from'] if 'from' in config else 0
        indxTo = config['to'] if 'to' in config else numPoints-1

        if not 0 <= indxFrom < numPoints - 1:

            raise ValueError("Index of departure station is out of bounds!")

        if not indxFrom < indxTo < numPoints:

            raise ValueError("Index of destination station is out of bounds!")

        self.crop(data['stops'][indxFrom], data['stops'][indxTo])


    # NOTE: currently limited to json file with two stops
    def exportJson(self, indent=4):
        """
        Export Track object to json file.
        """

        output = {'id':self.title, 'altitude':self.altitude}

        output['stops'] = [0., round(float(self.length), 1)]

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


    def checkLimits(self, df:pd.DataFrame):
        """
        Check start and end position.
        """

        if df.index[0] != 0:

            raise ValueError("Error in '{}': First track section must start at 0 m (beginning of track)!".format(df.columns[0]))

        if df.index[-1] > self.length:

            raise ValueError("Error in '{}': Last track section must start before {} m (end of track)!".format(df.columns[0], trackLength))


    def checkGradients(self):
        """
        Check gradients are initialized properly.
        """

        self.checkLimits(self.gradients)

        if self.gradients.shape[0] == 0:

            raise ValueError("Gradients not set!")


    def checkSpeedLimits(self):
        """
        Check speed limits are initialized properly.
        """

        self.checkLimits(self.speedLimits)

        if self.speedLimits.shape[0] == 0:

            raise ValueError("Speed limits not set!")


    def checkTrack(self):
        """
        Check track is initialized properly.
        """

        self.checkLength()

        self.checkGradients()

        self.checkSpeedLimits()

        if self.altitude is None or np.isinf(self.altitude):

            raise ValueError("Altitude must be a number, not {}!".format(self.altitude))

        if self.tUpper is not None and (self.tUpper <= 0 or np.isinf(self.tUpper)):

            raise ValueError("Maximum trip time (when specified) must be a strictly positive number, not {}!".format(self.tUpper))


    def importGradients(self, pairs):
        """
        Import user-defined gradients.
        """

        try:

            self.checkLength()

        except ValueError as e:

            raise ValueError("Cannot import gradients due to error: {}".format(str(e)))

        self.gradients = importPairs(pairs, 'Gradient [permil]')

        self.checkLimits(self.gradients)


    def importSpeedLimits(self, pairs):
        """
        Import user-defined speed limits
        """

        try:

            self.checkLength()

        except ValueError as e:

            raise ValueError("Cannot import speed limits due to error: {}".format(str(e)))

        self.speedLimits = importPairs(pairs, 'Speed limit [km/h]')

        self.checkLimits(self.speedLimits)


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


    def merge(self):
        """
        Return DataFrame with sections of constant gradient and speed limit.
        """

        return self.gradients.join(self.speedLimits, how='outer').fillna(method='ffill')


    def print(self):
        """
        Basic printing functionality.
        """

        print(self.merge())


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


    def plot(self, figSize=[12, 6], filename=None, withAltitude=True):
        """
        Basic plotting functionality.
        """

        fig, ax = plt.subplots()

        if withAltitude:

            alt = getAltitudeProfile(self.gradients, self.length, self.altitude)
            ax.plot(alt.index*1e-3, alt.values, drawstyle='default', color='gray', label='Altitude profile')
            ax.set_ylabel('Altitude [m]')

        else:

            ax.plot(self.gradients.index*1e-3, self.gradients.values, drawstyle='steps-post', color='gray', label='Gradient profile')
            ax.set_ylabel('Gradient [permil]')

        ax.set_xlabel('Position [km]')
        ax.set_title('Visualization of ' + self.title)
        ax.grid()

        ax.legend(loc='lower left')

        ax2 = ax.twinx()
        ax2.plot(self.speedLimits.index*1e-3, self.speedLimits.values, drawstyle='steps-post', color='purple', label='Speed limit')
        ax2.set_ylabel('Velocity [km/h]')

        ax2.legend(loc='upper right')

        fig.tight_layout()

        if figSize is not None:

            fig.set_size_inches(figSize[0], figSize[1])

        if filename is not None:

            plt.savefig(filename, bbox_inches='tight')

        plt.show()


    def crop(self, positionStart=None, positionEnd=None):
        """
        Update positions based on specified stops.
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

    # How to import a track from a json file

    track1 = Track(config={'id':'CH_Fribourg_Bern'})

    print("\nImported Track:\n")
    track1.print()

    track1.plot()
