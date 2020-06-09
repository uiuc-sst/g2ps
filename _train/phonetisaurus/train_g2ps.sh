#/bin/sh -e

mkdir -p /tmp/models
mkdir -p /tmp/dev_wlists
mkdir -p /tmp/dev_hyps
mkdir -p /tmp/logs

#for f in akan; do
for f in `ls /tmp/train`; do
    L=`echo $f | sed 's/\.txt//'`
    echo '####################################################################################'
    echo $L
    echo '####################################################################################'
    echo 'align'

    for seq1_max in 2 3 4; do
	for seq2_max in 2 3 4; do
	    for model_order in 1 2 4 8; do
		modelname=${L}_${model_order}_${seq1_max}_${seq2_max}
	
		echo phonetisaurus-align --input=/tmp/train/${L}.txt --ofile=/tmp/models/${modelname}.corpus --seq1_del=false --seq2_del=false --seq1_max=$seq1_max --seq2_max=$seq2_max --grow=true &> /tmp/logs/${L}_align.log
		phonetisaurus-align --input=/tmp/train/${L}.txt --ofile=/tmp/models/${modelname}.corpus --seq1_del=false --seq2_del=false --seq1_max=$seq1_max --seq2_max=$seq2_max --grow=true >> /tmp/logs/${L}_align.log 2>&1
		
		
		echo estimate-ngram -o $model_order -t /tmp/models/${modelname}.corpus -wl /tmp/models/${modelname}.arpa &> /tmp/logs/${modelname}_estimate.log
		estimate-ngram -o $model_order -t /tmp/models/${modelname}.corpus -wl /tmp/models/${modelname}.arpa
		>> /tmp/logs/${modelname}_estimate.log 2>&1
		
		if [ -f /tmp/models/${modelname}.arpa ]; then
		    echo phonetisaurus-arpa2wfst --lm=/tmp/models/${modelname}.arpa --ofile=/tmp/models/${modelname}.fst &> /tmp/logs/${modelname}_arpa2wfst.log
		    phonetisaurus-arpa2wfst --lm=/tmp/models/${modelname}.arpa --ofile=/tmp/models/${modelname}.fst >> /tmp/logs/${modelname}_arpa2wfst.log  2>&1
		    if [ -f /tmp/models/${modelname}.fst ]; then
			if [ -f /tmp/dev/${L}.txt ]; then
			    echo "test ${modelname}"
			    awk '{print $1}' /tmp/dev/${L}.txt > /tmp/dev_wlists/${L}.wlist
			    echo phonetisaurus-g2pfst --model=/tmp/models/${modelname}.fst --nbest=1 --beam=10000 --thresh=99.0 --accumulate=false --pmass=0.0 --nlog_probs=true --wordlist=/tmp/dev_wlists/${L}.wlist > /tmp/logs/${modelname}_g2pfst.log
			    phonetisaurus-g2pfst --model=/tmp/models/${modelname}.fst --nbest=1 --beam=10000 --thresh=99.0 --accumulate=false --pmass=0.0 --nlog_probs=true --wordlist=/tmp/dev_wlists/${L}.wlist > /tmp/dev_hyps/${modelname}.txt 2>/tmp/logs/${modelname}_g2pfst.log
			fi
		    fi
		fi
	    done
	done
    done

    echo ''
done


