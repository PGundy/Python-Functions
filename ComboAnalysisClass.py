## Project idea to expand on:
## class object called hotspot
## inputs would be
### data -- could
##
## methods
### return column names or the list given to data -- view options
### select column names or items from the list -- set input list
### set depth_maximum
### generate list of the combinations -- options could include whether to return all or only alphanumeric sorted options

# import example_module_name
# EX = example_module_name(data = [])
# EX.viewOption()
# EX.setOptions()
# EX.setDepthMax()
# EX.generatecombinations()

#%%
import itertools

#%%
import numpy as np
import pandas as pd

#%%


class ComboAnalysis:
    inputList: list
    depthMax: int
    data: pd.DataFrame

    def __init__(self, inputList=None, depthMax=None, data=None):
        self.inputList = inputList
        self.depthMax = depthMax
        self.data = data

    ## check the input values
    def checkInputs(self):
        print("Below are the currently defined inputs:")
        print("     inputList:", self.inputList)
        print("     depthMax:", self.depthMax)
        print("     data:", self.data)

    ## get the list of alphanumerically sorted combinations
    def generateCombos(self):

        if self.inputList is None:
            raise ValueError("inputList is set to None")
        if self.depthMax is None:
            raise ValueError("depthMax is set to None")

        ##define the interim objects
        combination_final = []

        for i in np.arange(0, self.depthMax, 1) + 1:
            combinations = list(
                itertools.combinations(self.inputList, int(i))
            )
            combinations = list(map(list, combinations))
            combinations.sort()
            ##print(
            ##    "combinations with element length",
            ##    i,
            ##    "have",
            ##    len(combinations),
            ##    "variations.",
            ##)

            ## Build up nested list of all combinations
            # combination_interim.append(combinations)
            combination_final = [*combination_final, combinations]

            if i == self.depthMax:
                ## unnest the combinations
                combination_final = list(
                    itertools.chain.from_iterable(combination_final)
                )
                print(
                    "In total there are",
                    len(combination_final),
                    "combinations with a depthMax max of",
                    self.depthMax,
                )

                return list(filter(None, combination_final))

    ## Iterate using userFunc & data using groupby(Combos)
    def ComputeCombos(self, generatedCombos, userFunc):
        result = []
        resultList = []
        for step_i, grp_var_i in enumerate(generatedCombos):
            print(
                "Step:",
                step_i,
                "of",
                len(generatedCombos) - 1,
                " -- Grouped by:",
                grp_var_i,
            )

            ## Run the calculations for each step
            groupedData = self.data.groupby(grp_var_i)
            result = userFunc(groupedData)

            ## Create variables to create 'clean' columns
            result_col_names = list(result.columns)
            result.reset_index(inplace=True)

            ### Create the easy to read variables
            ## Count of interactions
            result["depth"] = len(grp_var_i)

            ## pd.Series of list(relevant variable names)
            result["grouped_vars"] = pd.Series([grp_var_i] * len(result))

            ## pd.Series of the corresponding variable's values
            result["grouped_values"] = result[grp_var_i].apply(
                lambda row: list(row.values.astype(str)), axis=1
            )

            ### Create the list zip("grouped_vars","grouped_values")
            for row in np.arange(0, len(result), 1):

                ## create empty pd.Series t
                if row == 0:
                    result["grouped_clean"] = pd.Series(dtype=str)

                ###
                ### KNOWN BUG WITH CHAINED INDEXING
                ###
                ### TODO: Is this solvable with pd.Series of lists?
                ###
                result["grouped_clean"][row] = [
                    i + ": " + j + ""
                    for i, j in zip(
                        result["grouped_vars"].iloc[row],
                        result["grouped_values"].iloc[row],
                    )
                ]

                ## Select & order our final columns
                result = result[
                    list(
                        [
                            "depth",
                            "grouped_vars",
                            "grouped_values",
                            "grouped_clean",
                        ]
                    )
                    + result_col_names
                ]

            ## Final step in the loop
            resultList.append(result)
            result = []
        return pd.concat(resultList).reset_index(drop=True)

    ## Return all rows for a variable to see the content of the variable
    def getVarContents(self, data, varNames):
        if isinstance(varNames, str):
            varNames = [varNames]
        temp = data[data["grouped_vars"].apply(set(varNames).issuperset)]
        temp = temp[temp["depth"].isin([1])]
        return temp

    ## Filter to rows to any input variables
    def FilterListBroadly(
        self, data, columnToSearch: str, searchList, depth_filter=None
    ):
        if isinstance(searchList, str):
            searchList = [searchList]

        searchResult = []
        for searchTerm in searchList:
            searchResult.append(
                data[[searchTerm in x for x in data[columnToSearch]]]
            )
        searchResult = pd.concat(searchResult)
        if depth_filter is not None:
            searchResult = searchResult[
                searchResult["depth"].isin([depth_filter])
            ]
        searchResult.sort_values("depth", ascending=True, inplace=True)
        ## TODO: Is it better to reset the index or not?
        ##searchResult.reset_index(inplace=True, drop=True)
        return searchResult.copy()

    ## Filter rows in a more strict manner. Only complete matches
    def FilterListStrictly(
        self, data, columnToSearch: str, searchList, depth_filter=None
    ):
        if isinstance(searchList, str):
            searchList = [searchList]

        ## return error if not list
        if not isinstance(searchList, list):
            ValueError(
                "The object provided to search_list is not a list. Nor a string capable of being transformed into a list"
            )

        searchResult = []
        searchResult = data[
            data[columnToSearch].apply(set(searchList).issuperset)
        ]

        if depth_filter is not None:
            searchResult = searchResult[
                searchResult["depth"].isin([depth_filter])
            ]

        searchResult.sort_values("depth", ascending=True, inplace=True)
        ## TODO: Is it better to reset the index or not?
        ##searchResult.reset_index(inplace=True, drop=True)
        return searchResult.copy()

    def listToString(self, inputList, delimiter=None):
        delimiter: str

        if delimiter is None:
            delimiter = " -- "

        return inputList.apply(lambda x: delimiter.join(map(str, x)))


# %%

if __name__ == "__main__":

    import seaborn as sns

    df = sns.load_dataset("diamonds")
    df_key_vars = list(df.select_dtypes(include=["category"]).columns)

    CA = ComboAnalysis()
    CA.inputList = df_key_vars
    CA.depthMax = 3
    CA.data = df

    comboAnalysisList = CA.generateCombos()

    ###################################
    # Below are examples evaluating the comboAnalysis
    ###################################

    ## create the user defined summary function
    ### Key things
    ### (1) 'data' is the only argument
    ### (2) this function must work for the entire dataset (or sample)
    def exampleFunction(data):
        return data.agg(
            count=pd.NamedAgg("price", "count"),
            size=pd.NamedAgg("price", "size"),
            avg_price=pd.NamedAgg("price", np.mean),
            med_price=pd.NamedAgg("price", np.median),
        )

    ComboAnalysisOutput = CA.ComputeCombos(
        generatedCombos=CA.generateCombos(), userFunc=exampleFunction
    )
    ComboAnalysisOutput.sample(n=5)

    ## Example of how to view contents of any particular variable
    CA.getVarContents(data=ComboAnalysisOutput, varNames="color")

    ## Return all rows where 'color' appears - 54 rows
    CA.FilterListBroadly(
        data=ComboAnalysisOutput,
        columnToSearch="grouped_clean",
        searchList="color: H",
    )

    ## Return all rows where ONLY 'color' appears - only 1 row
    CA.FilterListStrictly(
        data=ComboAnalysisOutput,
        columnToSearch="grouped_clean",
        searchList="color: H",
    )

    ## Return all rows with these values
    CA.FilterListBroadly(
        data=ComboAnalysisOutput,
        columnToSearch="grouped_clean",
        searchList=["color: H", "color: D", "cut: Very Good"],
    )

    ## Return only rows with these values -- Note the interactions
    CA.FilterListStrictly(
        data=ComboAnalysisOutput,
        columnToSearch="grouped_clean",
        searchList=["color: H", "color: D", "cut: Very Good"],
    )

    ## Example of multistep filtering
    ### Step 1 Limit to any row with 'cut'
    filter_df_step1 = CA.FilterListBroadly(
        data=ComboAnalysisOutput,
        columnToSearch="grouped_vars",
        searchList="cut",
    )

    ### Step 2 limit to all rows of 'color:H' from rows with 'cut'
    filter_df_step2 = CA.FilterListBroadly(
        data=filter_df_step1,
        columnToSearch="grouped_clean",
        searchList="color: H",
    )
    filter_df_step2
    ## Example of converting lists to delimited string
    CA.listToString(ComboAnalysisOutput["grouped_clean"].tail(5))
    CA.listToString(
        ComboAnalysisOutput["grouped_clean"].tail(5), delimiter="; "
    )


# %%
