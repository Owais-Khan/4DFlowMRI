import vtk
import numpy
import argparse
from glob import glob
import os
from utilities import *
class ConvertCyclesToVti():
	def __init__(self,args):
		self.Args=args

	def Main(self):
		#Load Angio Image
		print ("--- Loading Angio Image: %s"%self.Args.ReferenceImage)
		RawAngio = ReadVTIFile(self.Args.ReferenceImage)

		#DICOM to VTI
		print ("--- Converting Dicoms to VTI Stacks")
		OutFileNames=self.ConvertDicomsToVTI()		
		
		for OutFileName_ in OutFileNames:
			#Load the Angiography Images
			print ("------ Loading Angiography Image: %s"%OutFileName_)
			Image_=ReadVTIFile(OutFileName_)

			#Scale the Image to correct origin and to cm instead of mm
			origin = RawAngio.GetOrigin()
			spacing = RawAngio.GetSpacing()

			Image_.SetOrigin(origin)
			Image_.SetSpacing(spacing)	

			#Save the Scaled Image
			WriteVTIFile(OutFileName_,Image_)


	def ConvertDicomsToVTI(self):
		FolderList=[]
		OutFileList=[]
		for Tag in ["Magnitude","Phase1","Phase2","Phase3"]:
			FolderList = FolderList + sorted(glob("%s/%s/*"%(self.Args.InputFolder,Tag)))
		
		print ("------ Number of Folders Detected: %d"%len(FolderList))
		NFolders= len(FolderList)
		for i in range (0,NFolders):
			os.system("rm %s/*.vti"%FolderList[i])	
			print ("------ Looping over: %s"%FolderList[i])
			#AngioConvert_ = vtk.vtkDICOMImageReader()
			#AngioConvert_.SetDirectoryName(FolderList[i])
			#AngioConvert_.Update()
				
			#Cycle Number
			CycleNo_=int(FolderList[i].split("_")[-1])
	
			#Give an Outfile Name
			OutFileName_=FolderList[i]+"/RawImage_%d.vti"%CycleNo_
			
			OutFileList.append(OutFileName_)

			#Write Unmasked VTI File
			#print ("------ Writing the unmasked VTI File: %s"%OutFileName_)
			#WriteVTIFile (OutFileName_,AngioConvert_.GetOutput())
			
			#Just take one file from the folder
			infile_=glob(FolderList[i]+"/*.IMA")+glob(FolderList[i]+"/*.dcm")
			os.system("vmtkimagewriter -ifile %s -ofile %s"%(infile_[i],OutFileName_))	
			
		return OutFileList




if __name__=="__main__":
        #Description
	parser = argparse.ArgumentParser(description="This script will generate a vti file for each of the velocity and magnitude file")

        #Provide a path to the Magnitude Images
	parser.add_argument('-InputFolder', '--InputFolder', type=str, required=True, dest="InputFolder",help="The foldername that contains three Folders: Magnitude, Phase1, Phase2 and Phase3. Each subfolder should contain Magnitude_0...MagnitudeN, Phase1_0...Phase1_N, Phase2_0...Phase2_N, Phase3_0...Phase3_N.")

	#Provide a file name whose origin and spacing we need to use
	parser.add_argument('-ReferenceImage', '--ReferenceImage', type=str, required=True, dest="ReferenceImage",help="The reference Angiography image whose origin and spacing to copy to the 4DMRI image.")


	args=parser.parse_args()
	ConvertCyclesToVti(args).Main()
