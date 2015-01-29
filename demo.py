from clawpack import pyclaw
from clawpack import riemann
import numpy as np
import pandas as pd

def advection_setup(nx=100, solver_type='classic', lim_type=2, weno_order=5, CFL=0.9, 
          time_integrator='SSP104', outdir='./_output'):

    riemann_solver = riemann.advection_1D

    if solver_type=='classic':
        solver = pyclaw.ClawSolver1D(riemann_solver)
    elif solver_type=='sharpclaw':
        solver = pyclaw.SharpClawSolver1D(riemann_solver)
        solver.lim_type = lim_type
        solver.weno_order = weno_order
        solver.time_integrator = time_integrator
    else: raise Exception('Unrecognized value of solver_type.')

    solver.kernel_language = 'Fortran'
    solver.cfl_desired = CFL
    solver.cfl_max = CFL*1.1

    solver.bc_lower[0] = pyclaw.BC.periodic
    solver.bc_upper[0] = pyclaw.BC.periodic

    x = pyclaw.Dimension(0.0,1.0,nx,name='x')
    domain = pyclaw.Domain(x)
    state = pyclaw.State(domain,solver.num_eqn)

    state.problem_data['u'] = 1.  # Advection velocity

    # Initial data
    xc = state.grid.x.centers
    beta = 100; gamma = 0; x0 = 0.75
    state.q[0,:] = np.exp(-beta * (xc-x0)**2) * np.cos(gamma * (xc - x0))

    claw = pyclaw.Controller()
    claw.keep_copy = True
    claw.solution = pyclaw.Solution(state,domain)
    claw.solver = solver

    if outdir is not None:
        claw.outdir = outdir
    else:
        claw.output_format = None

    claw.tfinal = 1.0

    return claw

def generate_data():
    df = pd.DataFrame(columns=['frame', 'data', 'time'])

    def run_and_save(params,df):
        claw = advection_setup(**params)
        claw.verbosity = 0
        status = claw.run()
        for i in range(len(claw.frames)):
            df = df.append(params,ignore_index=True)
            df.loc[len(df)-1,'frame'] = i
            df.loc[len(df)-1,'data'] = claw.frames[i]
            df.loc[len(df)-1,'time'] = claw.frames[i].t
        return df
            
    # Run at different resolutions
    # Put all results into a pandas dataframe
    for n in (10,20,40,80):
        for solver_type in ('classic','sharpclaw'):
            dirname = './_%s_%s_output' % (n,solver_type)
            params = {'nx' : n, 'outdir' : dirname}
            params['solver_type'] = solver_type
            df = run_and_save(params,df)

    for n in (10,20,40,80,160):
        solver_type = 'sharpclaw'
        dirname = './_%s_%s_output' % (n,solver_type)
        params = {'nx' : n, 'outdir' : dirname}
        params['solver_type'] = solver_type
        params['weno_order'] = 7
        df = run_and_save(params,df)

    return df
         
