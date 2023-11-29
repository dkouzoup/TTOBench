# Track library

## Track description

Every track in the library is defined by a JSON file with the following
fields:

- `metadata` : a dictionary of key-value pairs with general information on the
file content. Required fields: `id`, a unique identifier of the track that should
contain only letters, numbers and underscores, and `library version` for compatibility
reasons. Optional fields: `description`, `created by` and `license`.

- `altitude`: altitude at beginning of track. This field is optional and may
be used in combination with the gradients to plot the altitude profile of the
complete track.

- `stops`: a list of positions where stops are located. The first element
of the list must be the 0 position and the remaining positions should follow
a strictly increasing order. The last element of the list indicates the length
of the track *S*. Optimized trajectories may be derived from any departure
point to any destination point in the list.

- `speed limits`: a list of pairs - position, speed limit - indicating
the beginnings of track sections and their respective velocity restrictions.
The positions must be strictly increasing and every speed limit should be
different than its predecessor (otherwise there would be no need to add this
pair in the list). The position of the first pair should be 0 and the position
of the last pair must be smaller than the length of the track.

- `gradients`: a list of pairs - position, gradient - indicating the
beginnings of track sections and their respective (approximately constant)
slope. The positions must be strictly increasing and every gradient should be
different than its predecessor. Positive and negative gradient values indicate
uphill and downhill sections respectively. The position of the first pair should
be 0 and the position of the last pair must be smaller than the length of the track.
The field can be omitted for level tracks.

- `curvatures`: a list of triples - position, radius at start, and radius at end - 
indicating the beginnings of track sections and the corresponding curvature specifications.
Note that the curvature of the track at a point is the reciprocal of the (signed) radius of the
osculating circle at that point. A positive radius indicates a right-hand turn while 
a negative radius a left-hand turn. If the radius at start is equal to the radius at end 
then the track section has constant curvature.  For a straight track the two radii have value "infinity".
Different values for radius at start and radius at end denote a track section where the 
curvature of the section varies linearly with the travelled distance (clothoid curve) to 
interpolate between the two radii values. Note that the positions must be strictly 
increasing and the radius at start of each section should be equal to the redius at end of 
the previous section. The position of the first triple should be 0 and the position of the 
last triple must be smaller than the length of the track. The field can be omitted for straight tracks.

Note that the positions of speed limits, gradients, and curvatures will in general 
not coincide and a preprocessing step to derive track sections with constant properties
is necessary in the context of trajectory optimization. This representation,
however, makes a clear distinction between points with a speed limit change,
points with a slope change, and points with a curvature change. In this way the
interpretation of track properties is simplified.

## Content

- [This table](tracks.csv) summarizes the collected benchmark instances and some of their properties

