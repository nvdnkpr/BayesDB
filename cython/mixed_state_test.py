import argparse
#
import pylab
import numpy
#
import tabular_predDB.cython.State as State
import tabular_predDB.cython.gen_data as gen_data


# parse input
parser = argparse.ArgumentParser()
parser.add_argument('--gen_seed', default=0, type=int)
parser.add_argument('--inf_seed', default=0, type=int)
parser.add_argument('--num_clusters', default=4, type=int)
parser.add_argument('--num_cols', default=2, type=int)
parser.add_argument('--num_rows', default=20, type=int)
parser.add_argument('--num_splits', default=1, type=int)
parser.add_argument('--max_mean', default=10, type=float)
parser.add_argument('--max_std', default=0.3, type=float)
parser.add_argument('--num_transitions', default=10, type=int)
parser.add_argument('--N_GRID', default=31, type=int)
args = parser.parse_args()
#
gen_seed = args.gen_seed
inf_seed = args.inf_seed
num_clusters = args.num_clusters
num_cols = args.num_cols
num_rows = args.num_rows
num_splits = args.num_splits
max_mean = args.max_mean
max_std = args.max_std
num_transitions = args.num_transitions
N_GRID = args.N_GRID

# create the data
if True:
    T, M_r, M_c = gen_data.gen_factorial_data_objects(
        gen_seed, num_clusters,
        num_cols, num_rows, num_splits,
        max_mean=max_mean, max_std=max_std,
        )
else:
    with open('SynData2.csv') as fh:
        import numpy
        import csv
        T = numpy.array([
                row for row in csv.reader(fh)
                ], dtype=float).tolist()
        M_r = gen_data.gen_M_r_from_T(T)
        M_c = gen_data.gen_M_c_from_T(T)

T_array = numpy.array(T)
multinomial_idx = 1
multinomial_column = numpy.array(T_array[:,multinomial_idx], dtype=int)
multinomial_set = set(multinomial_column)
T_array[:, multinomial_idx] = multinomial_column
multinomial_column_metadata = M_c['column_metadata'][multinomial_idx]
code_to_value = dict(zip(list(multinomial_set), list(multinomial_set)))
value_to_code = dict(zip(list(multinomial_set), list(multinomial_set)))
multinomial_column_metadata['modeltype'] = 'symmetric_dirichlet_discrete'
multinomial_column_metadata['code_to_value'] = code_to_value
multinomial_column_metadata['value_to_code'] = value_to_code

# create the state
p_State = State.p_State(M_c, T, N_GRID=N_GRID, SEED=inf_seed)
p_State.plot_T()

# transition the sampler
print "p_State.get_marginal_logp():", p_State.get_marginal_logp()
for transition_idx in range(num_transitions):
    print "transition #: %s" % transition_idx
    p_State.transition()
    counts = [
        view_state['row_partition_model']['counts']
        for view_state in p_State.get_X_L()['view_state']
        ]
    format_list = '; '.join([
            "s.num_views: %s",
            "cluster counts: %s",
            "s.column_crp_score: %.3f",
            "s.data_score: %.1f",
            "s.score:%.1f",
            ])
    values_tuple = (
        p_State.get_num_views(),
        str(counts),
        p_State.get_column_crp_score(),
        p_State.get_data_score(),
        p_State.get_marginal_logp(),
        )
    print format_list % values_tuple    
    iter_idx = transition_idx if transition_idx % 10 == 0 else None
    p_State.plot(iter_idx=iter_idx)
