import numpy as np
import matplotlib.pyplot as plt

def exact_riemann_solution(q_l,q_r,v_l,v_r):
    r"""Exact solution to the Riemann problem for the LWR traffic model with variable speed limit.
        Inputs:
            - q_l, q_r : traffic density for left and right states
            - v_l, v_r : speed limits for left and right states
    """
    f = lambda q, v: v*q*(1-q)
    c = lambda q, v: v*(1.-2.*q)

    f_l = f(q_l,v_l)
    f_r = f(q_r,v_r)
    c_l = c(q_l,v_l)
    c_r = c(q_r,v_r)

    if f_r == f_l:
        states = [q_l, q_r]
        speeds = [0]
        wave_types = ['contact']
        reval = lambda xi: np.ones((1,len(xi)))*q_l

    elif (f_r < f_l) and (q_r > 0.5):
        # Left-going shock (1)
        q_star = (1. + np.sqrt(1.-4*f_r/v_l))/2.
        states = [q_l, q_star, q_r]
        shock_speed = (f_r-f_l)/(q_star-q_l)
        speeds = [shock_speed,0]
        wave_types = ['shock', 'contact']
        def reval(xi):
            q = np.zeros((1,len(xi)))
            q[0,:] = (xi<=shock_speed)*q_l \
              + (shock_speed<xi)*(xi<=0)*q_star \
              + (xi>=0)*q_r
            return q

    elif (f_r > f_l) and (q_l < 0.5):
        # Right-going shock (2)
        q_star = (1. - np.sqrt(1.-4*f_l/v_r))/2.
        states = [q_l, q_star, q_r]
        shock_speed = (f_r-f_l)/(q_r-q_star)
        speeds = [0,shock_speed]
        wave_types = ['contact', 'shock']
        def reval(xi):
            q = np.zeros((1,len(xi)))
            q[0,:] = (xi<=0)*q_l \
              + (0<xi)*(xi<=shock_speed)*q_star \
              + (xi>=shock_speed)*q_r
            return q

    elif (f_l > v_r/4.) and (q_r <= 0.5):
        # Left-going shock and right-going rarefaction (3)
        q_star = (1. + np.sqrt(1.-v_r/v_l))/2.
        shock_speed = -(f_l-v_r/4.)/(q_star-q_l)
        states = [q_l, q_star, 0.5, q_r]
        speeds = [shock_speed,0,(0,c_r)]
        wave_types = ['shock', 'contact', 'raref']
        def reval(xi):
            q = np.zeros((1,len(xi)))
            q[0,:] = (xi<=shock_speed)*q_l \
              + (shock_speed<xi)*(xi<=0)*q_star \
              + (0<xi)*(xi<c_r)*(1.-xi/v_r)/2. \
              + (xi>=c_r)*q_r
            return q

    elif (f_r > v_l/4.) and (q_l >= 0.5):
        # Left-going rarefaction and right-going shock (4)
        q_star = (1. - np.sqrt(1.-v_l/v_r))/2.
        shock_speed = (f_r-v_l/4.)/(q_r-q_star)
        states = [q_l,0.5,q_star,q_r]
        speeds = [(c_l, 0), 0, shock_speed]
        wave_types = ['raref', 'contact', 'shock']
        def reval(xi):
            q = np.zeros((1,len(xi)))
            q[0,:] = (xi<=c_l)*q_l \
                + (c_l<xi)*(xi<=0)*(1.-xi/v_l)/2. \
                + (0<xi)*(xi<=shock_speed)*q_star \
                + (shock_speed<xi)*q_r
            return q

    elif (f_l<f_r<=v_l/4.) and (q_l>0.5) and (q_r>=0.5):
        # Left-going rarefaction (6)
        q_star = (1. + np.sqrt(1.-4*f_r/v_l))/2.
        states = [q_l, q_star, q_r]
        c_star = c(q_star,v_l)
        speeds = [(c_l,c_star),0]
        wave_types = ['raref', 'contact']
        def reval(xi):
            q = np.zeros((1,len(xi)))
            q[0,:] = (xi<=c_l)*q_l \
                + (c_l<xi)*(xi<=c_star)*(1.-xi/v_l)/2. \
                + (c_star<xi)*(xi<=0)*q_star \
                + (0<=xi)*q_r
            return q

    elif (f_r<f_l<=v_r/4.) and (q_l<=0.5) and (q_r<0.5):
        # Right-going rarefaction (7)
        q_star = (1. - np.sqrt(1.-4*f_l/v_r))/2.
        states = [q_l, q_star, q_r]
        c_star = c(q_star,v_r)
        speeds = [0,(c_star,c_r)]
        wave_types = ['contact', 'raref']
        def reval(xi):
            q = np.zeros((1,len(xi)))
            q[0,:] = (xi<=0)*q_l \
                + (0<xi)*(xi<=c_star)*q_star \
                + (c_star<xi)*(xi<=c_r)*(1.-xi/v_r)/2. \
                + (c_r<=xi)*q_r
            return q

    elif (q_l>=0.5) and (q_r<=0.5) and (f_l<=v_r/4.) and (f_r<=v_l/4.):
        # Transonic rarefaction (5)
        if v_r < v_l:
            # q* on left side (5a)
            q_star = (1. + np.sqrt(1.-v_r/v_l))/2.
            states = [q_l, q_star, 0.5, q_r]
            c_star = c(q_star, v_l)
            speeds = [(c_l,c_star),0,(0,c_r)]
            wave_types = ['raref', 'contact', 'raref']
            def reval(xi):
                q = np.zeros((1,len(xi)))
                q[0,:] = (xi<=c_l)*q_l \
                    + (c_l<xi)*(xi<=c_star)*(1.-xi/v_l)/2. \
                    + (c_star<xi)*(xi<=0)*q_star \
                    + (0<xi)*(xi<=c_r)*(1.-xi/v_r)/2. \
                    + (c_r<xi)*q_r
                return q

        elif v_r > v_l:
            # q* on right side (5b)
            q_star = (1. - np.sqrt(1.-v_l/v_r))/2.
            states = [q_l, 0.5, q_star, q_r]
            c_star = c(q_star, v_r)
            speeds = [(c_l,0),0,(c_star,c_r)]
            wave_types = ['raref', 'contact', 'raref']
            def reval(xi):
                q = np.zeros((1,len(xi)))
                q[0,:] = (xi<=c_l)*q_l \
                    + (c_l<xi)*(xi<=0)*(1.-xi/v_l)/2. \
                    + (0<xi)*(xi<=c_star)*q_star \
                    + (c_star<xi)*(xi<=c_r)*(1.-xi/v_r)/2. \
                    + (c_r<xi)*q_r
                return q

        else:  # v_r == v_l
            states = [q_l, q_r]
            speeds = [(c_l,c_r),]
            wave_types = ['raref']
            def reval(xi):
                q = np.zeros((1,len(xi)))
                q[0,:] = (xi<=c_l)*q_l \
                    + (c_l<xi)*(xi<=c_r)*(1.-xi/v_l)/2. \
                    + (c_r<xi)*q_r
                return q

    else:
        print(f_l, f_r)
        raise Exception('Unhandled state!')

    return np.array([states]), speeds, reval, wave_types


def phase_plane_plot(q_l, q_r, v_l, v_r):
    r"""Plot Riemann solution in the q-f plane."""

    states, speeds, reval, wave_types = exact_riemann_solution(q_l, q_r, v_l, v_r)
    states = states[0]
    colors = {'shock': 'r', 'raref': 'b', 'contact': 'k'}

    f = lambda q, v: v*q*(1-q)

    f_l = f(q_l,v_l)
    f_r = f(q_r,v_r)

    # Plot flux curves
    q = np.linspace(0,1,500)
    plt.plot(q, f(q,v_l))
    plt.plot(q, f(q,v_r))
    plt.plot([q_l], [f(q_l,v_l)],'o')
    plt.plot([q_r], [f(q_r,v_r)],'o')

    fluxes = [f_l,f_r]
    if len(states) == 4:
        fluxes = [f_l, f(states[1],v_l), f(states[2],v_r), f_r]
    elif len(states) == 3:
        if isinstance(speeds[0],tuple):
            if speeds[0][1] >= 0:
                fluxes.insert(1,f(states[1],v_r))
            else:
                fluxes.insert(1,f(states[1],v_l))
        else:
            if speeds[0] < 0:
                fluxes.insert(1,f(states[1],v_l))
            else:
                fluxes.insert(1,f(states[1],v_r))

    for i, w in enumerate(wave_types):
        if w is 'raref':
            q = np.linspace(states[i],states[i+1],500)
            if min(speeds[i])<0:  # left-going
                ff = f(q,v_l)
            else:  # right-going
                ff = f(q,v_r)
            plt.plot(q,ff,color=colors['raref'],lw=3)
        else:
            plt.plot([states[i],states[i+1]],[fluxes[i],fluxes[i+1]],color=colors[wave_types[i]],lw=3)

    eps = 1.e-7
    speedlist = []
    for s in speeds:
        if not isinstance(s,tuple):
            s = [s]
        speedlist += s

    for s in speedlist:
        for xi in [s-eps, s+eps]:
            q = reval(np.array([xi]))
            if xi<0:
                v = v_l
            else:
                v = v_r
            plt.plot(q, f(q,v), 'ok')

    plt.text(q_l, f_l+0.02, '$q_l$')
    plt.text(q_r, f_r+0.02, '$q_r$')
    plt.xlim(0,1)
    ymax = 0.3*max(v_l,v_r)
    plt.ylim(0,ymax)
    plt.plot([0.5,0.5],[0,ymax],'--k',linewidth=1,alpha=0.5)
    plt.show()
