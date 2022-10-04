import dataset
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Device(BaseModel):
	hostname: str
	username: str
	password: str
	port: int

def connect_db():
	return dataset.connect("sqlite:///devices.db")

@app.get("/device")
def get_device(
		device_id: int = 0
):
	db = connect_db()
	table = db["device"]
	device = table.find_one(id=device_id)
	db.close()
	return dict(device)

@app.post("/device")
def post_device(
		device: Device
):
	db = connect_db()
	table = db["device"]
	table.insert(dict(
		hostname=device.hostname,
		username=device.username,
		password=device.password,
		port=device.port
	))
	db.close()
	return {"message": "success"}

@app.delete("/device")
def delete_device(
		device: Device
):
	db = connect_db()
	table = db["device"]	
	table.delete(
		hostname=device.hostname,
		username=device.username,
		password=device.password,
		port=device.port		
	)
	db.close()
	return {"message": "success"}

@app.get("/devices")
def get_devices():
	db = connect_db()
	table = db["device"]
	devices = table.all()
	data = []
	for device in devices:
		data.append(dict(device))
	db.close()
	return data
