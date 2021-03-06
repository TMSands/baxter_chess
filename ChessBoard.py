#! /usr/bin/env python
"""
 Project: Python Chess
 File name: ChessBoard.py
 Description:  Board layout; contains what pieces are present
	at each square.
	
 Copyright (C) 2009 Steve Osborne, srosborne (at) gmail.com
 http://yakinikuman.wordpress.com/
 
 Edited by:
 	Trevor Sands for EEEE 585, Rochester Institute of Technology under GNU GPL
 	December 7, 2013
 """
 
import string
import roslib
roslib.load_manifest('joint_position')
import rospy
import baxter_interface
import iodevices
import time

from baxter_msgs.msg import (
    JointVelocities,
    JointCommandMode,)

from MoveArmsIK import moveArmLoc
from ImgProc import findPiece, filterColors

class ChessBoard:
	def __init__(self,setupType=0):
		self.squares = [['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e'],\
				['e','e','e','e','e','e','e','e']]
						
		if setupType == 0:
			self.squares[0] = ['bR','bT','bB','bQ','bK','bB','bT','bR']
			self.squares[1] = ['bP','bP','bP','bP','bP','bP','bP','bP']
			self.squares[2] = ['e','e','e','e','e','e','e','e']
			self.squares[3] = ['e','e','e','e','e','e','e','e']
			self.squares[4] = ['e','e','e','e','e','e','e','e']
			self.squares[5] = ['e','e','e','e','e','e','e','e']
			self.squares[6] = ['wP','wP','wP','wP','wP','wP','wP','wP']
			self.squares[7] = ['wR','wT','wB','wQ','wK','wB','wT','wR']
			
	def GetState(self):
		return self.squares
		
	def ConvertMoveTupleListToAlgebraicNotation(self,moveTupleList):	
		newTupleList = []
		for move in moveTupleList:
			newTupleList.append((self.ConvertToAlgebraicNotation(move[0]),self.ConvertToAlgebraicNotation(move[1])))
		return newTupleList
	
	def ConvertSquareListToAlgebraicNotation(self,list):
		newList = []
		for square in list:
			newList.append(self.ConvertToAlgebraicNotation(square))
		return newList

	def ConvertToAlgebraicNotation(self,(row,col)):
		#Converts (row,col) to algebraic notation
		#(row,col) format used in Python Chess code starts at (0,0) in the upper left.
		#Algebraic notation starts in the lower left and uses "a..h" for the column.
		return  self.ConvertToAlgebraicNotation_col(col) + self.ConvertToAlgebraicNotation_row(row)
	
	def ConvertToAlgebraicNotation_row(self,row):
		#(row,col) format used in Python Chess code starts at (0,0) in the upper left.
		#Algebraic notation starts in the lower left and uses "1..8" for the row.	
		B = ['8','7','6','5','4','3','2','1']
		return B[row]
		
	def GetCartesian_row(self,row):
		Y = [0.156, 0.096, 0.059, 0.024, -0.023, -0.060, -0.112, -0.156]
		return Y[row]
		
	def ConvertToAlgebraicNotation_col(self,col):
		#(row,col) format used in Python Chess code starts at (0,0) in the upper left.
		#Algebraic notation starts in the lower left and uses "a..h" for the column.	
		A = ['a','b','c','d','e','f','g','h']
		return A[col]
		
	def GetCartesian_col(self,col):
		X = [0.642, 0.602, 0.559, 0.511, 0.469, 0.421, 0.363, 0.328]
		return X[col]	
	
	def GetFullString(self,p):
		if 'b' in p:
			name = "black "
		else:
			name = "white "
			
		if 'P' in p:
			name = name + "pawn"
		if 'R' in p:
			name = name + "rook"
		if 'T' in p:
			name = name + "knight"
		if 'B' in p:
			name = name + "bishop"
		if 'Q' in p:
			name = name + "queen"
		if 'K' in p:
			name = name + "king"
			
		return name
	
	def MovePiece(self,moveTuple):
		#Square variables
		fromSquare_r = moveTuple[0][0]
		fromSquare_c = moveTuple[0][1]
		toSquare_r = moveTuple[1][0]
		toSquare_c = moveTuple[1][1]
		
		#Gripper and arm initializations
		grip_right = baxter_interface.Gripper('right')
        	right = baxter_interface.Limb('right')
        	right.move_to_neutral()
		grip_right.calibrate()
		grip_right.open()
		
		#Give initial Cartesian coordinates to Baxter using fromSquare row and columns
		moveArmLoc('right', self.GetCartesian_col(fromSquare_c), self.GetCartesian_row(fromSquare_r), -0.20)
		time.sleep(1)
		
		#Pick up piece
		findPiece()
		moveArmLoc('right', self.GetCartesian_col(fromSquare_c), self.GetCartesian_row(fromSquare_r), -0.32)
		time.sleep(1)
		grip_right.close()
		time.sleep(1)
		
		#Give final Cartesian coordinates to Baxter using toSquare row and columns
		moveArmLoc('right', self.GetCartesian_col(toSquare_c), self.GetCartesian_row(toSquare_r), -0.20)
		
		#Drop piece
		moveArmLoc('right', self.GetCartesian_col(toSquare_c), self.GetCartesian_row(toSquare_r), -0.32)
		time.sleep(1)
		grip_right.open()
		
		#Return to home position
		moveArmLoc('right', self.GetCartesian_col(toSquare_c), self.GetCartesian_row(toSquare_r), -0.20)
		right.move_to_neutral()
		
		#Assign square positions for from and to pieces
		fromPiece = self.squares[fromSquare_r][fromSquare_c]
		toPiece = self.squares[toSquare_r][toSquare_c]
		
		#Move piece by changing square locations
		self.squares[toSquare_r][toSquare_c] = fromPiece
		self.squares[fromSquare_r][fromSquare_c] = 'e'

		fromPiece_fullString = self.GetFullString(fromPiece)
		toPiece_fullString = self.GetFullString(toPiece)
		
		if toPiece == 'e':
			messageString = fromPiece_fullString+ " moves from "+self.ConvertToAlgebraicNotation(moveTuple[0])+\
						    " to "+self.ConvertToAlgebraicNotation(moveTuple[1])
			
		else:
			messageString = fromPiece_fullString+ " from "+self.ConvertToAlgebraicNotation(moveTuple[0])+\
						" captures "+toPiece_fullString+" at "+self.ConvertToAlgebraicNotation(moveTuple[1])+"!"
		
		#capitalize first character of messageString
		messageString = string.upper(messageString[0])+messageString[1:len(messageString)]
		
		return messageString

if __name__ == "__main__":
	
	cb = ChessBoard(0)
	board1 = cb.GetState()
	for r in range(8):
		for c in range(8):
			print board1[r][c],
		print ""
		
	print "Move piece test..."
	cb.MovePiece(((0,0),(4,4)))
	board2 = cb.GetState()
	for r in range(8):
		for c in range(8):
			print board2[r][c],
		print ""
