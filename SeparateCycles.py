import vtk
import numpy
import argparse
from glob import glob
import os

class SeparateCycles():
	def __init__(self,Arg):
		self.Args=Arg

	def Main(self):
		#Separate all images into individual folders
		print ("Separating Folders: Magnitude")
		self.SeparateCycles(self.Args.Magnitude,"Magnitude")
		print ("Separating Folders: Phase1")
		self.SeparateCycles(self.Args.Phase1,"Phase1")
		print ("Separating Folders: Phase2")
		self.SeparateCycles(self.Args.Phase2,"Phase2")
		print ("Separating Folders: Phase3")
		self.SeparateCycles(self.Args.Phase3,"Phase3")		

	def SeparateCycles(self,FolderName,Tag):
		#Get all of the files in the folder
		FileNames_=sorted(glob(FolderName+"/*.IMA"))+sorted(glob(FolderName+"/*.dcm"))
		
		#Separte the files in N folders
		os.system("mkdir %s/%s"%(self.Args.OutputFolder,Tag))
		for i in range(self.Args.Cycles): os.system("mkdir %s/%s/%s_%d"%(self.Args.OutputFolder,Tag,Tag,i))	
		#Loop over all of the files and stack them into different folders
		counter=0
		for i in range(len(FileNames_)):
			os.system("cp %s %s/%s/%s_%d"%(FileNames_[i],self.Args.OutputFolder,Tag,Tag,counter))
			if (i+1)%(len(FileNames_)/self.Args.Cycles)==0: counter+=1
			


if __name__=="__main__":
	#Description
	parser = argparse.ArgumentParser(description="This script will average the 4D Flow MRI data to convert into angiography data to segmentation easier.")

	#Provide a path to the Magnitude Images
	parser.add_argument('-Magnitude', '--Magnitude', type=str, required=True, dest="Magnitude",help="The foldername that contains the magnitude images")
	
	#Provide a path for phase images 1 2 and 3
	parser.add_argument('-Phase1', '--Phase1', type=str, required=True, dest="Phase1",help="The foldername that contains the phase1 images")
	parser.add_argument('-Phase2', '--Phase2', type=str, required=True, dest="Phase2",help="The foldername that contains the phase2 images")
	parser.add_argument('-Phase3', '--Phase3', type=str, required=True, dest="Phase3",help="The foldername that contains the phase3 images")
	
	#Number of scan cycles 
	parser.add_argument('-Cycles', '--Cycles', type=int, required=False, dest="Cycles",default=15,help="The number of cycles in the 4D MRI images")

	#Name of the output folder
	parser.add_argument('-OutputFolder', '--OutputFolder', type=str, required=True, dest="OutputFolder",help="The foldername to put all the results in.")

	args=parser.parse_args()
	SeparateCycles(args).Main()
