'''
This protocol should take a csv file that has the sample names and the concentrations of the RNA samples. 
It should then dilute the RNA to 100 ng/ul if it is at a higher concentration. Then it should make cDNA for the samples.


	                            1x
RNA (from above)	            3
5X RT Buffer	                1
Random hexamers, 50 ng/µl	    0.125
Oligo dT, 100 µM	            0.125
dNTP, 10 mM	                    0.25
RNase inhibitor (eg. RNaseOUT)	0.125
Water, nuclease-free	        0.375

'''

