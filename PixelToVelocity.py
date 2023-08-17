import vtk
import numpy
import argparse
from glob import glob
import os
from utilities import *

class PixelToVelocity():
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
	parser = argparse.ArgumentParser(description="This script will take the Phase Images and Convert to Velocity using Venc.")

        #Provide a path to the Magnitude Images
	parser.add_argument('-InputFolder', '--InputFolder', type=str, required=True, dest="InputFolder",help="The foldername that contains Magnitude, Phase1, Phase2, and Phase3 images. The expected Path format is Magnitude/Magnitude_0/RawImage_0.vti")
	
	#Velocity Encoding
	parser.add_argument('-Venc', '--Venc', type=int, required=True, dest="Venc",help="The Velocity Encoding value.")


	args=parser.parse_args()
	PixelToVelocity(args).Main()
