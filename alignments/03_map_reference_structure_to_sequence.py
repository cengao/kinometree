from Bio.Seq import Seq
from Bio import AlignIO
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_protein
import numpy as npy
from Bio.Phylo.TreeConstruction import DistanceCalculator
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor
from Bio import Phylo
import sys

manningFlag=0
print("usage 03_map_reference_structure_to_sequence.py kinomealginment.fasta (manning/1)")
inputFile=sys.argv[1]

if (len(sys.argv))>2:
    manningFlag=1

def getAlignmentPositionsToExtract(structureToAlignmentMap,sequenceSelections):
    #print(structureToAlignmentMap)
    #print(sequenceSelections)
    idxs=sequenceSelections
    print(idxs)
    return(structureToAlignmentMap[idxs])

outputPrefix="type1Inactive"
if manningFlag:
    alignment = AlignIO.read(open(inputFile), "clustal")
    outputPrefix="type1Inactive_manning"
else :
    alignment = AlignIO.read(open(inputFile), "fasta")

print("Number of sequences in alignment %i" % len(alignment))

#take example structure and gather list of seq numbers to retain (uniprot sequence) -> map to kinase domain sequence -> map to sequence alignment
refUniprotCode="CDK2_HUMAN"
kinaseDomainRange=[(4+1),286]    #+1 here because I dropped the initial residue (python 0 indexing error before)
if manningFlag:
    refUniprotCode="CMGC_CDK_CDC2_CDK2"
    kinaseDomainRange=[(3+1),286]    #+1 here because I dropped the initial residue (python 0 indexing error before)



type1InactiveSeedStructure={"6guk":"FC8"}
residueSelection=npy.array([10,18,20,31,33,64,80,82,86,89,131,132,134,144,145,146,148])
#residueSelection=npy.array([10,13,14,15,18,20,31,33,55,58,63,64,66,78,80,82,86,89,131,132,134,144,145,146,148])
#probabloy out : 13,14,15,,63,66,78,
#likely in: 20
#less weight: 131,132,145,146,
#backpocket: 148, 146, 63,78
#wrong in current alignment : 55,58



type1InactiveSeedStructure={"4nj3":"2KD"}

type2IActiveSeedStructure={"5a14":"LQ5"}



idxs=[]
s=""
for record in alignment:
    if(record.id==refUniprotCode):
        idxs=npy.array([ix for ix,c in enumerate(record.seq) if c!="-"])
        s=record.seq
        break

if len(idxs):
    structureToAlignmentMap=idxs
    positions=getAlignmentPositionsToExtract(structureToAlignmentMap,residueSelection-kinaseDomainRange[0])

    print("Double check with initial selection: ",[c for idx,c in enumerate(s) if idx in positions])
    print(positions)
    pocketAlignment=""
    for pos in positions:
        if(len(pocketAlignment)==0):
            pocketAlignment=alignment[:, pos:(pos+1)]
        else :
            pocketAlignment+=alignment[:, pos:(pos+1)]
    pocketAlignment.sort()
    print(pocketAlignment)
    output_handle = open(outputPrefix+".fasta", "w")
    AlignIO.write(pocketAlignment, output_handle, "fasta")
    output_handle.close()

    calculator = DistanceCalculator('blosum62')
    dm = calculator.get_distance(pocketAlignment) 
    constructor = DistanceTreeConstructor(calculator, 'nj')
    tree = constructor.build_tree(pocketAlignment)
    Phylo.write(tree, outputPrefix+'.xml', 'phyloxml')
    Phylo.write(tree, outputPrefix+'.nwk', 'newick')



#approach to integrate here : 
# transform sequence of interest to numpy array
# map positions from structure of interest to uniprot sequence (3decision)
# map from uniprot sequence to sequence alignment here (double check pfam domain things first not to choose not suitable protein sequences)
