"""The `tracking` module handles the tracking of electricity
to determine the decomposition of the electric mix.
"""

from time import time

import numpy as np
import pandas as pd

############### Local functions
from ecodynelec.checking import check_frequency
from ecodynelec.preprocessing.auxiliary import load_rawEntso


#
###########################
# TRACK MIX
###########################
###########################


def track_mix(raw_data, freq='H', network_losses=None, residual_global=False, is_verbose=False):
    """Performs the electricity tracking. Master function for the electricity mix computation.

    Parameters
    ----------
        raw_data:
            path to ENTSO-E data (str), or `pandas.DataFrame` with production and exchange data.
        freq: str, default to "H"
            frequency of time steps
        network_losses: pandas.Series, default to None
            vector of estimate for grid losses at every time step.
        residual_global: bool, default to False
            whether to include a local production residual as production unit during the electricity
            tracking computation.
        is_verbose: bool, default to False
            show text during computation.

    Returns
    -------
    pandas.DataFrame
        table with the electricity mix in the studied countries (parameter.ctry + 'Other'), containing each production mean of each country at each time step.
    """

    t0 = time()  # time measurment

    if is_verbose: print("Importing information...")
    df = load_rawEntso(mix_data=raw_data, freq=freq)
    ctry, ctry_mix, prod_means, all_sources = reorder_info(data=df)

    if network_losses is not None:
        uP = get_grid_losses(df, losses=network_losses)
    else:
        uP = pd.Series(data=1, index=df.index)  # Grid losses not considered -> 1

    if is_verbose: print("Tracking origin of electricity...")
    mixE = compute_tracking(df, all_sources=all_sources, uP=uP, ctry=ctry, ctry_mix=ctry_mix,
                            prod_means=prod_means, residual=residual_global, freq=freq, is_verbose=is_verbose)

    if is_verbose: print("\n\tElectricity tracking: {:.1f} sec.\n".format(time() - t0))
    return mixE  # df is the raw power per source (kWh or MWh)


#
###############################################################################
# ###########################
# # Reorder info
# ###########################
# ###########################
#

def reorder_info(data):
    """
    Function to rename and reorder the columns in the production and exchanges table. It returns 4 useful
    lists for the electricity tracking.
    
    Parameters
    ----------
        data: pandas.DataFrame
            the production and exchange table

    Returns
    -------
    list
        ctry: sorted list of involved countries
    list
        ctry_mix: list of countries where eletricity can come from, including 'Other' (list)
    list
        prod_means: list of production means, without mixes (list)
    list
        all_sources: list of production means and mixes, with precision of the country of origin (list)
    """

    # Reorganize columns in the dataset
    ctry = sorted(list(np.unique([k.split("_")[-1] for k in data.columns])))  # List of considered countries
    ctry_mix = list(np.unique(
        [k.split("_")[1] for k in data.columns if k.startswith("Mix_")]))  # List of importing countries (right order)
    ctry_mix = ctry + [k for k in ctry_mix if k not in ctry]  # add "Others" in the end of pays_mixe

    # Definition of the means of production and column names for the calculation matrix
    prod_means = []
    all_sources = []
    for k in data.columns[data.columns.str.endswith(ctry[0])]:
        # Gather all energy source names (only for one country)
        if k.startswith("Mix_"):
            prod_means.append("_".join(k.split("_")[:-1]))  # Energy exchanges
            all_sources.append("_".join(k.split("_")[:-1]))
        else:
            prod_means.append(k.split("_{}".format(ctry[0]))[0])

    all_sources += [k for k in data.columns if not k.startswith("Mix_")]  # Add AFTER the names of means of production

    return ctry, ctry_mix, prod_means, all_sources


#
###############################################################################
# ###########################
# # Get grid losses
# ###########################
# ###########################
#

def get_grid_losses(data, losses=None):
    """Gives for each time step the amount of electricity to produce in order to consume 1 kWh."""
    # Add new demand in the FU vector for each step of time
    uP = pd.Series(data=None, index=data.index, dtype='float32')  # vector for values of FU vector at each time step
    for k in losses.index:  # grid losses ratio for each step of time
        localize = ((uP.index.year == losses.loc[k, "year"]) & (uP.index.month == losses.loc[k, "month"]))
        uP.iloc[localize] = losses.loc[k, "Rate"]

    return uP


#
###############################################################################
# ###########################
# # Set FU vector
# ###########################
# ###########################
#

def set_FU_vector(all_sources, target='CH'):
    """Defines the Functional Unit vector: full of zeros, except at the indexes
    corresponding to the target country, where a 1 is written.

    This function isn't used in the main pipeline.

    Parameters
    ----------
        all_sources: list
            All sources, as returned by `reorder_info`
        target: str, default to 'CH'
            target country
    """
    # Defines the FU vector
    u = np.zeros(
        len(all_sources))  # basic Fonctional Unit Vector (FU vector) --> do never change. Is multiplied by uP (for losses) during process
    u[all_sources.index(f"Mix_{target}")] = 1  # Location of target country in the FU vector
    return u


#
###############################################################################
# ###########################
# # Compute tracking
# ###########################
# ###########################
#

def compute_tracking(data, all_sources, uP, ctry, ctry_mix, prod_means,
                     residual=False, freq='H', is_verbose=False):
    """Function leading the electricity tracking: by building the technology matrix and computing the inversion at each time step.

    Parameters
    ----------
        data: pandas.DataFrame
            Table with the production and exchange data of all involved countries
        all_sources: array-like
            an ordered list with the mix names and production mean names, without origin
        uP: array-like
            vector that indicates the amount of energy before losses to obtain 1kWh of consumable elec
        prod_means: array-like
            list of production means, without mixes
        residual: bool, default to False
            if residual are considered
        freq: str, default to 'H'
            frequency of a time step
        is_verbose: bool, default to False
            show text during computation.
    
    Returns
    -------
    pandas.DataFrame
        table with the electricity mix in the studied countries (parameter.ctry + 'Other'), containing each production mean of each country at each time step.
    """
    mixE = []

    if is_verbose:
        check_frequency(freq)
        step = {'15min': 96, '15T': 96, '30min': 48, '30T': 48, 'H': 24,
                'd': 7, 'D': 7, 'W': 1, 'w': 1, 'M': 1, 'MS': 1, 'Y': 1, 'YS': 1}[freq]
        step_name = {'15min': "day", '15T': "day", '30min': "day", '30T': "day", 'H': "day", 'd': "week",
                     'D': "week", 'W': 'week', 'w': 'week', 'M': "month", 'MS': "month", 'Y': "year", 'YS': "year"}[
            freq]
        total = np.ceil(data.shape[0] / step).astype('int32')  # total nb of steps to display
    else:
        step = data.shape[0]

    # For each considered step of time
    for t in range(data.shape[0]):

        if ((is_verbose) & (t % step == 0)):
            print(f"\tcompute for {step_name} {(t // step) + 1}/{total}   ", end="\r")

        ##############################################
        # Build the technology matrix A
        ##############################################
        A = build_technology_matrix(data.iloc[t], ctry, ctry_mix, prod_means)
        L = A.shape[0]

        #######################################################
        # Drop the empty columns and lines for easier inversion
        #######################################################
        A, presence = clean_technology_matrix(A)

        #########################################################
        # Inversion & reintegrtion of the empty lines and columns
        #########################################################
        Ainv = invert_technology_matrix(A, presence, L=L)

        mixE.append(pd.DataFrame(np.dot(Ainv, uP.iloc[t]), index=all_sources, columns=all_sources, dtype="float32"))

    #######################################################################
    # Clear columns related to residual in other countries than CH
    #######################################################################

    # Possibly non-used residue columns are deleted (Only residual for CH can be considered)
    if residual:
        mixE = [m.drop(columns=[k for k in m.columns
                                if ((k.split("_")[0] == "Residual") & (k[-3:] != "_CH"))])
                for m in mixE]
    mixE = pd.concat(mixE, axis=0, keys=data.index)
    return mixE


#
###############################################################################
# ###########################
# # Build technology matrix
# ###########################
# ###########################
#

def build_technology_matrix(data, ctry, ctry_mix, prod_means):
    """Function building the technology matrix based on the production and exchange data.

    Parameters
    ----------
        data: pandas.DataFrame
            the production and exchange data
        ctry: array-like
            sorted list of involved countries
        ctry_mix: array-like
            list of countries where eletricity can come from, including 'Other'
        prod_means: array-like
            list of production means, without mixes

    Returns
    -------
    numpy.ndarray
       technology matrix A
    """
    # Gathering production by country in a matrix
    energy = pd.DataFrame(data=data.values.reshape((len(ctry), len(prod_means))),
                          columns=prod_means, index=ctry, dtype='float32')

    # Compute the contribution rate of each production unit in the production mix of each country
    weight = energy.div(energy.sum(axis=1), axis=0)

    # Shape parameters
    cm = 0  # anchor column number for the blocks containing data
    cM = len(ctry_mix)  # width of the block containing data
    height = len(prod_means) - len(ctry_mix)  # height data block with generation without exchange
    L = len(ctry_mix) + height * len(ctry)  # Shape of technology matrix

    # Building and calculation of the technology matrix A for this specific step of time
    # shapes of the A matrix
    A = np.zeros((L, L))

    # set production data one country after another
    for i in range(len(ctry)):
        # Calculate appropriate position in A
        i_mix = ctry_mix.index(ctry[i])  # indices of the location's order of countries
        lm = cM + i * (height)  # upper limit of the cosidered data block
        lM = lm + (height)  # lower limit of the cosidered data block
        # Replacement
        A[lm:lM, cm + i_mix] = weight.loc[ctry[i]].iloc[:height].values  # Column by column

    # set link between mixes (contribution of a mix to another --> cross-border flows contribution)
    A[cm:cM, cm:cM - 1] = weight.loc[ctry, [f"Mix_{k}" for k in ctry_mix]].T.values

    return A


#
###############################################################################
# ###########################
# # Clean technology matrix
# ###########################
# ###########################
#

def clean_technology_matrix(A):
    """Reduce the size of the technology matrix. As the matrix A is a square matrix, for all indexes i
    where the i-th row AND the i-th column are both full of zeros, both row and column i are dropped.
    All other indexes j are written in the list 'presence', and the row and column j is kept in A.
    """
    ###############################################
    # drop the empty columns and line for inversion
    ###############################################
    presence_line = pd.Series(A.sum(axis=1) != 0)  # The lines not full of zeros (true or false)
    presence_cols = pd.Series(A.sum(axis=0) != 0)  # The columns not full of zeros (true or false)

    presence = np.logical_or(presence_line, presence_cols)  # keep if value on a line or column
    presence = presence[presence.values == True].index  # lines and columns to keep (indexes)
    A = A[presence, :][:, presence]  # select only the non-empty lines and columns

    return A, presence


#
###############################################################################
# ###########################
# # Invert technology matrix
# ###########################
# ###########################
#

def invert_technology_matrix(A, presence, L):
    """Track the electric mix: it consists in computing (Id - A)⁻¹

    Parameters
    ----------
        A: numpy.array
            technology matrix at one time step
        presence: list-like
            list of indexes to replace the computation results in their context
        L: int
            the size of the results (and original A, before it was cleaned)

    Returns
    -------
    numpy.array
        matrix (Id - A)⁻¹ of shape (L, L)
    """
    ##########################################################
    # Inversion & reintegrtion of the empty lines and columns
    #########################################################
    Ainv = np.zeros((L, L))  # storage matrix
    m = np.linalg.inv(np.eye(len(presence)) - A)  # inversion
    k_m = 0
    for i in presence:
        Ainv[i, presence] = m[k_m]  # set for each concerned line the columns to fill
        k_m += 1

    return Ainv
