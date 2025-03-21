import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn
from request import dispatch_request, RequestType
from home_assistant import get_all_devices, toggle_tv_on_off

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Home Assistant Integration API",
    description="API for processing natural language requests to Home Assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class HomeAssistantRequest(BaseModel):
    query: str

# Response model
class HomeAssistantResponse(BaseModel):
    request_type: str
    description: str
    status: str
    message: str
    devices: List[Dict[str, Any]] = Field(default_factory=list)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Get all devices endpoint
@app.get("/api/devices")
async def get_devices():
    try:
        devices = get_all_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting devices: {str(e)}")

# Toggle TV endpoint
@app.post("/api/tv/toggle")
async def toggle_tv():
    try:
        result = toggle_tv_on_off()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling TV: {str(e)}")

# Main endpoint for processing requests
@app.post("/api/request", response_model=HomeAssistantResponse)
async def process_request(request: HomeAssistantRequest) -> Dict[str, Any]:
    if not request.query or request.query.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Get current state of all devices
        devices = get_all_devices()
        
        # Create a list to capture printed output
        import io
        import sys
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Call the dispatch_request function from request.py
        dispatch_request(request.query)
        
        # Restore stdout and get the captured output
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        
        # Parse the output to extract classification information
        request_type = "unknown"
        description = ""
        
        for line in output.split('\n'):
            if "Request classified as:" in line:
                request_type = line.split("Request classified as:")[1].strip()
            if "LLM explanation:" in line:
                description = line.split("LLM explanation:")[1].strip()
        
        # Determine the status based on the implementation
        if "Only device action requests are implemented at this time" in output and request_type != RequestType.DEVICE_ACTION.value:
            status = "not_implemented"
            message = "Only device action requests are implemented at this time."
        elif "Executing device action" in output:
            status = "success"
            message = "Device action request processed successfully."
        else:
            status = "processed"
            message = "Request processed."
        
        return {
            "request_type": request_type,
            "description": description,
            "status": status,
            "message": message,
            "devices": devices
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Run the FastAPI app with Uvicorn if this file is executed directly
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the API server
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)