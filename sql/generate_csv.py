import numpy as np
import csv

from create_sqlite import create_connection
from insert_sqlite import get_all_indexes
from collections import defaultdict
from statistics import geometric_mean
from statistics import mean

# 64-bit datasets
XS_SIZE = 1.6e5
S_SIZE = 1.6e6
M_SIZE = 1.6e7
L_SIZE = 1.6e8

# 32-bit datasets
XS_SIZE_32 = 8e4
S_SIZE_32 = 8e5
M_SIZE_32 = 8e6
L_SIZE_32 = 8e7

def rec_dd():
    """ Recursive nested defaultdict generating function """
    return defaultdict(rec_dd)

def get_ranked_indexes(dbname):
    build_times = rec_dd()
    latencies = rec_dd()
    sizes = rec_dd()
    conn = create_connection(dbname)
    all_indexes = get_all_indexes(conn)

    # Dictionaries have structure name -> size -> dataset -> variant -> time of that variant
    # First we'll process to get the lowest-latency variant on each dataset, then take the geometric
    # mean across datasets which gives us name -> size -> mean latency across datasets
    for entry_id, name, variant, latency, size, build_time, searcher, dataset in all_indexes:
        # Could have been multiple runs for latency

        size_category = ''
        if 'uint64' in dataset:
            if size == 0:
                # on-the-fly algorithm, put the latency in medium
                size_category = 'm'
            elif size < XS_SIZE:
                size_category = 'xs'
            elif size < S_SIZE:
                size_category = 's'
            elif size < M_SIZE:
                size_category = 'm'
            elif size < L_SIZE:
                size_category = 'l'
            else:
                size_category = 'xl'
        elif 'uint32' in dataset:
            if size == 0:
                # on-the-fly algorithm, put the latency in medium
                size_category = 'm'
            elif size < XS_SIZE_32:
                size_category = 'xs'
            elif size < S_SIZE_32:
                size_category = 's'
            elif size < M_SIZE_32:
                size_category = 'm'
            elif size < L_SIZE_32:
                size_category = 'l'
            else:
                size_category = 'xl'
        else:
            raise ValueError("Dataset name does not contain data type")
        
        build_times[name][size_category][dataset][variant] = build_time
        latencies[name][size_category][dataset][variant] = latency
        sizes[name][size_category][dataset][variant] = size

    for index_name in build_times:
        for size_cat in build_times[index_name]:
            for dataset_name in build_times[index_name][size_cat]:
                lowest_latency_variant = min(latencies[index_name][size_cat][dataset_name],
                    key = latencies[index_name][size_cat][dataset_name].get)
                build_times[index_name][size_cat][dataset_name] = build_times[index_name][size_cat][dataset_name][lowest_latency_variant]
                latencies[index_name][size_cat][dataset_name] = latencies[index_name][size_cat][dataset_name][lowest_latency_variant]
                sizes[index_name][size_cat][dataset_name] = sizes[index_name][size_cat][dataset_name][lowest_latency_variant]

    for index_name in build_times:
        for size_cat in build_times[index_name]:
            # Possibly filed with zeros
            if all(build_times[index_name][size_cat].values()):
                build_times[index_name][size_cat] = mean(build_times[index_name][size_cat].values())
            else:
                build_times[index_name][size_cat] = None
            latencies[index_name][size_cat] = mean(latencies[index_name][size_cat].values())
            if all(sizes[index_name][size_cat].values()):
                sizes[index_name][size_cat] = mean(sizes[index_name][size_cat].values())
            else:
                sizes[index_name][size_cat] = None
    
    return latencies, build_times, sizes
    
def get_size_str(size):
    if size < 1e6:
        return str(round(size/1000, 2)) + " KB"
    elif size < 1e9:
        return str(round(size/1e6, 2)) + " MB"
    else:
        return str(round(size/1e9, 2)) + " GB"

if __name__ == "__main__":
    db = r"./indexes.db"
    
    latencies, build_times, sizes = get_ranked_indexes(db)
    headers = ["Name", "XS", "S", "M", "L", "XL"]
    with open("./_data/latency.csv", "w") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(headers)
        for index in latencies:
            writer.writerow([
                index,
                round(latencies[index]['xs']) if 'xs' in latencies[index] and latencies[index]['xs'] is not None else ' ',
                round(latencies[index]['s']) if 's' in latencies[index] and latencies[index]['s'] is not None else ' ',
                round(latencies[index]['m']) if 'm' in latencies[index] and latencies[index]['m'] is not None else ' ',
                round(latencies[index]['l']) if 'l' in latencies[index] and latencies[index]['l'] is not None else ' ',
                round(latencies[index]['xl']) if 'xl' in latencies[index] and latencies[index]['xl'] is not None else ' '
            ])
    
    with open("./_data/buildtimes.csv", "w") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(headers)
        for index in build_times:
            writer.writerow([
                index,
                round(build_times[index]['xs']) if 'xs' in build_times[index] and build_times[index]['xs'] is not None else ' ',
                round(build_times[index]['s']) if 's' in build_times[index] and build_times[index]['s'] is not None else ' ',
                round(build_times[index]['m']) if 'm' in build_times[index] and build_times[index]['m'] is not None else ' ',
                round(build_times[index]['l']) if 'l' in build_times[index] and build_times[index]['l'] is not None else ' ',
                round(build_times[index]['xl']) if 'xl' in build_times[index] and build_times[index]['xl'] is not None else ' '
            ])
    
    with open("./_data/sizes.csv", "w") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(headers)
        for index in sizes:
            writer.writerow([
                index,
                get_size_str(sizes[index]['xs']) if 'xs' in sizes[index] and sizes[index]['xs'] is not None else ' ',
                get_size_str(sizes[index]['s']) if 's' in sizes[index] and sizes[index]['s'] is not None else ' ',
                get_size_str(sizes[index]['m']) if 'm' in sizes[index] and sizes[index]['m'] is not None else ' ',
                get_size_str(sizes[index]['l']) if 'l' in sizes[index] and sizes[index]['l'] is not None else ' ',
                get_size_str(sizes[index]['xl']) if 'xl' in sizes[index] and sizes[index]['xl'] is not None else ' '
            ])