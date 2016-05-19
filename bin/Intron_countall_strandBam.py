#!/bin/python
import getopt,copy,re,os,sys,logging,time,datetime;
import pysam,os.path
options, args = getopt.getopt(sys.argv[1:], 'o:',['gtf=','anchor=','lib=','read=','length=','bam=','output='])
gtf='';
read='';
bam='';
lib='';
length =0
anchor =0
output='';
for opt, arg in options:
	if opt in ('-o','--output'):
		output = arg
	elif opt in ('--gtf'):
		gtf = arg
	elif opt in ('--bam'):
                bam = arg
	elif opt in ('--lib'):
                lib = arg
	elif opt in ('--read'):
                read = arg
	elif opt in ('--length'):
                length= int(arg)
	elif opt in ('--anchor'):
                anchor= int(arg)
if (not gtf or not read or not bam or not output or not length or not anchor):
	print "Not enough parameters!"
	print "Program : ", sys.argv[0]
	print "          A python program to count the reads for retained intron events for varities of junction from a series of bam file."
	print "Usage :", sys.argv[0], " --gtf: the intron gtf file;"
	print "Usage :", sys.argv[0], " --length:the length of reads;"
	print "Usage :", sys.argv[0], " --anchor:the anchor length of the read;"
	print "Usage :", sys.argv[0], " --bam: the bam file,multiple bam file seperated by commas;"
	print "Usage :", sys.argv[0], " --lib: the library type;"
	print "Usage :", sys.argv[0], " --read: The sequencing strategy of producing reads with choices of P/S;"
	print "Usage :", sys.argv[0], ' --output: intron_id, gene_id,strand,chr,start,end,5SS inclusion counts,5SS skipping counts,3SS includion counts,3SS skipping counts,skipping counts,intron counts.'
	print datetime.datetime.now()
	print "Author  : Shaofang Li"
	print "Contact : sfli001@gmail.com"
	sys.exit()
if(lib=="unstrand"):
	fr1 = open(gtf)
	count = dict()
	#the dict to store the intron count,first is the inclusion at left side, second is the skipped count at smaller side, third inclusion at right side, fourth skipping at right side, fifith skipping counts, sixth intron counts, at the end of the three column store gene_id, gene_strand, and clean introns based on bam files
	ppL = dict()
	#the dict to store left edge  position of intron
	ppR = dict()
	#the dict to store right  edge  position of intron
	pp = dict()
	#the dict to store the two edge position of intron
	pos = dict()
	# the dictionary to store the introns in a certain windows
	bin =1000
	# set the bin size
	bamfile = bam.split(",")
	num = len(bamfile)
	for info1 in fr1:
		a1 = info1.strip().split("\t")
		key = "%s_%s_%s" % (a1[0],a1[3],a1[4])
		gene_id = re.sub('.*gene_id "|\".*','',a1[8])
		if(count.has_key(key)):
			gg = count[key][6*num].split(",")
			gg_l = "true"
			for g_id in gg:
				if(gene_id == g_id):
					gg_l = "false"
			if(gg_l =="true"):
				count[key][6*num]+=","
				count[key][6*num]+=gene_id
				count[key][6*num+1]+=","
				count[key][6*num+1]+=a1[6]

		else:
			count[key]= [0]*num*6
			count[key].append(gene_id)
			count[key].append(a1[6])
			count[key].append("true")
			count[key].append("true")
			ppL.setdefault((a1[0],int(a1[3])),[]).append(key)
                	ppR.setdefault((a1[0],int(a1[4])),[]).append(key)
			pp[a1[0],int(a1[3]),int(a1[4])] = key
			index_s =  int(a1[3]) / bin
               		index_e =  int(a1[4]) / bin
                	for i in  range(index_s , index_e+1):
                        	pos.setdefault((a1[0],i),[]).append(key)
	fr1.close()
	bamfile = bam.split(",")
	nn = 0
	print bamfile
	for file in bamfile:
		print file
		path = "%s.bai" % file
		print path
		if (not os.path.exists(path)):
			cmd = "samtools index %s" % file
			print cmd
			os.system(cmd)
		fr2 = pysam.AlignmentFile(file, "rb")
		iter = fr2.fetch()
		for iter in fr2:
			if(read =="P"):
				if((iter.flag /2 )%2 ==0 ):
					continue
				if(iter.get_tag('NH')!=1):
					continue
				if(re.search("D|H|S",iter.cigarstring)):
					continue
				if(re.search("I",iter.cigarstring)):
                                        continue
			if(read =="S"):
                #                if(not re.search(str(iter.flag),"0,16")):
                 #                       continue
                                if(iter.get_tag('NH')!=1):
                                        continue
                                if(re.search("D|H|S",iter.cigarstring)):
                                        continue
                                if(re.search("I",iter.cigarstring)):
                                        continue
                        aa1 = iter.cigarstring.split("M")
                        aa2 = iter.cigarstring.split("N")
                        l = len(aa2)
			if(len(aa1)== 2):
				for p in range(iter.get_reference_positions()[0]+1 + anchor, iter.get_reference_positions()[0]+1 + int(aa1[0]) - anchor +1):
					if( fr2.getrname(iter.reference_id),p) in ppL:
						for id in ppL[ fr2.getrname(iter.reference_id),p]:
							#inclusion count at left side
							count[id][nn*6] +=1
							continue
				for p in range(iter.get_reference_positions()[0]+1 + anchor-1, iter.get_reference_positions()[0]+1 + int(aa1[0]) - anchor):
					if( fr2.getrname(iter.reference_id),p) in ppR:
                                                for id in ppR[ fr2.getrname(iter.reference_id),p]:
                                                        #inclusion count at right side
                                                        count[id][nn*6+2] +=1 
                                                        continue	
				index= (iter.get_reference_positions()[0]+1)/bin
                                if ( fr2.getrname(iter.reference_id), index) in pos:
                                        for key in pos[ fr2.getrname(iter.reference_id),index]:
						in_p = key.split("_")
                                                if ((int(in_p[1]) <= iter.get_reference_positions()[0]+1 )& (int(in_p[2])>= (iter.get_reference_positions()[0]+1 + length -1))):
                                                        count[key][nn*6+5]+=1
			start = iter.get_reference_positions()[0]+1
			for i in range(0,l-1):
				if(re.search("\D",aa2[i].split("M")[0])):
					continue
				if(re.search("\D",aa2[i].split("M")[1])):
					continue
				if(re.search("\D",aa2[i+1].split("M")[0])):
					continue
				n1=int(aa2[i].split("M")[0])
				n2=int(aa2[i].split("M")[1])
				n3=int(aa2[i+1].split("M")[0])
				if (n1 >= anchor and n3 >= anchor):
					
					index1 = (start+ n1-1)/ bin
					index2 = (start+ n1+n2)/bin
					if( fr2.getrname(iter.reference_id), index1) in pos:
						for key in pos[ fr2.getrname(iter.reference_id),index1]:
							in_p = key.split("_")
                					if ((int(in_p[1]) < start +n1 )& (int(in_p[2])> start +n1)):        
								count[key][num*6+2] ="false"
					if( fr2.getrname(iter.reference_id), index2) in pos:
                                                for key in pos[ fr2.getrname(iter.reference_id),index2]:
                                                        in_p = key.split("_")   
                                                        if ((int(in_p[1]) < start +n1+n2 -1 )& (int(in_p[2])> start +n1+n2 -1)):
                                                                count[key][num*6+2] ="false"

					if ( fr2.getrname(iter.reference_id), start+n1) in ppL:
						for id in ppL[ fr2.getrname(iter.reference_id),start +n1]:
							#skipped count at left side
							count[id][nn*6+1] +=1
					if ( fr2.getrname(iter.reference_id), start+n1+n2-1) in ppR:
                                                for id in ppR[ fr2.getrname(iter.reference_id),start +n1+n2 -1]:
                                                        #skipped count at right side
                                                        count[id][nn*6+3] +=1
					if ( fr2.getrname(iter.reference_id),start+n1, start+n1+n2-1) in pp:
						#skipping count at both side
        					count[pp[ fr2.getrname(iter.reference_id),start+n1,start +n1+n2 -1]][nn*6+4] +=1	

				if( n1 -anchor+1 >  anchor):
					ss = start
					for p in range( ss + anchor, ss + n1 -anchor+1 ):
						if( fr2.getrname(iter.reference_id),p) in ppL:
							for id in ppL[ fr2.getrname(iter.reference_id),p]:
								count[id][nn*6] +=1
					for p in range( ss + anchor-1, ss + n1 -anchor ):
                                                if( fr2.getrname(iter.reference_id),p) in ppR:
                                                        for id in ppR[ fr2.getrname(iter.reference_id),p]:
								#included count at right side
                                                                count[id][nn*6+2] +=1
				if( n3 -anchor+1 >  anchor):
					ss = start + n1 + n2
					for p in range( ss + anchor, ss + n3 -anchor+1 ):
						if( fr2.getrname(iter.reference_id),p) in ppL:
							for id in ppL[ fr2.getrname(iter.reference_id),p]:
							#	if(id =="chr1_9881892_9884406"):
                                                         #       	print str(iter)
							#		print 33
							#		print iter.get_reference_positions()
							#		print aa1,aa2, start,ss, n1,n2,n3
								#included count at left side
								count[id][nn*6] +=1
					for p in range( ss + anchor-1, ss + n3 -anchor):
						if( fr2.getrname(iter.reference_id),p) in ppR:
                                                        for id in ppR[ fr2.getrname(iter.reference_id),p]:
                                                                #included count at left side
                                                                count[id][nn*6+2] +=1

				start += (n1+n2)

		nn += 1
		fr2.close()
	fr1 = open(gtf)
	fw = open(output,"w")
	for info1 in fr1:
		a1 = info1.strip().split("\t")
		key = "%s_%s_%s" % (a1[0],a1[3],a1[4])
		if(count[key][num*6+3]=="true"):
			if(re.search('\+',count[key][num*6+1])):
				fw.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (key, count[key][num*6],count[key][num*6+1],count[key][num*6+2],a1[0],a1[3],a1[4],"\t".join(str(x) for x in count[key][0:num*6])))
			else:
				fw.write("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (key, count[key][num*6],count[key][num*6+1],count[key][num*6+2],a1[0],a1[3],a1[4]))
				for i in range(0, num):
					fw.write("\t%s\t%s\t%s\t%s\t%s\t%s"%(count[key][i*6+2],count[key][i*6+3],count[key][i*6],count[key][i*6+1],count[key][i*6+4],count[key][i*6+5]))
				fw.write("\n") 
			count[key][num*6+3]="false"
	fw.close()
	exit()

print "this is library with strand info"
fr1 = open(gtf)
count = dict()
#the dict to store the intron count,first is the inclusion at left side, second is the skipped count at smaller side, third inclusion at right side, fourth skipping at right side, fifith skipping counts, sixth intron counts, at the end of the three column store gene_id, gene_strand, and clean introns based on bam files
ppL = dict()
#the dict to store left edge  position of intron
ppR = dict()
#the dict to store right  edge  position of intron
pp = dict()
#the dict to store the two edge position of intron
pos = dict()
# the dictionary to store the introns in a certain windows
bin =1000
# set the bin size

bamfile = bam.split(",")
num = len(bamfile)
for info1 in fr1:
	a1 = info1.strip().split("\t")
	key = "%s_%s_%s" % (a1[0],a1[3],a1[4])
        gene_id = re.sub('.*gene_id "|\".*','',a1[8])
	if(count.has_key(key)):
		gg = count[key][6*num].split(",")
		gg_l = "true"
		for g_id in gg:
			if(gene_id == g_id):
				gg_l = "falase"
		if(gg_l =="true"):
			count[key][6*num]+=","
			count[key][6*num]+=gene_id
			count[key][6*num+1]+=","
			count[key][6*num+1]+=a1[6]

	else:
		count[key]= [0]*num*6
		count[key].append(gene_id)
		count[key].append(a1[6])
		count[key].append("true")
		count[key].append("true")
		ppL.setdefault((a1[0],int(a1[3])),[]).append(key)
		ppR.setdefault((a1[0],int(a1[4])),[]).append(key)
		pp[a1[0],int(a1[3]),int(a1[4])] = key
		index_s =  int(a1[3]) / bin
		index_e =  int(a1[4]) / bin
                for i in  range(index_s , index_e+1):
                	pos.setdefault((a1[0],i),[]).append(key)

fr1.close()
bamfile = bam.split(",")
nn = 0
print "library building complete"
for file in bamfile:
	path = "%s.bai" % file
	if (not os.path.exists(path)):
		cmd = "samtools index %s" % file
		print cmd
		os.system(cmd)
        fr2 = pysam.AlignmentFile(file, "rb")
	iter = fr2.fetch()
        for iter in fr2:
		if(read =="P"):
			if((iter.flag /2 )%2 ==0 ):
				continue
			if(iter.get_tag('NH')!=1):
				continue
			if(re.search("D|H|S",iter.cigarstring)):
				continue
			if(re.search("I",iter.cigarstring)):
				continue
		if(read =="S"):
			if(not re.search(str(iter.flag),"0,16")):
				continue
			if(iter.get_tag('NH')!=1):
				continue
			if(re.search("D|H|S",iter.cigarstring)):
				continue
			if(re.search("I",iter.cigarstring)):
				continue
		strand=''
                flag = str(length) +'M' 
		ss = (iter.flag) /16 % 2
			
		if ((read =="S") & (lib=="first")):
			if (ss==0):
				strand="-"
			else:
				strand="+"
		if ((read =="S") & (lib=="second")):
                        if (ss==0):
                                strand="+"
                        else:
                                strand="-"
		
		if ((read =="P") & (lib =="first")):
			f = int(iter.flag ) /64 % 2
			s = int(iter.flag ) /128 % 2
			if ((ss == 0) & (f ==1)):
				strand = "-"
			if ((ss == 0) & (s ==1)):
                                strand = "+"
			if ((ss == 1) & (f ==1)):
                                strand = "+"
                        if ((ss == 1) & (s ==1)):
                                strand = "-"
		
		if ((read =="P") & (lib =="second")):
                        f = int(iter.flag ) /64 % 2
                        s = int(iter.flag ) /128 % 2
                        if ((ss == 0) & (f ==1)):
                                strand = "+"
                        if ((ss == 0) & (s ==1)):
                                strand = "-"
                        if ((ss == 1) & (f ==1)):
                                strand = "-"
                        if ((ss == 1) &( s ==1)):
                                strand = "+"
       
		aa1 = iter.cigarstring.split("M")
		aa2 = iter.cigarstring.split("N")
		l = len(aa2)
		if(len(aa1)== 2):
			for p in range(iter.get_reference_positions()[0]+1 + anchor, iter.get_reference_positions()[0]+1 + int(aa1[0]) - anchor +1):
				if( fr2.getrname(iter.reference_id),p) in ppL:
					for id in ppL[ fr2.getrname(iter.reference_id),p]:
						if(re.search(("\%s" %strand),count[id][num*6+1])):
							#inclusion count at left side
							count[id][nn*6] +=1
							continue
			for p in range(iter.get_reference_positions()[0]+1 + anchor-1, iter.get_reference_positions()[0]+1 + int(aa1[0]) - anchor):
				if( fr2.getrname(iter.reference_id),p) in ppR:
					for id in ppR[ fr2.getrname(iter.reference_id),p]:
						if(re.search(("\%s" %strand),count[id][num*6+1])):
							#inclusion count at right side
							count[id][nn*6+2] +=1 
							continue        
			index= (iter.get_reference_positions()[0]+1)/bin
			if ( fr2.getrname(iter.reference_id), index) in pos:
				for key in pos[ fr2.getrname(iter.reference_id),index]:
					in_p = key.split("_")
					if ((int(in_p[1]) <= iter.get_reference_positions()[0]+1 )& (int(in_p[2])>= (iter.get_reference_positions()[0]+1 + length -1))):
						if (re.search(("\%s" %strand),count[key][num*6+1])):
							count[key][nn*6+5]+=1
		start = iter.get_reference_positions()[0]+1
		for i in range(0,l-1):
			if(re.search("\D",aa2[i].split("M")[0])):
				continue
			if(re.search("\D",aa2[i].split("M")[1])):
				continue
			if(re.search("\D",aa2[i+1].split("M")[0])):
				continue
			n1=int(aa2[i].split("M")[0])
			n2=int(aa2[i].split("M")[1])
			n3=int(aa2[i+1].split("M")[0])
			if (n1 >= anchor and n3 >= anchor):
				index1 = (start+ n1-1)/ bin
				index2 = (start+ n1+n2)/bin
				if( fr2.getrname(iter.reference_id), index1) in pos:
					for key in pos[ fr2.getrname(iter.reference_id),index1]:
						in_p = key.split("_")
						if ((int(in_p[1]) < start +n1 )& (int(in_p[2]) > start +n1)):
							if (re.search(("\%s" %strand),count[key][num*6+1])):
								count[key][num*6+2] ="false"
				if( fr2.getrname(iter.reference_id), index2) in pos:
					 for key in pos[ fr2.getrname(iter.reference_id),index2]:
						 in_p = key.split("_")   
						 if ((int(in_p[1]) < start +n1+n2 -1 )& (int(in_p[2]) > start +n1+n2 -1 )):
							if (re.search(("\%s" %strand),count[key][num*6+1])):
								 count[key][num*6+2] ="false"		

				if ( fr2.getrname(iter.reference_id), start+n1) in ppL:
					for id in ppL[ fr2.getrname(iter.reference_id),start +n1]:
						if(re.search(("\%s" %strand),count[id][num*6+1])):
							#skipped count at left side
							count[id][nn*6+1] +=1
				if ( fr2.getrname(iter.reference_id), start+n1+n2-1) in ppR:
					for id in ppR[ fr2.getrname(iter.reference_id),start +n1+n2 -1]:
						if(re.search(("\%s" %strand),count[id][num*6+1])):
							#skipped count at right side
							count[id][nn*6+3] +=1
				if ( fr2.getrname(iter.reference_id),start+n1, start+n1+n2-1) in pp:
					if(re.search(("\%s" %strand),count[pp[ fr2.getrname(iter.reference_id),start+n1,start +n1+n2 -1]][num*6+1])):
						#skipping count at both side
						count[pp[ fr2.getrname(iter.reference_id),start+n1,start +n1+n2 -1]][nn*6+4] +=1   
		    	if( n1 -anchor+1 >  anchor):
				ss = start
				for p in range( ss + anchor, ss + n1 -anchor+1 ):
					if( fr2.getrname(iter.reference_id),p) in ppL:
						for id in ppL[ fr2.getrname(iter.reference_id),p]:
							if(re.search(("\%s" %strand),count[id][num*6+1])):
								#included count at left side
								count[id][nn*6] +=1
				for p in range( ss + anchor-1, ss + n1 -anchor ):
					if( fr2.getrname(iter.reference_id),p) in ppR:
						for id in ppR[ fr2.getrname(iter.reference_id),p]:
							if(re.search(("\%s" %strand),count[id][num*6+1])):
								#included count at right side
								count[id][nn*6+2] +=1
			if( n3 -anchor+1 >  anchor):
				ss = start + n1 + n2
				for p in range( ss + anchor, ss + n3 -anchor+1 ):
					if( fr2.getrname(iter.reference_id),p) in ppL:
						for id in ppL[ fr2.getrname(iter.reference_id),p]:
							if(re.search(("\%s" %strand),count[id][num*6+1])):
								#included count at left side
								count[id][nn*6] +=1
				for p in range( ss + anchor-1, ss + n3 -anchor):
					if( fr2.getrname(iter.reference_id),p) in ppR:
						for id in ppR[ fr2.getrname(iter.reference_id),p]:
							if(re.search(("\%s" %strand),count[id][num*6+1])):
								#included count at left side
								count[id][nn*6+2] +=1

			start += (n1+n2)
	nn += 1
	fr2.close()

fr1 = open(gtf)
fw = open(output,"w")
for info1 in fr1:
	a1 = info1.strip().split("\t")
	key = "%s_%s_%s" % (a1[0],a1[3],a1[4])
	if(count[key][num*6+3]=="true"):
		if(re.search('\+',count[key][num*6+1])):
			fw.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (key, count[key][num*6],count[key][num*6+1],count[key][num*6+2],a1[0],a1[3],a1[4],"\t".join(str(x) for x in count[key][0:num*6])))
		else:
			fw.write("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (key, count[key][num*6],count[key][num*6+1],count[key][num*6+2],a1[0],a1[3],a1[4]))
			for i in range(0, num):
				fw.write("\t%s\t%s\t%s\t%s\t%s\t%s"%(count[key][i*6+2],count[key][i*6+3],count[key][i*6],count[key][i*6+1],count[key][i*6+4],count[key][i*6+5]))
			fw.write("\n") 
		count[key][num*6+3]="false"
fw.close()

