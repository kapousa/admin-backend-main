import json
import os
from typing import List, Optional, Dict, Any

import uvicorn
from bson import ObjectId
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import secrets
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Header, Response, UploadFile, File, Form
from typing import List
from pymongo import MongoClient
from fastapi.responses import JSONResponse

from starlette.staticfiles import StaticFiles

# from routes.CompanyAttachmentRoutes import router as attachment_router # Import the router, rename it


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]
companies_collection = db["companies"]

# Authentication (Basic HTTP Auth)
security = HTTPBasic()
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

app.mount("/files", StaticFiles(directory="uploads"))


def authenticate_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return credentials.username


# Pydantic Models
class FileAttachment(BaseModel):
    filename: str
    file_url: str  # URL to the file in your storage
    file_type: str  # Mime type of the file.


class KeyValuePair(BaseModel):
    key: str
    value: str
    file: Optional[FileAttachment] = None


class DynamicSectionItem(BaseModel):
    key: str
    value: str
    file: Optional[FileAttachment] = None


class DynamicSection(BaseModel):
    key: str  # Section Title
    value: List[DynamicSectionItem]

class CompanyCreate(BaseModel):
    name: str
    category: str
    size: str
    location: str
    employees: int
    description: str
    logo: Optional[str] = None #Modified line
    website: str
    revenue: int
    profit: int
    assets: int
    liabilities: int
    founded: str
    headquarters: str
    mission: str
    company_values: List[str]
    investors: List[KeyValuePair]
    financialStatement: List[KeyValuePair]
    assessment: List[KeyValuePair]
    portfolio: List[KeyValuePair]
    transformation_plan: List[KeyValuePair]
    dynamicSections: List[DynamicSection]

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    employees: Optional[int] = None
    description: Optional[str] = None
    logo: Optional[UploadFile] = File(None) # Change to UploadFile
    website: Optional[str] = None
    revenue: Optional[int] = None
    profit: Optional[int] = None
    assets: Optional[int] = None
    liabilities: Optional[int] = None
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    mission: Optional[str] = None
    company_values: Optional[List[str]] = None
    investors: Optional[List[KeyValuePair]] = None
    financialStatement: Optional[List[KeyValuePair]] = None
    assessment: Optional[List[KeyValuePair]] = None
    portfolio: Optional[List[KeyValuePair]] = None
    transformation_plan: Optional[List[KeyValuePair]] = None
    dynamicSections: Optional[List[DynamicSection]] = None  # Added dynamicSections

class CompanyResponse(BaseModel):
    id: str
    name: str
    category: str
    size: str
    location: str
    employees: int
    description: str
    logo: str
    website: str
    revenue: int
    profit: int
    assets: int
    liabilities: int
    founded: str
    headquarters: str
    mission: str
    company_values: List[str]
    investors: List[KeyValuePair]
    financialStatement: List[KeyValuePair]
    assessment: List[KeyValuePair]
    portfolio: List[KeyValuePair]
    transformation_plan: List[KeyValuePair]
    dynamicSections: List[DynamicSection]  # Added dynamic sections


# Admin Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}


# @app.post("/admin/companies/add", response_model=dict)
# async def create_company(company: CompanyCreate, admin: str = Depends(authenticate_admin)):
#     company_data = company.dict()
#     result = companies_collection.insert_one(company_data)
#     return {"id": str(result.inserted_id)}

@app.post("/admin/companies/add", response_model=dict)
async def create_company(
    name: str = Form(...),
    category: str = Form(...),
    size: str = Form(...),
    location: str = Form(...),
    #employees: int = Form(...),
    description: str = Form(...),
    website: str = Form(...),
    revenue: int = Form(...),
    #profit: int = Form(...),
    #assets: int = Form(...),
    #liabilities: int = Form(...),
    founded: str = Form(...),
    headquarters: str = Form(...),
    mission: str = Form(...),
    company_values: str = Form(...),
    investors: str = Form(...),
    financialStatement: str = Form(...),
    assessment: str = Form(...),
    portfolio: str = Form(...),
    transformation_plan: str = Form(...),
    dynamicSections: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    request_files: List[UploadFile] = File([]),
    admin: str = Depends(authenticate_admin)
):
    try:
        company_values_list = json.loads(company_values)
        investors_list = json.loads(investors)
        financialStatement_list = json.loads(financialStatement)
        assessment_list = json.loads(assessment)
        portfolio_list = json.loads(portfolio)
        transformation_plan_list = json.loads(transformation_plan)
        dynamicSections_list = json.loads(dynamicSections)

        company_data = {
            "name": name,
            "category": category,
            "size": size,
            "location": location,
            "employees": 0,
            "description": description,
            "website": website,
            "revenue": revenue,
            "profit": 0,
            "assets": 0,
            "liabilities": 0,
            "founded": founded,
            "headquarters": headquarters,
            "mission": mission,
            "company_values": company_values_list,
            "investors": investors_list,
            "financialStatement": financialStatement_list,
            "assessment": assessment_list,
            "portfolio": portfolio_list,
            "transformation_plan": transformation_plan_list,
            "dynamicSections": dynamicSections_list
        }

        UPLOAD_DIR = "uploads"
        ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"]
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        BASE_URL = os.getenv("API_BASE_URL") #get the base url

        if logo:
            if logo.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(status_code=400, detail="Invalid logo file type")
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{logo.filename}")
            with open(file_path, "wb") as buffer:
                buffer.write(await logo.read())

            if BASE_URL:
                file_url = f"{BASE_URL}/files/{file_id}_{logo.filename}"
            else:
                file_url = f"/files/{file_id}_{logo.filename}" #local testing

            company_data["logo"] = file_url

        for file in request_files:
            if file:
                if file.content_type not in ALLOWED_FILE_TYPES:
                    raise HTTPException(status_code=400, detail=f"Invalid file type for {file.filename}")
                file_id = str(uuid.uuid4())
                file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
                with open(file_path, "wb") as buffer:
                    buffer.write(await file.read())

                if BASE_URL:
                    file_url = f"{BASE_URL}/files/{file_id}_{file.filename}"
                else:
                    file_url = f"/files/{file_id}_{file.filename}" #Local testing

                for list_name in ["investors", "financialStatement", "assessment", "portfolio", "transformation_plan"]:
                    list_data = company_data[list_name]
                    if isinstance(list_data, list):
                        for item in list_data:
                            if isinstance(item, dict) and "key" in item and "value" in item and "fileName" in item:
                                if file.filename == item["fileName"]:
                                    item["fileName"] = file_url


                if isinstance(company_data["dynamicSections"], list):
                    for section in company_data["dynamicSections"]:
                        if isinstance(section, dict) and isinstance(section.get("value"), list):
                            for item in section["value"]:
                                if isinstance(item, dict) and "fileName" in item:
                                    if file.filename == item["fileName"]:
                                        item["fileName"] = file_url

        result = companies_collection.insert_one(company_data)
        return {"id": str(result.inserted_id)}

    except Exception as e:
        print(f"Error in create_company: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.put("/admin/companies/{company_id}", response_model=dict)
async def update_company(
    company_id: str,
    name: Optional[str] = None,
    category: Optional[str] = None,
    size: Optional[str] = None,
    location: Optional[str] = None,
    employees: Optional[int] = None,
    description: Optional[str] = None,
    logo: Optional[UploadFile] = File(None),  # Handle file upload here
    website: Optional[str] = None,
    revenue: Optional[int] = None,
    profit: Optional[int] = None,
    assets: Optional[int] = None,
    liabilities: Optional[int] = None,
    founded: Optional[str] = None,
    headquarters: Optional[str] = None,
    mission: Optional[str] = None,
    company_values: Optional[List[str]] = None,
    investors: Optional[List[KeyValuePair]] = None,
    financialStatement: Optional[List[KeyValuePair]] = None,
    assessment: Optional[List[KeyValuePair]] = None,
    portfolio: Optional[List[KeyValuePair]] = None,
    transformation_plan: Optional[List[KeyValuePair]] = None,
    dynamicSections: Optional[List[DynamicSection]] = None,
    admin: str = Depends(authenticate_admin)
):
    ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"]  # Example.
    UPLOAD_DIR = "uploads"
    try:
        try:
            object_id = ObjectId(company_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid company ID format")

        company_data = {}
        if name is not None: company_data["name"] = name
        if category is not None: company_data["category"] = category
        if size is not None: company_data["size"] = size
        if location is not None: company_data["location"] = location
        if employees is not None: company_data["employees"] = employees
        if description is not None: company_data["description"] = description
        if website is not None: company_data["website"] = website
        if revenue is not None: company_data["revenue"] = revenue
        if profit is not None: company_data["profit"] = profit
        if assets is not None: company_data["assets"] = assets
        if liabilities is not None: company_data["liabilities"] = liabilities
        if founded is not None: company_data["founded"] = founded
        if headquarters is not None: company_data["headquarters"] = headquarters
        if mission is not None: company_data["mission"] = mission
        if company_values is not None: company_data["company_values"] = company_values
        if investors is not None: company_data["investors"] = investors
        if financialStatement is not None: company_data["financialStatement"] = financialStatement
        if assessment is not None: company_data["assessment"] = assessment
        if portfolio is not None: company_data["portfolio"] = portfolio
        if transformation_plan is not None: company_data["transformation_plan"] = transformation_plan
        if dynamicSections is not None: company_data["dynamicSections"] = dynamicSections

        if logo:
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)

            if logo.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(status_code=400, detail="Invalid file type")

            try:
                file_id = str(uuid.uuid4())
                file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{logo.filename}")

                with open(file_path, "wb") as buffer:
                    buffer.write(await logo.read())

                BASE_URL = os.getenv("API_BASE_URL")
                file_url = f"{BASE_URL}/files/{file_id}_{logo.filename}"

                company_data["logo"] = file_url  # Store the URL in the database

            except OSError as e:
                raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

        if company_data:
            result = companies_collection.update_one({"_id": object_id}, {"$set": company_data})
            if result.modified_count > 0:
                return {"message": "Company updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="Company not found")
        else:
            raise HTTPException(status_code=400, detail="No update data provided")
    except Exception as e:
        print(f"Error in update_company: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.delete("/admin/companies/{company_id}", response_model=dict)
async def delete_company(company_id: str, admin: str = Depends(authenticate_admin)):
    result = companies_collection.delete_one({"id": company_id})
    if result.deleted_count > 0:
        return {"message": "Company deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Company not found")


@app.get("/admin/companies", response_model=List[CompanyResponse])
async def list_companies(
    admin: str = Depends(authenticate_admin),
    search: str = Query(None),
    category: str = Query(None),
    size: str = Query(None),
    location: str = Query(None),
    limit: int = Query(100),
    skip: int = Query(0),
):
    try:
        query = {}
        if search:
            query["name"] = {"$regex": search, "$options": "i"}
        if category:
            query["category"] = category
        if size:
            query["size"] = size
        if location:
            query["location"] = location

        total_count = companies_collection.count_documents(query)

        companies_data = list(companies_collection.find(query).skip(skip).limit(limit))

        companies = []
        for company_data in companies_data:
            company_data["id"] = str(company_data.pop("_id"))
            companies.append(CompanyResponse(**company_data))

        json_compatible_item_data = jsonable_encoder(companies)  # Encode the data

        headers = {"x-total-count": str(total_count)}

        return JSONResponse(content=json_compatible_item_data, headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/admin/companies/{company_id}")
async def get_company(company_id: str, admin: bool = Depends(authenticate_admin)):
    try:
        company = companies_collection.find_one({"_id": ObjectId(company_id)})
        if company:
            company["_id"] = str(company["_id"])
            # Adjust file URLs
            # for list_name in ["investors", "financialStatement", "assessment", "portfolio", "transformation_plan"]:
            #     if isinstance(company.get(list_name), list):
            #         for item in company[list_name]:
            #             if isinstance(item, dict) and isinstance(item.get("value"), str) and item["value"]:
            #                 if item["value"].startswith("http"): #Check if already an absolute url
            #                     item["value"] = f"{BASE_URL}/files/{item['value']}"
            #                 else:
            #                     item["value"] = f"{item['value']}" #local testing

            # if isinstance(company.get("dynamicSections"), list):
            #     for section in company["dynamicSections"]:
            #         if isinstance(section.get("value"), list):
            #             for item in section["value"]:
            #                 if isinstance(item, dict) and isinstance(item.get("value"), str) and item["value"]:
            #                     if item["value"].startswith("http"):
            #                         item["value"] = f"{BASE_URL}/files/{item['value']}"
            #                     else:
            #                         item["value"] = f"/files/{item['value']}" #local testing

            return company
        else:
            raise HTTPException(status_code=404, detail="Company not found")
    except Exception as e:
        print(f"Error getting company: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

from fastapi import UploadFile, File, APIRouter
import uuid

@app.post("/admin/upload/")
async def upload_file(file: UploadFile = File(...)):
    BASE_URL = os.getenv("API_BASE_URL")
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    file_url = f"{BASE_URL}/files/{file_id}_{file.filename}"

    return {"filename": file.filename, "file_url": file_url, "file_type": file.content_type}


app.mount("/files", StaticFiles(directory="uploads"))

# Sections to be removed
