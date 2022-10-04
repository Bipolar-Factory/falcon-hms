import dataset
import asyncio
import aiohttp
# from .config import *

UPDATE_PERIOD=10
DB_URI="sqlite:///devices.db"
ONVIF_URL="https://onvif.falconvms.com"


async def get_device_record_status(
		host: str,
		username: str,
		password: str,
		port: int
):
	async with aiohttp.ClientSession(ONVIF_URL) as session:
		payload = dict(
			host=host,
			username=username,
			password=password,
			port=port
		)
		async with session.post(
				"/api/hms/getDeviceHealth",
				json=payload
		) as resp:
			response = await resp.json()
			
	print(response)
	return response
	

async def get_device_health_status(
		host: str,
		username: str,
		password: str,
		port: int
):
	async with aiohttp.ClientSession(ONVIF_URL) as session:
		payload = dict(
			host=host,
			username=username,
			password=password,
			port=port
		)
		async with session.post(
				"/api/hms/getDeviceRecord",
				json=payload
		) as resp:
			response = await resp.json()
	return response
	

async def device_monitor(device_id: int):
	db = dataset.connect(DB_URI)
	table = db["devices"]
	device = table.find_one(id=device_id)
	curr = {}
	prev = {}
	first = True
	db.close()
	while True:
		record_statuses = await get_device_record_status(
			device["hostname"],
			device["username"],
			device["password"],
			device["port"]
		)
		if record_statuses["success"]:
			await asyncio.sleep(UPDATE_PERIOD)
		else:
			print("Unable to fetch data from ONVIF Server")
			continue
		
		for record_status in record_statuses["data"]:
			sourceToken = record_status["sourceToken"]
			status = record_status["status"]
			if first:
				first = False
				prev[sourceToken] = status
				
			curr[sourceToken] = status
			if curr[sourceToken] != prev[sourceToken]:
				prev[sourceToken] = curr[sourceToken]
				db = dataset.connect(DB_URI)
				table = db["activity_log"]
				table.insert({
					"sourceToken": sourceToken,
				})
				db.close()
				
asyncio.run(get_device_record_status("183.82.251.72", "admin", "admin12345", 80))
