import unittest
import calcVarPriors

class test_calcVarPriors(unittest.TestCase):

    def setUp(self):

        self.variant = {"Chr": "13",
                        "Pos": "32314943",
                        "Ref": "A",
                        "Alt": "G",
                        "Gene_Symbol": "BRCA2",
                        "Reference_Sequence": "NM_000059.3",
                        "pyhgvs_cDNA": "NM_000059.3:c.-764A>G"}

        self.strand = {"minus": "-",
                       "plus": "+"}

        self.varTypes = {"sub": "substitution",
                         "ins": "insertion",
                         "del": "deletion",
                         "delins": "delins"}
                           
    def test_checkSequence(self):
        '''Tests that checkSequence function categorized acceptable sequences correctly'''
        # sequence with unacceptable letters
        self.variant["Ref"] = "ATGSFHG"
        self.variant["Alt"] = "AGTHA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # sequence with numbers
        self.variant["Ref"] = "3452345"
        self.variant["Alt"] = "3456324"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # blank sequence
        self.variant["Ref"] = ""
        self.variant["Alt"] = ""
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # sequence with only ATCG
        self.variant["Ref"] = "ATGACG"
        self.variant["Alt"] = "AGTAATA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertTrue(acceptableRefSeq)
        self.assertTrue(acceptableAltSeq)

        # sequence containing all possible acceptable bases
        self.variant["Ref"] = "ATGRACYGN"
        self.variant["Alt"] = "YAGRTNAATA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertTrue(acceptableRefSeq)
        self.assertTrue(acceptableAltSeq)


    def test_getVarStrand(self):
        '''Tests that variant strand is set correctly based on variant's gene_symbol'''
        self.variant["Gene_Symbol"] = "BRCA1"
        varStrand = calcVarPriors.getVarStrand(self.variant)
        self.assertEquals(varStrand, self.strand["minus"])

        self.variant["Gene_Symbol"] = "BRCA2"
        varStrand = calcVarPriors.getVarStrand(self.variant)
        self.assertEquals(varStrand, self.strand["plus"])

        
    def test_getVarType(self):
        '''
        Tests that variant type is set correctly to substitution, deletion, insertion, or delins based on variant "Ref" and "Alt" values
        '''
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, self.varTypes["sub"])

        self.variant["Ref"] = "A"
        self.variant["Alt"] = "AAA"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, self.varTypes["ins"])

        self.variant["Ref"] = "AGT"
        self.variant["Alt"] = "A"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, self.varTypes["del"])

        self.variant["Ref"] = "AG"
        self.variant["Alt"] = "AGTA"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, self.varTypes["delins"])

        self.variant["Ref"] = "AGTA"
        self.variant["Alt"] = "AG"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, self.varTypes["delins"])

        self.variant["Ref"] = "AG"
        self.variant["Alt"] = "GT"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, self.varTypes["delins"])

    def test_getVarConsequences(self):
        '''
        Tests that:
        1. Variants with non-BRCA1/BRCA2 chromosomes are skipped
        2. Variants with Alt alleles that are not one of the 4 canonical bases are skipped
        '''

        self.variant["Chr"] = ""
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "41160094"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "chr17:g.43008077:TAGG"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32339320"
        self.variant["Hg38_End"] = "32339320"
        self.variant["Alt"] = "R"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Alt"] = "-"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Alt"] = "38413620"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        
    def test_getVarLocation(self):
        '''
        Tests that:
        1. Variant location is set correctly for genomic position outside transcript boundaries
        2. Variant location is set correctly for genomic position in exon
        3. Variant location is set correclty for genomic position in intron
        '''
        # TO DO - implement tests for varLocation once varLocation changed to use Ensembl API
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        # position before txn start site for BRCA1
        self.variant["Pos"] = "43044274"
        varLoc = calcVarPriors.getVarLocation(self.variant)

        # position in exon for BRCA1
        self.variant["Pos"] = "43070957"
        varLoc = calcVarPriors.getVarLocation(self.variant)
        
        # position in intron for BRCA1
        self.variant["Pos"] = "43106443"
        varLoc = calcVarPriors.getVarLocation(self.variant)

        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        # position before txn start site for BRCA2
        self.variant["Pos"] = "32315477"
        varLoc = calcVarPriors.getVarLocation(self.variant)

        # position in exon for BRCA2
        self.variant["Pos"] = "32326500"
        varLoc = calcVarPriors.getVarLocation(self.variant)
        
        # position in intron for BRCA2
        self.variant["Pos"] = "32357952"
        varLoc = calcVarPriors.getVarLocation(self.variant)
        

    def test_getVarDict(self):
        '''
        Tests that: 
        1. Variant information is being parsed correctly
        '''

        varDict = calcVarPriors.getVarDict(self.variant)
        self.assertEquals(varDict["varHGVScDNA"], self.variant["pyhgvs_cDNA"])
        self.assertEquals(varDict["varChrom"], self.variant["Chr"])
        self.assertEquals(varDict["varGene"], self.variant["Gene_Symbol"])
        self.assertEquals(varDict["varGenCoordinate"], self.variant["Pos"])
        
