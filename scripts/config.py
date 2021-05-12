GEOMETRY_TYPE = 'Polygon'
# Add ALL option to both the metrics
METRICS = ['cluster_number', 'Dlimit', 'minimum_cluster_distance', 'hindex',
           'total_perimeter','total_area', 'area_ratio', #'area_ratio_cell',  # 'distance_matrix',
           #'clusters_at_distance', 'clusters_at_percent_distance',
           'distance_matrix_mean', #'distance_matrix_sum'
           ]
PROCESS_METRICS = ['xy', 'total_sum', 'total_nr_sum',
                   'max_variation', 'iter_max_variation',
                   'clusters_reduction_distance']
CANVAS = (600, 600)
