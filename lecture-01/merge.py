#Merging 

l1 = [50]
l2 = [1,100]
merged_list=list()

i=0
j=0

print "l1 = " + str(l1)
print "l2 =" + str(l2)
print "\n\n"

l1.append('end')
l2.append('end')

while l1[i] != 'end' or l2[j] != 'end':
	if l1[i] != 'end' and l2[j] != 'end' and l1[i] < l2[j]:
		merged_list.append(l1[i])
		i=i+1
		print "l1 < l2"

	elif l1[i]!= 'end' and l2[j] != 'end' and l1[i] > l2[j]:
		merged_list.append(l2[j])
		j=j+1
		print "l1 > l2"
	elif l1[i]!= 'end' and l2[j] != 'end' and l1[i] == l2[j]:
		merged_list.append(l1[i])
		merged_list.append(l2[j])
		i=i+1
		j=j+1
	elif l1[i] == 'end':
		merged_list.append(l2[j])
		j=j+1
		print "l1 = end"
	elif l2[j] == 'end':
		merged_list.append(l1[i])
		i=i+1
		print "l2 = end"
	else:
		print "Error"
print "\n"
print "Merged List = " + str(merged_list) + "\n"

