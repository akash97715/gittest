from fastapi import FastAPI, Request
import asyncio

app = FastAPI()

# Assuming request_response_metering is defined as follows
async def request_response_metering(request, r_parent_wf_req_id, r_vendor_id, r_uom_id, r_uom_val):
    # Implementation of the function
    pass

# Example data structures for vendors, uom, and metering_dict
class Vendors:
    AZURE = "azure"
    AWS = "aws"

class UOM:
    TOTAL_TOKENS = "total_tokens"

vendors = Vendors()
uom = UOM()

@app.post("/process")
async def process_request(request: Request):
    metering_dict = [
        {"engine": "gpt-3.5-turbo", "total_token": 1500},
        {"engine": "aws-engine", "total_token": 1200},
    ]

    request_id = "req-789"  # This should be dynamically assigned as per your logic

    # Generate the list of request_response_metering calls
    metering_requests = [
        request_response_metering(
            request,
            r_parent_wf_req_id=request_id,
            r_vendor_id=vendors.AZURE if param["engine"].startswith("gpt") else vendors.AWS,
            r_uom_id=uom.TOTAL_TOKENS,
            r_uom_val=param["total_token"],
        )
        for param in metering_dict
    ]

    # Await all the metering requests
    await asyncio.gather(*metering_requests)

    return {"status": "success"}

# To run the FastAPI app, use the command `uvicorn script_name:app --reload`
