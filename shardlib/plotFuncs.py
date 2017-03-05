import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy.stats as stats
import trees
import dbaccess as dba
import dataProcessing as dp
import sessionFuncs as sf
from types import *

titles = {
    'K1': '$K_{I}$ errors', 'K2': '$K_{II}$ errors', 'K3': '$K_{III}$ errors'}
figtitle = {
    'avgNormError': 'Normalized average error along the crack front',
    'maxNormError': 'Maximum magnitude of the normalized error along the crack front',
    'areaDiff': 'Normalized difference between integrals of the analytical and analysis along the crack front',
    'dotProd': 'Normalized error difference between analytical and analysis dot products'}


def getBranchSimIdsByCriteria(treeRoot, criteria):
    stack = [treeRoot]
    while len(stack) > 0:
        if str(stack[0].getName()) == criteria[0]:
            index = criteria.index(str(stack[0].getName()))
            criteria.pop(index)
            stack = [stack[0]]
            if len(criteria) == 0:
                node = stack[0]
                break
        temp = stack.pop(0)
        stack = temp.getChildren() + stack
    if criteria == []:
        return node.getSuccessfulMembers(), node.getFailedMembers()
    else:
        raise KeyError


def filterSimIds(simIds, criteriaDict):
    simKeys = simIds
    for parKey in criteriaDict.keys():
        simKeys = dba.getSubsetByCriterion(
            simKeys, parKey, criteriaDict[parKey])
    return set(simKeys)

# XFEM CP


def getCeAeError(simId, errType, sif, successful=True):
    ad = dp.AnalysisData(simId)
    ad.calcAnSol()
    ad.calculateStats()
    ce = ad.getMeshParams()['crackEdges']
    ae = ad.getMeshParams()['allEdges']
    if successful:
        err = ad.getErrorReports()[errType][sif]
    else:
        err = None
    key = (ce, ae)
    return key, err


def createCeAeDataStr(simIds, errType, sif, successful):
    data = {}
    for simId in simIds:
        key, err = getCeAeError(simId, errType, sif, successful)
        data[key] = (simId, err)
    return data


def getDiamHeightError(simId, errType, sif):
    ad = dp.AnalysisData(simId)
    ad.calcAnSol()
    ad.calculateStats()
    d = ad.getContainerDiam()
    h = ad.getContainerHeight()
    err = ad.getErrorReports()[errType][sif]
    key = (d, h)
    return key, err


def createD_H_SimId_Err_ValDataStr(simIds, errType, sif):
    data = {}
    for simId in simIds:
        key, err = getDiamHeightError(simId, errType, sif)
        if key not in data.keys():
            data[key] = []
        data[key].append((simId, err))
    return data


def getSimIdsWithLowestErrorPerDH(simIds, errorType, sif):
    data = createD_H_SimId_Err_ValDataStr(simIds, errorType, sif)
    simIdDict = {}
    for dhk in data.keys():
        data[dhk].sort(key=lambda x: abs(x[1]))
        simIdDict[dhk] = data[dhk][0]
    return simIdDict


def selectSimsForMinErrors(validSimIds, errorTypes, sifs):
    simDict = {}
    for et in errorTypes:
        simDict[et] = {}
        for sk in sifs:
            simDict[et][sk] = getSimIdsWithLowestErrorPerDH(
                validSimIds, et, sk)
    return simDict


def getContourPlotData(data):
    ds, hs, errors = [], [], []
    for d, h in data.keys():
        ds.append(d)
        hs.append(h)
        errors.append(data[(d, h)][1])
    return ds, hs, errors


def prepContourPlotData(dataDict, errorType):
    sifs = sorted(dataDict.keys())
    ds, hs, errors = [], [], []
    for s in sifs:
        d, h, errs = getContourPlotData(dataDict[s])
        ds.append(d)
        hs.append(h)
        errors.append(errs)
    ds = np.array(ds)
    hs = np.array(hs)
    errors = np.array(errors)
    if errorType in ['maxNormError', 'dotProd', 'avgNormError']:
        errors = np.abs(errors)
    minErr, maxErr = np.min(errors), np.max(errors)
    return sifs, ds, hs, errors, minErr, maxErr


def createContourPlot4(dataDict, fig, errorType, selected=None, levels=25):
    levels = levels + 1
    axes = []
    sifs, d, h, errors, minErr, maxErr = prepContourPlotData(
        dataDict, errorType)

    gs = mpl.gridspec.GridSpec(2, len(sifs),
                               height_ratios=[16.18, 1], hspace=0.35)

    for i in range(len(sifs)):
        axes.append(fig.add_subplot(gs[0, i]))
        axes[i].tricontourf(
            d[i],
            h[i],
            errors[i],
            levels,
            cmap=mpl.cm.rainbow,
            norm=mpl.colors.Normalize(
                vmin=minErr,
                vmax=maxErr))
        axes[i].tricontour(d[i], h[i], errors[i],
                           levels, linewidths=0.5, colors='k',
                           norm=mpl.colors.Normalize(vmin=minErr, vmax=maxErr))
        axes[i].plot(d[i], h[i], 'ko', ms=4)

        if selected is not None:
            xax = max(d[i]) - min(d[i])
            yax = max(h[i]) - min(h[i])
            ratio = yax / xax
            r = 10
            c = mpl.patches.Ellipse(
                selected,
                width=r,
                height=r * ratio,
                axes=axes[i],
                fc='none',
                ec='w',
                linewidth=1.5)
            axes[i].add_artist(c)

        axes[i].set_xlabel('container diameter')
        axes[i].set_ylabel('container height')
        axes[i].set_title(titles[sifs[i]])
        axes[i].set_xlim(min(d[i]), max(d[i]))
        axes[i].set_ylim(min(h[i]), max(h[i]))
        axes[i].set_xticks(d[i])
        axes[i].set_yticks(h[i])
        axes[i].set_xticklabels(
            ['${0}$'.format(l) for l in d[i]], rasterized=False)
        axes[i].set_yticklabels(
            ['${0}$'.format(l) for l in h[i]], rasterized=False)

    ax = fig.add_subplot(gs[1, :])
    bounds = np.linspace(
        round(
            minErr *
            100,
            1),
        round(
            maxErr *
            100,
            1),
        levels)
    cb = mpl.colorbar.ColorbarBase(
        ax,
        cmap=mpl.cm.rainbow,
        norm=None,
        boundaries=bounds,
        extendfrac='auto',
        ticks=bounds,
        spacing='uniform',
        orientation='horizontal')
    cb.set_label('Errors [%]')
    mpl.pyplot.figtext(0.5, 1, figtitle[errorType], figure=fig,
                       horizontalalignment='center', size='x-large')


# 3D scatter plot funcs
def get3dScatterPlotData(simIds):
    diams, heights, aes = [], [], []
    for simId in simIds:
        dob = dp.AnalysisData(simId)
        d, h, ae = dob.get3dScatterPlotData()
        diams.append(d)
        heights.append(h)
        aes.append(ae)
    return diams, heights, aes


def create3dScatterPlotSummary(validSimIds, invalidSimIds, title, fig):
    vd, vh, vae = get3dScatterPlotData(validSimIds)
    ivd, ivh, ivae = get3dScatterPlotData(invalidSimIds)
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(vd, vh, vae, c='b')
    ax.scatter(ivd, ivh, ivae, c='r')
    ax.set_xlim3d(getMinMaxVals(vd, ivd))
    ax.set_ylim3d(getMinMaxVals(vh, ivh))
    ax.set_zlim3d(getMinMaxVals(vae, ivae))
    ax.set_xlabel('diameter')
    ax.set_ylabel('height')
    ax.set_zlabel('allEdges')
    ax.set_title(title)

    s = mpl.lines.Line2D([0, 1], [0, 1],
                         marker='o', markeredgecolor='k', markerfacecolor='b',
                         linestyle=' ', markeredgewidth=1, markersize=4.4)
    f = mpl.lines.Line2D([0, 1], [0, 1],
                         marker='o', markeredgecolor='k', markerfacecolor='r',
                         linestyle=' ', markeredgewidth=1, markersize=4.4)
    ax.legend([s, f], ['successful simulations', 'failed simulations'],
              loc=2, bbox_to_anchor=(1.02, 0.8), borderaxespad=0)


def getMinMaxVals(a, b):
    a = np.array(a)
    b = np.array(b)
    if len(a) == 0 and len(b) == 0:
        return None, None
    elif len(a) == 0:
        return min(b), max(b)
    elif len(b) == 0:
        return min(a), max(a)
    else:
        return min(min(a), min(b)), max(max(a), max(b))


# Container size comparisons
def plotContainerSizeComparison(d, h, crackRatio, simTree, fig):
    sims_s, sims_f = getBranchSimIdsByCriteria(simTree, [crackRatio])
    simIds = sims_s | sims_f
    a = dba.getParameterRange(simIds, 'a')
    b = dba.getParameterRange(simIds, 'b')
    cracks = []
    for a_ in a:
        for b_ in b:
            a_ = float(a_)
            b_ = float(b_)
            if a_ / b_ == float(crackRatio):
                cracks.append([a_, b_])
    x0 = 0
    y0 = 0
    center = (x0, y0)
    ax = fig.add_subplot(211, aspect='equal')
    for crack in cracks:
        e = mpl.patches.Ellipse(
            xy=center, width=crack[0], height=crack[1],
            angle=0, alpha=0.4, fc='r', ec='r', lw=2, axes=ax)
        ax.add_artist(e)
        e1 = mpl.patches.Ellipse(
            xy=center, width=crack[0], height=crack[1],
            angle=0, ec='r', lw=2, fill=False, axes=ax)
        ax.add_artist(e1)

    cont_xfem = mpl.patches.Circle(xy=center, radius=float(d / 2),
                                   ec='b', lw=1.5, fill=False)
    ax.add_artist(cont_xfem)

    a = cracks[0][0]
    b = cracks[0][1]
    dm_ellip = d * np.sqrt(1 + (a**2 - b**2) / (d**2))
    dm_scale = d * float(a) / b

    cont_fem_e = mpl.patches.Ellipse(
        xy=center, width=dm_ellip, height=d,
        ec='m', lw=1.5, fill=False)
    ax.add_artist(cont_fem_e)

    cont_fem_s = mpl.patches.Ellipse(
        xy=center, width=dm_scale, height=d,
        ec='g', lw=1.5, fill=False)
    ax.add_artist(cont_fem_s)

    vl = mpl.lines.Line2D([0, 0], [-0.7 * d, 0.7 * d], c='k', ls='-.')
    hl = mpl.lines.Line2D(
        [-0.55 * dm_scale, 0.55 * dm_scale], [0, 0], c='k', ls='-.')
    ax.add_artist(vl)
    ax.add_artist(hl)

    ax.set_xlim(-dm_scale, dm_scale)
    ax.set_ylim(-d, d)
    # ax.grid(True)
    ax.set_title('Comparison of container sizes after mesh transformation')
    ax.legend([e, cont_xfem, cont_fem_e, cont_fem_s],
              ['crack', 'XFEM', 'FEM elliptic', 'FEM scale'])

    ax = fig.add_subplot(212, aspect='equal')
    cr_l = mpl.lines.Line2D([-0.5 * a, 0.5 * a], [0, 0], color='r', lw=2)
    ax.add_artist(cr_l)

    c_xfem = mpl.patches.Rectangle(
        [-0.5 * d, -0.5 * h], d, h,
        ec='b', lw=1.5, fill=False)
    ax.add_artist(c_xfem)

    c_fem_e = mpl.patches.Rectangle(
        [-0.5 * dm_ellip, -0.5 * h], dm_ellip, h,
        ec='m', lw=1.5, fill=False)
    ax.add_artist(c_fem_e)

    c_fem_s = mpl.patches.Rectangle(
        [-0.5 * dm_scale, -0.5 * h], dm_scale, h,
        ec='g', lw=1.5, fill=False)
    ax.add_artist(c_fem_s)

    vl = mpl.lines.Line2D([0, 0], [-0.55 * h, 0.55 * h], c='k', ls='-.')
    ax.add_artist(vl)

    ax.set_xlim(-dm_scale, dm_scale)
    ax.set_ylim(-h, h)


def plotSimId(simId, fig):
    sifs = ['K1', 'K2', 'K3']
    ylabels = {'K1': '$K_{I}$', 'K2': '$K_{II}$', 'K3': '$K_{III}$'}
    ylabels2 = {
        'K1': '$K_{I}$ errors [%]',
        'K2': '$K_{II}$ errors [%]',
        'K3': '$K_{III}$ errors [%]'}
    ad = dp.AnalysisData(simId)
    ad.calcAnSol()
    ad.calculateStats()
    angles = np.array(ad.getAngles())
    axes = []
    for i in range(len(sifs)):
        axes.append(fig.add_subplot(len(sifs) * 100 + 10 + (i + 1)))
        ax2 = axes[i].twinx()
        ansol = axes[i].plot(angles, ad.getAnSol()[sifs[i]])
        res = axes[i].plot(angles, ad.getResults()[sifs[i]])
        errs = ax2.plot(
            angles, ad.getErrorReports()['difference'][
                sifs[i]], 'r')  # *100

        axes[i].set_ylabel(ylabels[sifs[i]])
        ax2.set_ylabel(ylabels2[sifs[i]])
        axes[i].grid(True)
        axes[i].set_xlim(min(angles), max(angles))
        axes[i].spines['right'].set_color('r')
    axes[0].legend(
                   ansol + res + errs,
                   ['SIF analytical', 'simulation', 'errors'],
                   bbox_to_anchor=(1.08, 1),
                   loc=2,
                   borderaxespad=0)
