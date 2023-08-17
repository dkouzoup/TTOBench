import os
import json
import numpy as np

def printTracks(tracksDir, filename=None):

    # TODO: check filename ends with csv

    rows = []

    rows += [['ID', 'Min speed limit [km/h]', 'Max speed limit [km/h]', 'Min gradient [permil]', 'Max gradient [permil]', 'Length [m]', 'Min interval [m]', 'Max interval [m]', 'Num intervals [-]', 'Num stops [-]']]

    for file in os.listdir(tracksDir):

        if file.endswith(".json"):

            with open(os.path.join(tracksDir, file)) as f:

                data = json.load(f)

            id, _ = os.path.splitext(file)

            length = data['stops']['values'][-1]
            numStops = len(data['stops']['values'])

            speedLimitValues = [v[1]*(3.6 if data['speed limits']['units']['velocity'] == 'm/s' else 1) for v in data['speed limits']['values']]  # km/h
            gradientValues = [v[1] for v in data['gradients']['values']]  # permil
            speedLimitPositions = [v[0]*(1e3 if data['speed limits']['units']['position'] == 'km' else 1) for v in data['speed limits']['values']]  # m
            gradientPositions = [v[0]*(1e3 if data['gradients']['units']['position'] == 'km' else 1) for v in data['gradients']['values']]  # m

            positions = sorted(set(speedLimitPositions + gradientPositions + [length]))
            intervals = np.diff(positions)

            rows += [[id, min(speedLimitValues), max(speedLimitValues), min(gradientValues), max(gradientValues), length, round(min(intervals), 1), round(max(intervals), 1), len(intervals), numStops]]

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
