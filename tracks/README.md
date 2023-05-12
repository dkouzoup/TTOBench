# Track library

## Track description

Every track in the library is defined by a JSON file with the following
fields:

- `id` : a unique identifier to represent the track that should contain only letters,
numbers and underscores. If applicable, the first part of the ID followed by
an underscore should indicate the country of origin via the ISO Country
Code. Otherwise, the prefix 00 shall be used.

- `altitude`: altitude (in m) at beginning of track. This field is optional and may
be used in combination with the gradients to plot the altitude profile of the
complete track.

- `stops`: a list of positions (in m) where stops are located. The first element
of the list must be the 0 position and the remaining positions should follow
a strictly increasing order. The last element of the list indicates the length
of the track *S*. Optimized trajectories may be derived from any departure
point to any destination point in the list.

- `speed limits`: a list of pairs - position (in m), speed limit (in km/h) - indicating
the beginnings of track sections and their respective velocity restrictions.
The positions must be strictly increasing and every speed limit should be
different than its predecessor (otherwise there would be no need to add this
pair in the list). The position of the first pair should be 0 and the position
of the last pair cannot exceed the length of the track.

- `gradients`: a list of pairs - position (in m), gradient (in h) - indicating the
beginnings of track sections and their respective (approximately constant)
slope. The positions must be strictly increasing and every gradient should be
different than its predecessor. Positive and negative gradient values indicate
uphill and downhill sections respectively. The position of the first pair should
be 0 and the position of the last pair cannot exceed the length of the track.
The field can be omitted for level tracks.

Note that the positions of speed limits and gradients will in general not coincide
and a preprocessing step to derive track sections with constant properties
is necessary in the context of trajectory optimization. This representation,
however, makes a clear distinction between points with a speed limit change
and points with a slope change and simplifies the interpretation of the track
properties.

## Content

- [This table](tracks.csv) summarizes the collected benchmark instances and some of their properties

- The `Source` column specifies how the track data were acquired
    - `P`: public data (already in digital form)
    - `D`: described data (e.g., text or table in public document)
    - `I`: illustrated data (digitalization of publicly available figure)

- Data acquired via digitalization are subject to large approximation errors with respect to their souce

- The `References` column contains a non-exhaustive list of publications using each benchmark instance

## References

[1] Goverde, R.M.P., Scheepmaker, G.M., Wang, P.: Pseudospectral optimal
train control. European Journal of Operational Research (2021)

[2] Kouzoupis, D., Pendharkar, I., Frey, J., Diehl, M., Corman, F.: Direct multiple
shooting for computationally efficient train trajectory optimization. Transportation Research Part C (2023)

[3] Scheepmaker, G.M., Willeboordse, H.Y., Hoogenraad, J.H., Luijt, R.S.,
Goverde, R.M.P.: Comparing train driving strategies on multiple key performance
indicators. Journal of Rail Transport Planning & Management (2020)

[4] Trivella, A., Wang, P., Corman, F.: The impact of wind on energy-efficient
train control. EURO Journal on Transportation and Logistics (2021)

[5] Meyer, M., Menth, S., Lerjen, M.: Potentialermittlung Energieeffizienz
Traktion bei den SBB. Technical report, Bundesamt für Energie BFE
(2007)

[6] Aradi, S., Bécsi, T., Gáspár, P.: A predictive optimization method for
energy-optimal speed profile generation for trains. IEEE International
Symposium on Computational Intelligence and Informatics (2013)

[7] Aradi, S., Bécsi, T., Gáspár, P.: Design of predictive optimization method for
energy-effcient operation of trains. Proceedings of the European Control Conference (2014)

[8] Mäder, D.: Entwicklung eines tools für die auslegung von traktionsbatterien
für die netzunterstützung. Master’s thesis, FHNW (2023)

[9] Yang, X., Li, X., Ning, B., Tang, T.: An optimisation method for train
scheduling with minimum energy consumption and travel time in metro
rail systems. Transportmetrica B: Transport Dynamics (2015)

[10] Ye, H., Liu, R.: A multiphase optimal control method for multi-train
control and scheduling on railway lines. Transportation Research Part B (2016)

[11] Zhong, W., Lin, Q., Loxton, R., Teo, K.L.: Optimal train control
via switched system dynamic optimization. Optimization Methods and
Software (2021)

[12] Ghaviha, N., Bohlin, M., Holmberg, C., Dahlquist, E., Skoglund, R.,
Jonasson, D.: A driver advisory system with dynamic losses for passen-
ger electric multiple units. Transportation Research Part C: Emerging
Technologies (2017)