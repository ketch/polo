import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib import animation
from ipywidgets import interact, widgets

def set_up_subplot_grid(subplot_names,fig):
    r"""Set up grid of axes for a single figure.
    
    Inputs:
      - subplot_names : list of strings that refer to the individual axes
      - fig : mpl figure on which the axes should appear
      
    Returns:
      - axes : a dictionary whose keys are subplot_names and whose values are the axes objects
      - nrows, ncols : the number of rows and columns in the axis grid
    """
    N = len(subplot_names)
    ncols = int(np.ceil(np.sqrt(N)))
    nrows = int(np.ceil(float(N)/ncols))
    axes = {}
    ax_grid = matplotlib.gridspec.GridSpec(nrows, ncols)
    ax_grid.update(wspace=0.,hspace=0.)

    # Set up axes and remove internal ticklabels
    row = 0
    col = 0
    for ax_name in subplot_names:
        axes[ax_name] = fig.add_subplot(ax_grid[row,col])
        if col > 0:
            axes[ax_name].yaxis.set_ticklabels(())
        col += 1
        if col == ncols:
            col = 0
            row += 1
    return axes, nrows, ncols


def set_up_lines(line_names,axes):
    r"""Create empty lines on one mpl axes object.
    
    Inputs:
      - line_names : list of strings that refer to the individual lines
      - axes : mpl axes object on which lines will be plotted
      
    Returns a dictionary whose keys are line_names and whose values are the line objects.
    """
    lines = {}
    for line_name in line_names:
        lines[line_name], = axes.plot([],[],'-o',lw=2)
    return lines


def set_up_faceting(df,ax_var,line_var,widget_var):
    r"""
    
    Inputs:
      - ax_var : parameter over which to facet axes
      - line_var : parameter over which to facet lines
      - widget_var : parameters to facet with widgets
      
    Returns:
      - param_values : dict of lists of unique parameter values for each facet type
      - facet_param : dict of parameters for each facet type
    """
    param_values   = {}  
    facet_param = {}
    
    facet_types = ['subplot','line']
    if type(widget_var) in (list, tuple):
        facet_params_list = [ax_var,line_var]+widget_var
        facet_types.extend(['widget_%s' % i for i in range(len(widget_var))])
    else:
        facet_params_list = [ax_var,line_var,widget_var]
        facet_types.append('widget_0')
    
    for fparam, ftype in zip(facet_params_list,facet_types):
        if fparam is not None:
            if type(fparam[1]) in (tuple,list):
                param_values[ftype]   = fparam[1] # Restrict to entries with these values 
                                                  # in the specified column
                facet_param[ftype] = fparam[0] # DataFrame column to use
                for param_value in param_values[ftype]:
                    if param_value not in df[facet_param[ftype]].unique():
                        raise Exception("No value %s in column %s" % (name, facet_param[ftype]))
            else:
                param_values[ftype] = df[fparam].unique() # Use all values
                facet_param[ftype] = fparam
        else:
            param_values[ftype] = [None]
            facet_param[ftype] = [None]
            
    return param_values, facet_param


def get_raw_data(row):
    r"""Get data for 1D PyClaw results."""
    sol = row.data[row.index[0]]
    xc = sol.state.grid.p_centers[0]
    q = sol.state.q[0,:]
    return xc, q


def comparison_plot(df,fig,facets,data_fun=get_raw_data,
                    xlim=(0,1),ylim=(-0.1,1.1)):
    r"""Plot solutions from Pandas dataframe df on figure fig.

        Inputs:
            - df: dataframe
            - fig: matplotlib figure
            - facets: a dictionary that may contain the following keys: 'subplot', 'line', 'slider'
              The value for each of these refers to a column of df and
              specifies what parameter should be differentiated
              (over different subplots, lines, or slider values).
              Each of the values in facets can be either:
                - A string, in which case all values in that column are used
                - A tuple of (str,list), in which the string indicates the column and
                  the list indicates which values to include
            - data_fun: a function that takes one row of df and returns the relevant data to plot.
    """
    ax_var = facets.get('subplot')
    line_var = facets.get('line')
    widget_var = facets.get('slider')
    if type(widget_var) in (list,tuple):
        num_widgets = len(widget_var)
    elif widget_var is not None:
        num_widgets = 1
    else:
        num_widgets = 0

    param_values, facet_param = set_up_faceting(df,ax_var,line_var,widget_var)
            
    axes, nrows, ncols = set_up_subplot_grid(param_values['subplot'],fig)
    lines = {}
    for ax_name, axis in axes.iteritems():
        lines[ax_name] = set_up_lines(param_values['line'],axis)
        
    for ax_name, ax in axes.iteritems():
        ax.set_xlim(xlim); ax.set_ylim(ylim)
        fs = 10+10./nrows
        if ax_var is not None:
            ax.set_title("%s: %s" % (facet_param['subplot'],ax_name), x = 0.5, y=0.95-nrows/30., fontsize=fs)
    ax0_lines = axes[param_values['subplot'][0]].lines
    if facet_param['line'][0] is not None:
        fig.legend(ax0_lines,param_values['line'],title=facet_param['line'])
    
    
    def plot_frame(**widget_vals):
        r"""Plot one frame."""
        widget_rows = [True]*len(df)
        figstring = []
        for i in range(num_widgets):
            widget_value = widget_vals[facet_param['widget_%s' % i]]
            widget_name = param_values['widget_%s' % i][widget_value]
            widget_rows = widget_rows & (df[facet_param['widget_%s' % i]]==widget_name)
            figstring.append("%s: %s" % (facet_param['widget_%s' % i],widget_name))
        figstring = ', '.join(figstring)
        fig.suptitle(figstring,fontsize=20)
      
        for ax_name, linedict in lines.iteritems():

            if param_values['subplot'][0] is not None:
                ax_rows = (df[facet_param['subplot']]==ax_name)
            else:
                ax_rows = [True]*len(df)
            
            for line_name, line in linedict.iteritems():
                if param_values['line'][0] is not None:
                    line_rows = (df[facet_param['line']]==line_name)
                else:
                    line_rows = [True]*len(df)
                row = df[widget_rows & ax_rows & line_rows]
                if len(row) == 1:
                    # User-defined function goes here
                    ####################
                    x, y = data_fun(row)
                    line.set_data(x,y)
                elif len(row) == 0:
                    line.set_data([],[])
                else:
                    diffs = [col for col in df.columns if row.iloc[0][col] != row.iloc[1,][col]]
                    diffs.remove('data')
                    raise Exception('Multiple entries would be plotted with the same parameters.                                     You must differentiate by the following:'+str(diffs))

        fig.canvas.draw()
        return fig

    if param_values['widget_0'][0] is not None:
        widges = {}
        for i in range(num_widgets):
            widges[facet_param['widget_%s' % i]] = widgets.IntSlider(min=0,max=len(param_values['widget_%s' % i])-1,value=0, description=facet_param['widget_%s' % i], readout=False)

        return interact(plot_frame, **widges)

    else:
        return plot_frame()
