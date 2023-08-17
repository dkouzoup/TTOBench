import os

import json


class ValidateTrack():

    def __init__(self):

        self.requiredFields = {'metadata', 'stops', 'speed limits'}

        self.optionalFields = {'altitude', 'gradients'}

        self.requiredMetadata = {'id'}

        self.optionalMetadata = {'description', 'created by', 'library version', 'license'}

        self.trackData = None


    def validateTrack(self, filename):

        self.loadJson(filename)

        self.validateKeys()

        self.validateMetadata()

        self.validateAltitude()

        self.validateStops()

        self.validateSpeedLimits()

        self.validateGradients()


    def loadJson(self, filename):

        try:

            with open(filename) as file:

                data = json.load(file)

        except FileNotFoundError:

            raise FileNotFoundError("Specified track file not found!")

        self.trackData = data
        self.filename = filename


    def validateKeys(self):
        "Check that all required keys are there and that there are no redundant fields."

        data = self.trackData

        requiredFields = set()

        for key in data.keys():

            if key in self.requiredFields:

                requiredFields.add(key)

            elif key not in self.optionalFields:

                raise ValueError("Unknown field detected: {}'!".format(key))

        if requiredFields != self.requiredFields:

            missing = ", ".join([f"'{item}'" for item in self.requiredFields-requiredFields])
            output = f"Not all required fields found! Missing: {missing}!"

            raise ValueError(output)


    def validateMetadata(self):

        metadata = self.trackData['metadata']

        requiredMetadata = set()

        for key in metadata.keys():

            if key in self.requiredMetadata:

                requiredMetadata.add(key)

            elif key not in self.optionalMetadata:

                raise ValueError("Unknown field detected in metadata: {}'!".format(key))

        if requiredMetadata != self.requiredMetadata:

            missingMetadata = ", ".join([f"'{item}'" for item in self.requiredMetadata-requiredMetadata])
            outputMetadata = f"Not all required fields found in metadata! Missing: {missingMetadata}!"

            raise ValueError(outputMetadata)

        trackID, _ = os.path.splitext(self.filename.split(os.path.sep)[-1])

        if trackID != metadata['id']:

            raise ValueError("Inconsistent ID between filename and metadata!")


    def validateAltitude(self):

        altitude = self.trackData['altitude'] if 'altitude' in self.trackData else None

        if altitude is not None:

            fields = {'unit', 'value'}

            if fields != altitude.keys():

                raise ValueError("Unexpected keys in 'altitude'! Expecting 'unit' and 'value'.")

            if altitude['unit'] not in {'m', 'km'}:

                raise ValueError("Unexpected unit in 'altitude'! Expecting 'm' or 'km'.")

            if type(altitude['value']) not in {float, int}:

                raise ValueError("Unexpected value type in 'altitude'! Expecting float or int, found {}.".format(type(altitude['value'])))

            if altitude['value'] < 0:

                raise ValueError("'altitude' must be positive!")


    def validateStops(self):

        stops = self.trackData['stops']

        fields = {'unit', 'values'}

        if fields != stops.keys():

            raise ValueError("Unexpected keys in 'stops'! Expecting 'unit' and 'values'.")

        if stops['unit'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'stops'! Expecting 'm' or 'km'.")

        for ii, v in enumerate(stops['values']):

            if type(v) not in {float, int}:

                raise ValueError("Unexpected value type in 'stops'! Expecting float or int, found {}.".format(type(v)))

            if v < 0:

                raise ValueError("Values in 'stops' must be positive!")

            if ii == 0:

                if v != 0:

                    raise ValueError("First value in 'stops' must be equal to zero!")

            if ii > 0 and v <= stops['values'][ii-1]:

                raise ValueError("Values in 'stops' must be strictly increasing!")


    def validateSpeedLimits(self):

        speedLimits = self.trackData['speed limits']

        fields = {'units', 'values'}

        if fields != speedLimits.keys():

            raise ValueError("Unexpected keys in 'speed limits'! Expecting 'units' and 'values'.")

        fieldsUnits = {'position', 'velocity'}

        if fieldsUnits != speedLimits['units'].keys():

            raise ValueError("Unexpected keys in  units of 'speed limits'! Expecting 'position' and 'velocity'.")

        if speedLimits['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in position of 'speed limits'! Expecting 'm' or 'km'.")

        if speedLimits['units']['velocity'] not in {'km/h', 'm/s'}:

            raise ValueError("Unexpected unit in velocity of 'speed limits'! Expecting 'km/h' or 'm/s'.")

        for ii, v in enumerate(speedLimits['values']):

            if len(v) != 2:

                raise ValueError("Unexpected size of nested list in 'speed limits'! Expecting 2, got {}.".format(len(v)))

            pos, vel = v

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'speed limits'! Expecting float or int, found {}.".format(type(pos)))

            if type(vel) not in {float, int}:

                raise ValueError("Unexpected value type in velocity of 'speed limits'! Expecting float or int, found {}.".format(type(vel)))

            if pos < 0 or vel < 0:

                raise ValueError("Position and velocity of 'speed limits' must be positive!")

            if ii == 0:

                if pos != 0:

                    raise ValueError("First position of 'speed limits' must be equal to zero!")

            if ii > 0 and pos <= speedLimits['values'][ii-1][0]:

                raise ValueError("Positions in 'speed limits' must be strictly increasing! Error at point {}.".format(ii+1))


    def validateGradients(self):

        gradients = self.trackData['gradients']

        fields = {'units', 'values'}

        if fields != gradients.keys():

            raise ValueError("Unexpected keys in 'gradients'! Expecting 'units' and 'values'.")

        fieldsUnits = {'position', 'slope'}

        if fieldsUnits != gradients['units'].keys():

            raise ValueError("Unexpected keys in  units of 'gradients'! Expecting 'position' and 'slope'.")

        if gradients['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in position of 'gradients'! Expecting 'm' or 'km'.")

        if gradients['units']['slope'] not in {'permil'}:

            raise ValueError("Unexpected unit in velocity of 'gradients'! Expecting 'permil'.")

        for ii, v in enumerate(gradients['values']):

            if len(v) != 2:

                raise ValueError("Unexpected size of nested list in 'gradients'! Expecting 2, got {}.".format(len(v)))

            pos, grad = v

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'gradients'! Expecting float or int, found {}.".format(type(pos)))

            if type(grad) not in {float, int}:

                raise ValueError("Unexpected value type in slope of 'gradients'! Expecting float or int, found {}.".format(type(grad)))

            if pos < 0:

                raise ValueError("Position of 'gradients' must be positive!")

            if ii == 0:

                if pos != 0:

                    raise ValueError("First position of 'gradients' must be equal to zero!")

            if ii > 0 and pos <= gradients['values'][ii-1][0]:

                raise ValueError("Positions in 'gradients' must be strictly increasing! Error at point {}.".format(ii+1))


if __name__ == '__main__':

    validator = ValidateTrack()

    tracksDir = "../tracks"

    for file in os.listdir(tracksDir):

        if file.endswith(".json"):

            id, _ = os.path.splitext(file)

            print("Validating track: {}".format(id))

            validator.validateTrack(os.path.join(tracksDir, file))

            print("ok")

