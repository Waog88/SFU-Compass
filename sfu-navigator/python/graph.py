# ============================================================
# SFU Campus Graph
#
# Each node is:
#
# node -> {neighbor: distance_in_metres}
#
# Hidden nodes represent routing junctions and do not
# necessarily appear to the user.
#
# IMPORTANT:
# Distances are approximate prototype values.
# Verify important routes on-site.
# ============================================================


GRAPH = {

    "WMC": {
        "WMC_EAST": 25,
    },

    "WMC_EAST": {
        "WMC": 25,
        "LIBRARY_WEST": 120,
    },

    "LIBRARY_WEST": {
        "WMC_EAST": 120,
        "Library": 25,
        "CONVOCATION_WEST": 55,
    },

    "Library": {
        "LIBRARY_WEST": 25,
        "SUB": 70,
    },

    "SUB": {
        "Library": 70,
        "CONVOCATION_WEST": 55,
    },

    "CONVOCATION_WEST": {
        "LIBRARY_WEST": 55,
        "SUB": 55,
        "CONVOCATION_CENTRE": 60,
    },

    "CONVOCATION_CENTRE": {
        "CONVOCATION_WEST": 60,
        "MBC": 35,
        "AQ_WEST": 45,
    },

    "MBC": {
        "CONVOCATION_CENTRE": 35,
        "AQ_WEST": 45,
    },

    "AQ_WEST": {
        "CONVOCATION_CENTRE": 45,
        "MBC": 45,
        "AQ": 25,
        "AQ_SOUTH": 70,
    },

    "AQ": {
        "AQ_WEST": 25,
        "AQ_SOUTH": 55,
    },

    "AQ_SOUTH": {
        "AQ": 55,
        "AQ_WEST": 70,
        "SHRUM_NORTH": 45,
    },

    "SHRUM_NORTH": {
        "AQ_SOUTH": 45,
        "Shrum Chemistry": 30,
        "Shrum Physics": 40,
        "SHRUM_SOUTH": 60,
    },

    "Shrum Chemistry": {
        "SHRUM_NORTH": 30,
        "Shrum Physics": 45,
    },

    "Shrum Physics": {
        "SHRUM_NORTH": 40,
        "Shrum Chemistry": 45,
        "Shrum Biology": 55,
        "SHRUM_SOUTH": 45,
    },

    "Shrum Biology": {
        "Shrum Physics": 55,
        "SHRUM_SOUTH": 35,
    },

    "SHRUM_SOUTH": {
        "SHRUM_NORTH": 60,
        "Shrum Physics": 45,
        "Shrum Biology": 35,
        "South Sciences": 35,
        "ASB_WEST": 65,
    },

    "South Sciences": {
        "SHRUM_SOUTH": 35,
        "ASB_WEST": 50,
    },

    "ASB_WEST": {
        "SHRUM_SOUTH": 65,
        "South Sciences": 50,
        "ASB": 25,
        "TASC_JUNCTION": 85,
    },

    "ASB": {
        "ASB_WEST": 25,
        "TASC_JUNCTION": 75,
    },

    "TASC_JUNCTION": {
        "ASB_WEST": 85,
        "ASB": 75,
        "TASC1": 35,
        "TASC2": 55,
    },

    "TASC1": {
        "TASC_JUNCTION": 35,
        "TASC2": 50,
    },

    "TASC2": {
        "TASC_JUNCTION": 55,
        "TASC1": 50,
    },
}