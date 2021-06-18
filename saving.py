import pandas


# +

##########################
# #########################
# Save impact vector
# #########################
# #########################
# -

def save_impact_vector(impact_matrix, savedir, cst_import=False, residual=False):
    """Function to save the impact matrix.
    Parameter:
        impact matrix: the table with the impact factors (pandas DataFrame)
        savedir: the directory where to save (str)
        cst_import: if constant exchange impacts are considered (bool, default: False)
        residual: if a residual is considered (bool, default: False)
    """
    add_on = ""
    if cst_import: add_on += "_CstImp"
    if residual: add_on += "_Res"
    file_name = f"Impact_Vector{add_on}.csv"
    
    impact_matrix.to_csv(savedir + file_name, sep=";", index=True)


# +
##########################
# #########################
# Save Dataset
# #########################
# #########################
# -

def save_dataset(data, savedir, name, target=None, freq='H'):
    """Function to save the datasets with information of the frequency.
    
    Parameter:
        data: the dataset (pandas DataFrame)
        savedir: the directory where to save (str)
        name: the name of the file (excluding extension and frequency info) (str)
        freq: the frequency (str)
    """
    ### Formating the time extension
    tPass = {'15min':'15min','30min':'30min',"H":"hour","D":"day",'d':'day','W':"week",
             "w":"week","MS":"month","M":"month","YS":"year","Y":"year"}
    as_target = "" if target is None else f"_{target}"
    
    ### Saving
    data.to_csv(savedir+f"{name}{as_target}_{tPass[freq]}.csv",sep=";",index=True)
