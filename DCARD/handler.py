# coding=utf-8
from __future__ import print_function  # Python 2/3 compatibility
import os
import sys
import boto3
import json
import time

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./lib"))

import requests


def main(event, context):
	allSchool = ['cycu', 'csmu', 'wzu']
	# DynamoDB init
	dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
	table = dynamodb.Table('dcardPost')

	for school in allSchool:
		nowOffset = 0
		print("School", school)
		while True:
			# Debug
			print("Offset", nowOffset)

			dcardPostLink = "https://www.dcard.tw/_api/search/posts"
			dcardPostLink += "?query=%E4%BF%AE%E9%81%8E&forum=" + school + "&offset="
			dcardPostLink += str(nowOffset)
			res = requests.get(dcardPostLink)
			res.encoding = "utf-8"
			dataSet = json.loads(res.text)

			# Debug
			print("dataSet Length", len(dataSet))

			# ending condition
			if (len(dataSet) == 0):
				break

			nowOffset += len(dataSet)
			for data in dataSet:
				response = table.put_item(
					Item=data
				)
				print("PutItem", response)
			time.sleep(1)
	return("PutItem succeeded!")

def commentCrawler(event, context):
	allSchool = ['ntu','nccu','nctu','tku','ndhu','ncku','ntut','fju','ntnu','nknu','ncue','ncu','fcu','nthu','ncnu','thu','nkfust','ntust','nchu','yzu','nuu','ntou','nsysu','ntpu','cpu','ccu','usc','ym','ntua','shu','ntue','tnua','utaipei','pccu','scu','ncyu','nuk','nutc','ntunhs','isu','cgu','tmu','cycu','csmu','wzu','kuas','cgust','ncut','mcu','niu','nfu','nhcue','ttu','ntub','ntcu','nptu','pu','nkmu','cyut','ndu','stust','nkuht','cmu','cjcu','npust','mcut','asia','uch','stu','au','cnu','kmu','must','nttu','tut','nqu','dyu','nhu','ltu','fy','cute','tcust','tcu','chihlee','knu','hk','nutn','chu','takming','just','lhu','yuntech','csu','feu','wfu','ctust','npu','ksu','ntupes','ocu','hwu','twu','hwai','hfu','fgu','vnu','oit','cku','ctu','tnu','nkut','sju','mdu','meiho','tnnua','ukn','ydu','kyu','cust','ypu','ntsu','tajen','tsu','hcu','nju','ccut','hwh','hust','tust','tpcu','mmc','dlit','tcmt','tiit','tcpa','lit','toko','apic','tf','fit','tht','ttc','cit','fotech','dila','dahan']
	dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
	PostTable = dynamodb.Table('dcardPost')
	CommentTable = dynamodb.Table('dcardComments')

	def startCrawl(response):
		for post in response['Items']:
			after = 0
			while True:
				print("after", after)
				dcardCommentLink = "https://www.dcard.tw/_api/posts/"
				dcardCommentLink += str(post['id']) + "/comments?after=" + str(after)
				print("dcardCommentLink", dcardCommentLink)
				res = requests.get(dcardCommentLink)
				res.encoding = "utf-8"
				dataSet = json.loads(res.text)
				after += len(dataSet)
				# ending condition
				if (type(dataSet) == dict or len(dataSet) == 0):
					break
				for data in dataSet:
					data['reportReason'] = ' ' if data['reportReason'] == '' else data['reportReason']
					responseComment = CommentTable.put_item(
						Item=data
					)
					print("PutComment", responseComment)
				# time.sleep(1)
	try:
		for school in allSchool:
			print("School", school)
			print("Request ID:", context.aws_request_id)
			print("Time remaining (MS):", context.get_remaining_time_in_millis())
			if (context.get_remaining_time_in_millis() < 60000):
				print("Not start to crawl: ", school)
				break
			try:
				response = PostTable.scan(
					FilterExpression='forumAlias = :school',
					ExpressionAttributeValues={":school": school, },
				)
			except Exception, e:
				print("Dynamo Exception1: ", e['errorMessage'])
				return("Error", e)
			print("lenResponse", len(response['Items']))
			if (len(response['Items']) == 0):
				print("Response Empty!")
				continue
			startCrawl(response)
			print('LastEvaluatedKey:', response['LastEvaluatedKey'])
			if (context.get_remaining_time_in_millis() < 60000):
				print("Stop to crawl: ", school, "when LastEvaluatedKey")
				break
			while 'LastEvaluatedKey' in response:
				print('LastEvaluatedKey in while')
				print('LastEvaluatedKey:', response['LastEvaluatedKey'])
				if (context.get_remaining_time_in_millis() < 60000):
					print("Stop to crawl: ", school, "when LastEvaluatedKey")
					break
				try:
					time.sleep(1)
					response = PostTable.scan(
						FilterExpression='forumAlias = :school',
						ExpressionAttributeValues={":school": school, },
						ExclusiveStartKey=response['LastEvaluatedKey']
					)
				except Exception, e:
					print("Dynamo Exception2: ", e)
					return("Error", e['errorMessage'])
				if (len(response['Items']) == 0):
					print("Response Empty!")
					break
				startCrawl(response)
	except Exception, e:
		print("Lambda Exception: ", e)
		return("Time out!")
	return "Finish!!"
	# for school in allSchool:
	# 	print("School", school)
	# 	print("Request ID:",context.aws_request_id)
	# 	print("Time remaining (MS):", context.get_remaining_time_in_millis())
	# 	if (context.get_remaining_time_in_millis() < 60000):
	# 		print("Not start to crawl: ", school)
	# 		break
	# 	try:
	# 		response = PostTable.scan(
	# 			FilterExpression = 'forumAlias = :school',
	# 			ExpressionAttributeValues =  { ":school": school, },
	# 		)
	# 	except Exception, e:
	# 		print(e)
	# 		return("Error")
	# 	print("lenResponse", len(response['Items']))
	# 	if (len(response['Items']) == 0):
	# 		print("Response Empty!")
	# 		continue
	# 	startCrawl(response)
	# 	print('LastEvaluatedKey:', response['LastEvaluatedKey'])
	# 	if (context.get_remaining_time_in_millis() < 60000):
	# 		print("Stop to crawl: ", school, "when LastEvaluatedKey")
	# 		break
	# 	while 'LastEvaluatedKey' in response:
	# 		print('LastEvaluatedKey in while')
	# 		print('LastEvaluatedKey:', response['LastEvaluatedKey'])
	# 		if (context.get_remaining_time_in_millis() < 60000):
	# 			print("Stop to crawl: ", school, "when LastEvaluatedKey")
	# 			break
	# 		try:
	# 			response = PostTable.scan(
	# 			FilterExpression = 'forumAlias = :school',
	# 			ExpressionAttributeValues =  { ":school": school, },
	# 			ExclusiveStartKey=response['LastEvaluatedKey']
	# 			)
	# 		except Exception, e:
	# 			print(e)
	# 			return("Error")
	# 		if (len(response['Items']) == 0):
	# 			print("Response Empty!")
	# 			break
	# 		startCrawl(response)
