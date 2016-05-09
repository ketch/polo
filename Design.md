# Polo design

This file contains a record of design decisions for the project.

## Project scope
Polo is intended to allow exploration of high-dimensional datasets in the
IPython notebook via Pandas and Matplotlib.
The data may come from e.g. experiments or simulations, and the *dimensions*
referred to here are the parameters that vary between different experiments
or simulations (additionally, the data from each experiment or simulation may
itself be multidimensional).  When more than two parameters are varied, it can be quite
difficult to visually explore the properties of the dataset, since plots must
be projections onto a two-dimensional space.  In order to *see* into the other
dimensions, Polo facilitates varying parameters across

- multiple subplots
- multiple points or lines on a single plot (using color, style, etc.)

Additionally, Polo uses IPython widgets to allow rapid visual scanning through
additional parameter dimensions.

## Pandas dataframes
For now, Polo assumes that all data is provided in the form of a Pandas dataframe.
The dataframe fields can of course contain arbitrary objects.

## Matplotlib
For the moment, all plotting is done with matplotlib.  The design
is intended to make it possible eventually to plot with other packages
(e.g. Bokeh or Plotly).

## notebook backend
In order to deal directly and efficiently with low-level Matplotlib objects,
the current design requires use of the notebook (formerly nbagg) backend.  With
the inline backend, widgets will not work.
