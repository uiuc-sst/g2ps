This directory contains data relevant to normalizing pronlexes from a variety of sources, 
and then training finite state transducer G2Ps using Phonetisaurus.

python normalize_dicts.py lists /tmp/dicts

python make_folds.py /tmp/dicts /tmp bad_dicts.txt

## not working yet: python align_corpora.py traindir modelsdir logdir

train_g2ps.sh

python generate_models_column.py /tmp/models /tmp/dev /tmp/dev_hyps


