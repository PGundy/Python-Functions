#%% packages
import numpy as np
import itertools


#%%


def alpha_numeric_ordered_permutations(input_list, permutation_depth_max=None):
    """Generate permutations, sort each permutation alphanumerically and return the unique permutations.
    
    input_list -- np.array, index, list, etc.
    permutation_depth_max -- The maximum length of the permutations. Default is len(input_list).
    
    
    Example: 
        alpha_numeric_ordered_permutations(input_list = list(["a", "b", "c"]), permutation_depth_max=2)
        would return: [[a], [b], [a,b], [a,c], [b,c]]
        
        
    Example loop on function output:
        for i in range(len(permutation_final)):
        print("Step", i, "grouping on:", permutation_final[i])"""
    permutation_interim = []
    permutation_final = []

    if permutation_depth_max is None:
        permutation_depth_max = len(input_list)

    if permutation_depth_max > 7:
        print(
            "Having a permutation_depth_max of",
            permutation_depth_max,
            "will take several minutes to compute.",
            "\nIt is suggested to keep permutation_depth_max under 7.",
        )

    for i in np.arange(0, permutation_depth_max, 1) + 1:
        permutations = list(itertools.permutations(input_list, int(i)))
        permutations = list(map(list, permutations))
        permutations = list(map(sorted, permutations))
        ## Convert our sorted sub-lists into unique tuples using set() & then back to lists
        permutations = [list(x) for x in set(tuple(x) for x in permutations)]
        permutations.sort()
        print(
            "Permutations with element length",
            i,
            "have",
            len(permutations),
            "variations.",
        )

        ## Build up nested list of all permutations
        # permutation_interim.append(permutations)
        permutation_interim = [*permutation_interim, permutations]

        if i == permutation_depth_max:
            ## unnest the permutations
            permutation_final = list(itertools.chain.from_iterable(permutation_interim))
            print(
                "In total there are",
                len(permutation_final),
                "permutations with a permutation_depth_max max of",
                permutation_depth_max,
            )
            return permutation_final


#%%
if __name__ == "__main__":

    test_list1 = ["a", "b", "c", "d"]
    test_list2 = [4, 2]

    print("\n\n\nNow for test_list1\n\n")
    test1 = alpha_numeric_ordered_permutations(
        input_list=test_list1, permutation_depth_max=2
    )

    ##TODO: understand why pylance errors out on example 2: "Object of type "None" cannot be used as iterable value"
    ## Example with no pylance issue:
    for i in list(filter(None, test1)):
        print(i)

    # ? ## Example of issue with None:
    # ? for i in test1:
    # ?     print(i)
    # ? https://pythoncircle.com/post/708/solving-python-error-typeerror-nonetype-object-is-not-iterable/
    # ? Possible work around is to avoid aList.append() as a way to aggregate the lists

    print("\n\n\nNow for test_list2\n\n")
    test2 = alpha_numeric_ordered_permutations(
        input_list=test_list2, permutation_depth_max=2
    )

    for i in list(filter(None, test2)):
        print(i)


# %%
