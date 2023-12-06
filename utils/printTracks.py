import os
import json
import numpy as np

def printTracks(tracksDir, filename=None):

    # TODO: check filename ends with csv

    rows = []

    rows += [['ID', 'Min speed limit [km/h]', 'Max speed limit [km/h]', 'Min gradient [permil]', 'Max gradient [permil]', 'Min (abs) radius [m]', 'Length [m]', 'Min interval [m]', 'Max interval [m]', 'Num intervals [-]', 'Num stops [-]']]

    for file in os.listdir(tracksDir):

        if file.endswith(".json"):

            with open(os.path.join(tracksDir, file)) as f:

                data = json.load(f)

            id, _ = os.path.splitext(file)

            length = data['stops']['values'][-1]
            numStops = len(data['stops']['values'])

            speedLimitValues = [v[1]*(3.6 if data['speed limits']['units']['velocity'] == 'm/s' else 1) for v in data['speed limits']['values']]  # km/h
            speedLimitPositions = [v[0]*(1e3 if data['speed limits']['units']['position'] == 'km' else 1) for v in data['speed limits']['values']]  # m

            if 'gradients' in data:

                gradientValues = [v[1] for v in data['gradients']['values']]  # permil
                gradientPositions = [v[0]*(1e3 if data['gradients']['units']['position'] == 'km' else 1) for v in data['gradients']['values']]  # m

            else:

                gradientValues, gradientPositions = [0.0], [0.0]

            if 'curvatures' in data:

                availableUnits = ['position', 'radius at start', 'radius at end']
                radiusValuesNonNegative = [abs(float(v[i]))*(1e3 if data['curvatures']['units'][availableUnits[i]] == 'km' else 1) for v in data['curvatures']['values'] for i in range(1,3) ] # m
                radiusPositions = [v[0]*(1e3 if data['curvatures']['units']['position'] == 'km' else 1) for v in data['curvatures']['values']]  # m

            else:

                radiusValuesNonNegative, radiusPositions = [float("infinity")], [0.0]

            positions = sorted(set(speedLimitPositions + gradientPositions + radiusPositions + [length]))
            intervals = np.diff(positions)

            rows += [[id, min(speedLimitValues), max(speedLimitValues), min(gradientValues), max(gradientValues), min(radiusValuesNonNegative),
                      length, round(min(intervals), 1), round(max(intervals), 1), len(intervals), numStops]]

    if filename is not None:

        content = ''

        for row in rows:

            row = [str(r) for r in row]
            content += ','.join(row)
            content += '\n'

        f = open(filename, 'w')
        f.write(content)
        f.close()

    else:

        for row in rows:

            print(row)  # TODO: nicer print


if __name__ == '__main__':

    tracksDir = "../tracks"

    printTracks(tracksDir, filename=None)
