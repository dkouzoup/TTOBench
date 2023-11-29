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
If radius at start is equal to radius at end then the track section has constant curvature.
A positive radius indicates that the osculating circle is located to the right of the track; 
a negative radius indicates that the circle is located to the left of the track. For a straight
track the two radiuses have value "infinity". Different values for radius at start and radius at
end denote a track section where the curvature of the section changes linearly with travelled
distance (clothoid curve). Note that the positions must be strinctly increasing and the radius at start
should be equal to the the redius at end of the previous section. The position of the first pair should
be 0 and the position of the last pair must be smaller than the length of the track. 
The field can be omitted for straight tracks.

Note that the positions of speed limits and gradients will in general not coincide
and a preprocessing step to derive track sections with constant properties
is necessary in the context of trajectory optimization. This representation,
however, makes a clear distinction between points with a speed limit change
and points with a slope change and simplifies the interpretation of the track
properties.

## Content

- [This table](tracks.csv) summarizes the collected benchmark instances and some of their properties

