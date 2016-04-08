## CARIE: Computational Analysis of Retained Intron Events

Requirements
------------
1. Install Python 2.7.x and corresponding versions of NumPy and
SciPy.
2. Add the Python directory to the $PATH environment variable.

Installation:
------------
The source code can be directly called from Python.

Usage:
--------------------------------

    $ python CARIE.py --GTF ./test.gtf -i ./test_R1.bam,./test_R2.bam,./control_R1.bam,./control_R2.bam --anchor 8 --length 100 --lib unstrand --read P --type All --comparison ./comparison -o ./bam --analysis U

Required Parameters:
------------
-i/--input:
	s1.bam/s1.sam[,s2.bam/s2.sam]. Mapping results for all of samples in bam/sam format. Different samples  are sepreated by commas
--GTF:
	The gtf file
	
	 -r *       reference genome (Fasta)
 -s *       read sequences, either single or paired end
 -o *       output directory 
 -T         number of threads STAR uses, default is 8
 -M         max number of multiple alignments, default is 20
 -N         max number of read mismatches, default is 3
 --gz       flag denoting sequence reads are gzipped
    
