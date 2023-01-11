
# The **Track** class

Helper class to import track data from json files and vice versa.

## Usage

- Importing a JSON file

    - Create a configuration file as a Python dictionary with fields:
        - `id`: track ID (required)
        - `from`: index of starting timing point (optional)
        - `to`: index of ending timing point (optional)
        - `time`: maximum allowed travel time (optional)

    - Call Track constructor specifying the above configuration file.

- Exporting a JSON file

    - Create empty track or import existing track using the Track constructor.

    - Edit track properties as desired.

    - Use the `exportJson` method to export a JSON file with the new track.


## Example

An example of both importing and exporting a track is provided in the main script of `track.py`.

## Relevant attributes

- `title`: string with track ID.
- `length`: trip length between two timing points in m.
- `altitude`: altitude of starting point in m.
- `tUpper`: maximum trip time in s (None if not specified).

- `gradients`: pandas DataFrame with sections of constant gradient. Positions in m and gradients in permil.
- `speed limits`: pandas DataFrame with sections of constant speed limit. Positions in m and speed limits in km/h.

## Relevant methods

- `importJson`: create Track object from JSON file by specifying a configuration file as Python dictionary.
- `exportJson`: write JSON file from Track object. Limited to two timing points (more timing points can be manually added to the JSON file as a workaround).
- `importGradients`: define gradient sections as list of pairs (tuples or lists). Positions in m and gradients in permil.
- `importSpeedLimits`: define speed limit sections as list of pairs (tuples or lists). Positions in m and speed limits in km/h.
- `reverse`: change direction of track.
- `merge`: return pandas DataFrame containing sections with constant gradient _and_ speed limit.
- `print`: print pandas DataFrame created with the merge method.
- `plot`: plot track to file or screen.
